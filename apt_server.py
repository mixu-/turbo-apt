#!/usr/bin/env python3
 
"""Simple HTTP Server for turbo_apt.
This module builds on BaseHTTPServer by implementing the standard GET request.
"""
 
import os
import posixpath
import http.server
import urllib.request, urllib.parse, urllib.error
import cgi
import shutil
import mimetypes
import re
import pprint
from io import BytesIO

import importlib.util
spec = importlib.util.spec_from_file_location("turbo_apt", "C:\\proj\\turbo-apt\\turbo_apt.py")
turbo_apt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(turbo_apt)

__version__ = "0.1"
__all__ = ["SimpleHTTPRequestHandler"]
_g_apt_file = "turbo_apt-development.json"

class SimpleHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    """Simple HTTP request handler with GET commands."""
 
    server_version = "SimpleHTTPWithUpload/" + __version__
 
    def do_GET(self):
        """Serve a GET request."""
        #pprint.pprint(self.__dict__)
        
        if self.path:
            tmp = self.path.rstrip('/')
            params = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(tmp).query))
            pprint.pprint(params)
            if "url" in params:
                apt = turbo_apt.EtuoviApt(params["url"], _g_apt_file)
                for key, value in params.items():
                    setattr(apt, key, value)
                print(apt)
            
        #TODO return success/failure
        f = self.show_hello(params)
        if f:
            shutil.copyfileobj(f, self.wfile)
            f.close()
 
    def show_hello(self, params=None):
        """Print an empty hello page."""

        f = BytesIO()
        f.write(b'<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
        f.write(("<html>\n<title>Nothing here.</title>\n").encode())
        f.write(("<body>\n").encode())
        f.write(b"<h1>Hi!</h1>\n")
        if params:
            f.write(b"We got some parameters:")
            f.write(pprint.pformat(params).encode())
        f.write(b"</body>\n</html>\n")
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        return f     
 
    if not mimetypes.inited:
        mimetypes.init() # try to read system mime.types
    extensions_map = mimetypes.types_map.copy()
    extensions_map.update({
        '': 'application/octet-stream', # Default
        '.py': 'text/plain',
        '.c': 'text/plain',
        '.h': 'text/plain',
        })
 
 
def test(HandlerClass = SimpleHTTPRequestHandler,
         ServerClass = http.server.HTTPServer):
    http.server.test(HandlerClass, ServerClass)
 
if __name__ == '__main__':
    test()