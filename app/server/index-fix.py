#!/usr/bin/env python

from __future__ import print_function
import os
import sys
import subprocess
import argparse

if sys.version_info[0] == 2:
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
    from BaseHTTPServer import test as _test
    from SocketServer import ThreadingMixIn
else:
    from http.server import BaseHTTPRequestHandler, HTTPServer, test as _test
    from socketserver import ThreadingMixIn


parser = argparse.ArgumentParser(description=('Simple Threaded HTTP server '
                                              'to run linux-dash.'))
parser.add_argument('--port', metavar='PORT', type=int, nargs='?', default=80,
                    help='Port to run the server on.')

modulesSubPath = '/server/linux_json_api.sh'
appRootPath = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass


class MainHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            data = ''
            contentType = 'text/html'
            if self.path.startswith("/server/"):
                module = self.path.split('=')[1]
                output = subprocess.Popen(
                    appRootPath + modulesSubPath + " " + module,
                    shell=True,
                    stdout=subprocess.PIPE)
                data = output.communicate()[0]
            else:
                if self.path == '/':
                    self.path = 'index.html'
                f = open(appRootPath + os.sep + self.path, 'rb')
                data = f.read()
                if self.path.startswith('/linuxDash.min.css'):
                    contentType = 'text/css'
                f.close()
            self.send_response(200)
            self.send_header('Content-type', contentType)
            self.end_headers()
            self.wfile.write((data if type(data) == bytes else data.encode('utf-8')))

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)


if __name__ == '__main__':
    args = parser.parse_args()
    server = ThreadedHTTPServer(('0.0.0.0', args.port), MainHandler)
    print('Starting server, use <Ctrl-C> to stop')
    server.serve_forever()
