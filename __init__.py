import os
import sys
import pathlib
import traceback
from importlib.machinery import SourceFileLoader

import re
import json
import urllib
from yarl import URL
from http import server

from typing import Callable, TypeAlias


import asyncio
from aiohttp import web

def rootDir():
	return os.path.dirname( sys.modules['__main__'].__file__ )

# https://docs.aiohttp.org/en/stable/web_lowlevel.html
async def startHTTPServer(hostname: str = "localhost", port: int = 8080, routes: str = "/routes"):

	if routes[0] == "/": # Absolute path
		routes = rootDir() + routes

	routesHandlers = loadAllRoutesHandlers(routes)
	requestHandler = buildRequestHandler(routesHandlers)

	server = web.Server(requestHandler)
	runner = web.ServerRunner(server)
	await runner.setup()
	site = web.TCPSite(runner, hostname, port)
	await site.start()

	# wait forever ?
	await asyncio.Event().wait()

	# http.server version
	#RequestHandler = buildRequestHandler(routesHandlers)
	#server = HTTPServer( (hostname, port), RequestHandler)
	#server.serve_forever()


class HTTPError(Exception):
	def __init__(self, error_code: int, message: str):
		super().__init__(message)
		self.error_code = error_code



def getAllRoutes(path: str) -> list[str]:
	return [f for f in pathlib.Path(path).rglob('**/*.py')]

Handler: TypeAlias = Callable[[], None ] #(request: HandlerParams) => Promise<any|SSEResponse>;
Routes : TypeAlias = dict[str, Handler]

def loadAllRoutesHandlers(path: str) -> Routes:

	routes = getAllRoutes(path)

	handlers = {}

	for route in routes:

		module_name = 'routes.' + str(route.relative_to(path)).replace('/', '.')[:-3]
		module = SourceFileLoader(module_name, str(route) ).load_module() 

		handlers[str(route.relative_to(path))[:-3]] = module.default

	return handlers


def path2regex(path: str):
	# better to use re.compile()
	path = re.sub("([-[\]{}()*+?.,\\^$|#\s])", r'\\\1', path) # escape REGEX characters.

	path = "^/" + re.sub("\\\{([^\}]+)\\\}", r'(?P<\1>[^/]+)', path) + "$"

	return re.compile(path)


def match(regex, uri):

	result = re.match(regex, uri)

	if result is None:
		return False;

	return result.groupdict()

class Route:

	def __init__(self, handler: Handler, path: str, vars: dict[str,str]):
		self.handler = handler
		self.path = path
		self.vars = vars

	handler: Handler
	path: str
	vars: dict[str, str]

def getRouteHandler(regexes, method, url):

	curRoute = f"{url.path}/{method}"

	for route in regexes:
		vars = match(route[0], curRoute)
		if vars != False:
			return Route(handler=route[1], path=route[2], vars=vars)

	return None

CORS_HEADERS = {
	"Access-Control-Allow-Origin" : "*",
	"Access-Control-Allow-Methods": "POST, GET, PATCH, PUT, OPTIONS, DELETE"
}

class SSEResponse:

	def __init__(self, run):
		self.__run = run

	def _setControler(self, controler):
		self.__controler = controler

	async def run(self):
		await self.__run(self)

	async def send(self, data, event: str = None):
		text = f"data: {json.dumps(data)}\n\n"
		if event is not None:
			text = f"event: {event}\n{text}"

		await self.__controler.write(text.encode('utf-8'))

def buildRequestHandler( routes: Routes):

	regexes = []
	for route in routes:
		regexes.append( (path2regex(route), routes[route], route ) )

	async def handler(request):

		try:

			if request.method == "OPTIONS":
				return web.Response(headers=CORS_HEADERS)

			route = getRouteHandler(regexes, request.method, request.url)
			if route is None:
				raise HTTPError(404, "Not Found")
				
			body = None
			if request.body_exists:
				body = await request.json()

			answer = await route.handler(url=request.url, body=body, route=route);

			if isinstance(answer, SSEResponse):

				# "content-type": "text/event-stream"

				response = web.StreamResponse(headers={"content-type": "text/event-stream", **CORS_HEADERS})
				await response.prepare(request)
				answer._setControler(response)
				await answer.run()
				return response

			return web.Response(text=json.dumps(answer, indent=2),
								content_type="application/json",
								headers=CORS_HEADERS)

		except Exception as e:

			error_code = 500;
			if isinstance(e, HTTPError):
				error_code = e.error_code;
			else:
				traceback.print_exc()

			error_url = URL.build(path=f"/errors/{error_code}", host=request.url.host, port=request.url.port);
			route = getRouteHandler(regexes, "GET", error_url);
			if route is not None:
				try:
					answer = await route.handler(url=request.url, body= e.message, route=route);
					return web.Response(text=answer, content_type="text/plain", headers=CORS_HEADERS );
				except Exception as e:
					console.error(e);

			return web.Response(status=error_code, text=str(e), headers=CORS_HEADERS );

	return handler


# https://stackoverflow.com/questions/67578472/converting-multidict-to-dict-with-duplicate-keys-values-as-a-list
def get_query(url):

	multi_dict = url.query

	new_dict = {}
	for k in set(multi_dict.keys()):
		k_values = multi_dict.getall(k)
		new_dict[k] = k_values if len(k_values) > 1 else k_values[0]

	return new_dict


# http.server version
#def buildRequestHandler( routes: Routes ):
#
#	regexes = []
#	for route in routes:
#		regexes.append( (path2regex(route), routes[route], route ) )
#
#	class RequestHandler(server.BaseHTTPRequestHandler):
#
#		def send_answer(self, code: int, message: str, mime: str = 'text/plain'):
#			
#			self.send_response(code)
#
#			self.send_header("Access-Control-Allow-Origin", "*")
#			self.send_header("Access-Control-Allow-Methods", "POST, GET, PATCH, PUT, OPTIONS, DELETE")
#
#			self.send_header('Content-type', mime + '; charset=utf-8')
#			self.send_header('Content-Length', str(len(message)))
#
#			self.end_headers();
#			self.wfile.write( bytes(message, 'utf-8') )
#
#		def do_query(self):
#
#			try:
#
#				if self.command == "OPTIONS":
#					return self.send_anwser(200, "");
#
#				url = urllib.parse.urlparse(self.path)
#
#				route = getRouteHandler(regexes, self.command, url)
#				if route is None:
#					return self.send_answer(404, "Not found")
#
#				body = None
#
#				if 'Content-Length' in self.headers:
#					body = self.rfile.read(int(self.headers['Content-Length'])).decode('utf-8')
#					body = None if body == "" else json.loads(body)
#
#				answer = route['handler'](url=url, body=body, route=route);
#
#				#if(answer instanceof SSEResponse)
#				#	return new Response(answer._body, {headers: {"content-type": "text/event-stream", ...CORS_HEADERS} } )
#
#				return self.send_answer(200, json.dumps(answer, indent=2), "application/json")
#			except Exception as e:
#
#				print(e, file=sys.stderr)
#
#				error_code = 500;
#				if isinstance(e, HTTPError):
#					error_code = e.error_code;
#
#				return self.send_answer(error_code, str(e) );
#
#		def log_message(self, format, *args):
#			pass
#
#		def do_GET(self):
#			self.do_query();
#
#		def do_POST(self):
#			self.do_query();
#
#		def do_PUT(self):
#			self.do_query();
#
#		def do_PATCH(self):
#			self.do_query();
#
#		def do_DELETE(self):
#			self.do_query();
#
#	return RequestHandler