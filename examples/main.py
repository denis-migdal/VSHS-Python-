import asyncio
from VSHS import startHTTPServer

asyncio.run( startHTTPServer(hostname="localhost", port=8080, routes="/routes") )