from VSHS import SSEResponse

async def run(self):
	#for await (let chunk of process.stdout.pipeThrough( new TextDecoderStream() ) ) {
			
	#		let data = JSON.parse(chunk);

	#		if(data.name !== route.vars.name)
	#			continue;

	#		self.send(data, "message");
	#	}
	pass

async def default(url, body, route):

	# not optimized
	#const process = new Deno.Command("tail", {
	#		args: ["-F", "-n", "-1", "./demo/messages.txt"],
	#		stdout: "piped",
	#		stderr: "piped",
	#	}).spawn();

	return SSEResponse( run )
