#!/usr/bin/env python3
"""
Sentinel Canvas Server
Serves the canvas builder UI. All data comes directly from Log Sentinel's API
in the browser — this server only serves the HTML file.
"""

import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler

HOST = 'localhost'
PORT = 8889  # different port from Dashboard-server (8888) so both can run together


class CanvasHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path in ('/', '/index.html'):
            self.serve_canvas()
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not found')

    def serve_canvas(self):
        canvas_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'canvas.html')
        try:
            with open(canvas_path, 'rb') as f:
                content = f.read()
        except FileNotFoundError:
            self.send_response(404)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'canvas.html not found. Make sure it is in the same directory as canvas-server.py.')
            return
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, format, *args):
        pass  # suppress request logs


if __name__ == '__main__':
    server = HTTPServer((HOST, PORT), CanvasHandler)
    print(f"Sentinel Canvas running at http://{HOST}:{PORT}")
    print(f"Make sure Log Sentinel Dashboard is running at http://localhost:8888")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nSentinel Canvas stopped.")
        sys.exit(0)
