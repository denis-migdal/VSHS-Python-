from VSHS import HTTPError, rootDir

import json
import aiofiles
from datetime import datetime

async def default(url, body, route):

	name = route.vars["name"];
	if name == "foo":
		raise HTTPError(400, "Parameter name can't be equal to \"foo\".");

	async with aiofiles.open(f"{rootDir()}/demo/messages.txt", mode='a') as f:
		await f.write( json.dumps({
						"timestamp": datetime.now().isoformat(),
						"name": name,
						"message": body["message"]
					}) + "\n" )

	return {
		"answer": "OK",
		"request": {
			"url" : str(url),
			"body": body,
			"route": {
				"path": route.path,
				"vars": route.vars
			}
		}
	}