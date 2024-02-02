from VSHS import get_query

async def default(
					url,	  # yarl.URL: the requested URL
					body,	  # any|None: json.loads( body ) or None if empty body.
					route     # Route: cf next section
				):

	return {
		"urlParams" : get_query(url),
		"bodyParams": body,
		"pathParams": route.vars # dict[string, string]
	}