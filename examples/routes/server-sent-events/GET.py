import asyncio
import traceback
from VSHS import SSEResponse

async def run(self):

	try:
		i = 0
		while True:
			await asyncio.sleep(1)
			i += 1
			await self.send(data={"count": i}, event="event_name")

	except Exception as e:
		print("Connection closed")
		traceback.print_exc()

async def default(url, body, route):
	return SSEResponse( run )