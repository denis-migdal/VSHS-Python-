import asyncio
from VSHS import startHTTPServer, rootDir

# Put the bytecode-cache in the same directory to keep the project clean
import sys
sys.pycache_prefix = rootDir() + "/__pycache__"

asyncio.run( startHTTPServer(hostname="localhost",
							 port=8080,
							 routes="/routes",
							 static="/assets") )