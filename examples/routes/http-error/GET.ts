import {HTTPError} from "VSHS";

export default async function() {
	throw new HTTPError(403, "Forbidden Access");
}