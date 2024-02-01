import { HandlerParams } from "VSHS";

export default async function(
		{
			url,	  // URL: the requested URL
			// ( cf https://developer.mozilla.org/en-US/docs/Web/API/URL )
			body,	  // any|null: JSON.parse( query.body ) or null if no body.
			route: {  // cf next section
				vars  // Record<string, string>
			}
		}: HandlerParams			
	) {

	return {
		urlParams : Object.fromEntries(url.searchParams.entries()),
		bodyParams: body,
		pathParams: vars
	};
}