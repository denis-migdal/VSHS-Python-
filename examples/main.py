# Put the bytecode-cache in the same directory to keep the project clean
import os
import sys
sys.pycache_prefix = os.path.dirname( sys.modules['__main__'].__file__ ) + "/__pycache__"

import asyncio
from VSHS import startHTTPServer

asyncio.run( startHTTPServer(hostname="localhost", port=8080, routes="/routes") )