from VSHS import Blob

async def default(url, body, route):

	if body is None:
		return 'null'

	if isinstance(body, Blob):
		return body.type;

	if isinstance(body, str):
		return "String"
	if isinstance(body, bytes):
		return "Uint8Array"
	if isinstance(body, dict):
		return "Object"

	print("?", type(body) )