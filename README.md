## Examples

You can test the examples from the section below, simply by running the server given in the `./examples` directory:

```shell
python3 examples/main.py
```

You can then send HTTP queries to the server with the command `curl`:

```shell
curl -X $HTTP_METHOD -d "$BODY" -w "\n\nStatus code:%{http_code}\n" "$URL"
```

## Usage

To create a new HTTP server, just call the function `startHTTPServer()`:

```python
import asyncio
from VSHS import startHTTPServer, rootDir

# Put the bytecode-cache in the same directory to keep the project clean
import sys
sys.pycache_prefix = rootDir() + "/__pycache__"

asyncio.run( startHTTPServer(hostname="localhost", port=8080, routes="/routes") )
```

### Routes and handlers

The `routes` parameter is a directory containing the differents routes your HTTP server will answer to. In this directory, each subdirectory corresponds to a route, and each files, to a supported HTTP method for this route.

For example, the file `./routes/hello-world/GET.ts` defines how your server will answer to a `GET /hello-world` HTTP query. In order to do so, `GET.py` default exports an asynchronous function whose return value is the answer to the received HTTP query.

```python
async def default(url, body, route):
    return {"message": "Hello World"}
```

```shell
curl -w "\n" -X GET http://localhost:8080/hello-world
```

**Output:**

```
{
    "message": "Hello World"
}
```

### Handler parameters

In fact, the handler function takes 3 parameters:

```python
from VSHS import get_query

async def default(
                    url,      # yarl.URL: the requested URL
                    body,      # any|None: json.loads( body ) or None if empty body.
                    route     # Route: cf next section
                ):

    return {
        "urlParams" : get_query(url),
        "bodyParams": body,
        "pathParams": route.vars # dict[string, string]
    }
```

```shell
curl -w "\n" -X POST -d '{"body": "A"}' http://localhost:8080/params/C?url=B
```

***Output:***

```
{
    "urlParams": {
        "url": "B"
    },
    "bodyParams": {
        "body": "A"
    },
    "pathParams": {
        "route": "C"
    }
}
```

⚠ Some brower might forbid to add body to GET queries.

### Routes variables

The `route` parameter has two components:

- `path` is the route path, e.g. `/params/{name}/GET.ts`. Letters in between braces represents a variable, corresponding to set of letters (except `/`). Hence a single route path can match several URL, e.g.:
  
  - `/params/faa`
  - `/params/fuu`

- `vars` is an object whose keys are the path variables names and whose values their values in the current URL, e.g.:
  
  - `{name: "faa"}`
  - `{name: "fuu"}`

### HTTP Error Code

If an exception is thrown inside an handlers, the server will automatically send an HTTP 500 status code (Internal Server Error).

```python
async def default(url, body, route):
    raise Exception('Oups...')
```

```shell
curl -w "\n\nStatus code: %{http_code}\n" -X GET http://localhost:8080/exception
```

***Output:***

```
Oups...

Status code: 500
```

You can send other HTTP status code, by throwing an instance of `HTTPError`:

```python
from VSHS import HTTPError

async def default(url, body, route):
    raise HTTPError(403, "Forbidden Access")
```

```shell
curl -w "\n\nStatus code: %{http_code}\n" -X GET http://localhost:8080/http-error
```

***Output:***

```
Forbidden Access

Status code: 403
```

💡 If it exists, errors are redirected to the `/errors/{error_code}` route, with `body` containing the error message.

### Mime-type

#### In the response

We infer the mime type from the handler return value :

| Return        | Mime                                              |
| ------------- | ------------------------------------------------- |
| `str`         | `text/plain`                                      |
| `bytes`       | `application/octet-stream`                        |
| `Blob`        | `blob.type`<br/>or<br/>`application/octet-stream` |
| `any`         | `application/json`                                |
| `SSEResponse` | `text/event-stream`                               |

💡 We provide a `Blob` class to mimic JS `Blob` :

```python
blob = Blob(content, type="text/plain")

await blob.text()
await blob.bytes()
```

#### In the query

### Static ressources

You can also provide a directory containing static files 

```python
import asyncio
from VSHS import startHTTPServer, rootDir

# Put the bytecode-cache in the same directory to keep the project clean
import sys
sys.pycache_prefix = rootDir() + "/__pycache__"

asyncio.run( startHTTPServer(hostname="localhost",
                             port=8080,
                             routes="/routes",
                             static="/assets") )
```

```shell
curl -w "\n\nType: %{content_type}\n" -X GET http://localhost:8080/
```

***Output:***

```
<b>Hello world</b>

Type: text/html
```

### Server-Sent Events

If you want to return [Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events), you just have to return an instance of `SSEResponse`:

```python
import asyncio
import traceback
from VSHS import SSEResponse

async def run(self):

    try:
        i = 0
        while True:
            await asyncio.sleep(1)
            i += 1
            await self.send(data={"count": i}, event="event_name")

    except Exception as e:
        print("Connection closed")
        traceback.print_exc()

async def default(url, body, route):
    return SSEResponse( run )
```

The method `send(message: any, event?: str)` sends a new event to the client. Once the client closes the connection, an exception is raised:

```shell
curl -X GET http://localhost:8080/server-sent-events
```

***Output:***

```
event: event_name
data: {"count":0}

event: event_name
data: {"count":1}

event: event_name
data: {"count":2}
```

## Demo Messages.html

We also provide an additionnal demonstration in `./examples/demo/`.

This webpage sends two HTTP queries :

- `GET /demo/website` to receive Server-Sent Events at each modification of `./examples/messages.txt`.
- `POST /demo/website` to append a new line into `./examples/messages.txt` at each submission of the formular.
