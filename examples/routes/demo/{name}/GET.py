import json
import asyncio
import traceback

from VSHS import SSEResponse, rootDir

async def default(url, body, route):

	proc = await asyncio.create_subprocess_exec("tail",
												"-F", "-n", "-1", f"{rootDir()}/demo/messages.txt",
												stdout=asyncio.subprocess.PIPE,
												stderr=asyncio.subprocess.PIPE)


	async def run(self):

		try:
			stdout = proc.stdout

			while True:
				data = json.loads( (await stdout.readline()).decode('utf-8') )

				if data['name'] != route.vars['name']:
					continue

				await self.send(data=data, event="message")


		except Exception as e:

			print("Connection closed")
			traceback.print_exc()

			if proc.returncode is None:
				proc.terminate()

	return SSEResponse( run )
