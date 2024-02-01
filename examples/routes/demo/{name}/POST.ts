import { HTTPError, HandlerParams } from "VSHS";

export default async function(request: HandlerParams) {

	const name = request.route.vars.name;

	if( name === "foo" )
		throw new HTTPError(400, "Parameter name can't be equal to \"foo\".");

	const message = request.body.message;

	const timestamp = new Date().toISOString();

	await Deno.writeTextFile("./demo/messages.txt", JSON.stringify({timestamp, name, message}) + "\n", {append: true});

	return {
		answer: "OK",
		request
	};
}