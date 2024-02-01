from VSHS import HTTPError

async def default(url, body, route):

	#print( url.query )

	raise HTTPError(504, "ok")
	return {"message": "Hello World"}