from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse


class RequestTokenHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the URL and get the request token
        query_components = parse_qs(urlparse(self.path).query)
        if "request_token" in query_components:
            # Store the request token
            self.server.request_token = query_components["request_token"][0]

            # Send success response
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"Login successful! You can close this window.")

            # Stop the server
            self.server.stop = True

    def log_message(self, format, *args):
        # Suppress log messages
        pass


def setup_auth_server():
    # Set up the local server
    server = HTTPServer(("localhost", 8000), RequestTokenHandler)
    server.request_token = None
    server.stop = False
    return server
