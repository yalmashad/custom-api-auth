import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse


AUTH_HEADER_NAME = os.getenv("AUTH_HEADER_NAME", "X-Demo-Authenticated")
AUTH_HEADER_VALUE = os.getenv("AUTH_HEADER_VALUE", "f5-poc-secret")
HOST = os.getenv("API_HOST", "0.0.0.0")
PORT = int(os.getenv("API_PORT", "8080"))


ENDPOINTS = {
    ("GET", "/api/accounts"): {
        "accounts": [
            {"id": "acct-1001", "name": "Acme Corp", "tier": "gold"},
            {"id": "acct-1002", "name": "Globex", "tier": "silver"},
        ]
    },
    ("GET", "/api/orders"): {
        "orders": [
            {"id": "ord-7001", "accountId": "acct-1001", "status": "shipped"},
            {"id": "ord-7002", "accountId": "acct-1002", "status": "pending"},
        ]
    },
    ("GET", "/api/profile"): {
        "profile": {
            "userId": "user-demo-1",
            "displayName": "F5 API Discovery Demo User",
            "role": "operator",
        }
    },
    ("POST", "/api/payments"): {
        "paymentId": "pay-demo-9001",
        "status": "accepted",
    },
}


class DemoApiHandler(BaseHTTPRequestHandler):
    server_version = "F5ApiDiscoveryDemo/1.0"

    def do_GET(self):
        self._handle_api_request()

    def do_POST(self):
        self._handle_api_request()

    def log_message(self, format, *args):
        print(
            json.dumps(
                {
                    "client": self.client_address[0] if hasattr(self, "client_address") else "-",
                    "request": getattr(self, "requestline", ""),
                    "message": format % args,
                }
            )
        )

    def _handle_api_request(self):
        path = urlparse(self.path).path

        if path == "/health":
            self._send_json(200, {"status": "ok"})
            return

        if not self._is_authenticated():
            self._send_json(
                401,
                {
                    "error": "custom authentication failed",
                    "expectedHeader": AUTH_HEADER_NAME,
                },
            )
            return

        payload = ENDPOINTS.get((self.command, path))
        if payload is None:
            self._send_json(404, {"error": "endpoint not found"})
            return

        self._send_json(
            200,
            {
                "endpoint": path,
                "method": self.command,
                "authType": "custom-header",
                "data": payload,
            },
        )

    def _is_authenticated(self):
        return self.headers.get(AUTH_HEADER_NAME) == AUTH_HEADER_VALUE

    def _send_json(self, status, payload):
        response = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)


def run():
    server = ThreadingHTTPServer((HOST, PORT), DemoApiHandler)
    print(
        json.dumps(
            {
                "message": "demo api listening",
                "host": HOST,
                "port": PORT,
                "authHeader": AUTH_HEADER_NAME,
            }
        )
    )
    server.serve_forever()


if __name__ == "__main__":
    run()
