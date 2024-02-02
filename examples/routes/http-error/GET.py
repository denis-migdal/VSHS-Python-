from VSHS import HTTPError

async def default(url, body, route):
	raise HTTPError(403, "Forbidden Access")