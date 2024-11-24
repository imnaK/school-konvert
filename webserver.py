#!/usr/bin/python

import http.server
import socketserver
import json
from urllib.parse import urlparse, parse_qs

# HTML content
html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Python Web App</title>
</head>
<body>
    <h1 id="message">Hello from Python!</h1>
    <button onclick="updateMessage()">Update Message</button>

    <script>
        function updateMessage() {
            fetch('/update_message')
                .then(response => response.text())
                .then(data => {
                    document.getElementById('message').textContent = data;
                });
        }
    </script>
</body>
</html>
"""

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html_content.encode())
        elif self.path == '/update_message':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Updated message from Python!")
        else:
            self.send_error(404)

PORT = 8000

with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
