
export class SSEResponse {

	#controller?: ReadableStreamDefaultController;

	#stream = new ReadableStream({

		start: (controller: any) => {
			this.#controller = controller;
		},
		cancel: () => {
			this.onConnectionClosed?.();
		}
	});

	onConnectionClosed: null| (() => Promise<void>|void) = null;

	constructor(run: (self: SSEResponse) => Promise<void>) {
		run(this);
	}

	get _body() {
		return this.#stream;
	}

	send(data: any, event?: string) {

		let text = `data: ${JSON.stringify(data)}\n\n`;
		if( event !== undefined)
			text = `event: ${event}\n${text}`

		this.#controller?.enqueue( new TextEncoder().encode( text ) );
	}
}

function buildRequestHandler(routes: Routes) {

	return async function(request: Request): Promise<Response> {

		try {

			if(answer instanceof SSEResponse)
				return new Response(answer._body, {headers: {"content-type": "text/event-stream", ...CORS_HEADERS} } )

		} catch(e) {}
	};
}