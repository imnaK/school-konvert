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
    <h1 id="result">Result: </h1>
    <input type="number" id="num1" placeholder="Enter number 1">
    <input type="number" id="num2" placeholder="Enter number 2">
    <button onclick="calculate()">Calculate</button>

    <script>
        function calculate() {
            const num1 = document.getElementById('num1').value;
            const num2 = document.getElementById('num2').value;
            const url = encodeURI(`/calculate?num1=${num1}&num2=${num2}`);
            fetch(url)
                .then(response => response.text())
                .then(data => {
                    document.getElementById('result').textContent = 'Result: ' + data;
                });
        }
    </script>
</body>
</html>
"""


class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html_content.encode())
        elif self.path.startswith("/calculate"):
            parsed_url = urlparse(self.path)
            params = parse_qs(parsed_url.query)

            try:
                num1 = int(params["num1"][0])
                num2 = int(params["num2"][0])
                result = num1 + num2

                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(str(result).encode())
            except (KeyError, ValueError):
                self.send_error(400, "Invalid parameters")
        else:
            self.send_error(404)


PORT = 8000

with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
