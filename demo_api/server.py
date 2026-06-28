import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse


AUTH_HEADER_NAME = os.getenv("AUTH_HEADER_NAME", "X-Demo-Authenticated")
AUTH_HEADER_VALUE = os.getenv("AUTH_HEADER_VALUE", "f5-poc-secret")
HOST = os.getenv("API_HOST", "0.0.0.0")
PORT = int(os.getenv("API_PORT", "8080"))


CUSTOMERS = {
    "cust-1001": {
        "id": "cust-1001",
        "name": "Acme Manufacturing",
        "status": "active",
        "region": "emea",
    },
    "cust-1002": {
        "id": "cust-1002",
        "name": "Globex Logistics",
        "status": "active",
        "region": "amer",
    },
    "cust-1003": {
        "id": "cust-1003",
        "name": "Initech Finance",
        "status": "suspended",
        "region": "apac",
    },
}

ORDERS = {
    "ord-7001": {
        "id": "ord-7001",
        "customerId": "cust-1001",
        "status": "shipped",
        "total": 245.9,
    },
    "ord-7002": {
        "id": "ord-7002",
        "customerId": "cust-1002",
        "status": "processing",
        "total": 89.5,
    },
    "ord-7003": {
        "id": "ord-7003",
        "customerId": "cust-1001",
        "status": "backordered",
        "total": 1299.0,
    },
}

INVOICES = [
    {"id": "inv-3001", "customerId": "cust-1001", "status": "open", "amount": 245.9},
    {"id": "inv-3002", "customerId": "cust-1002", "status": "paid", "amount": 89.5},
    {"id": "inv-3003", "customerId": "cust-1001", "status": "open", "amount": 1299.0},
]


class DemoApiHandler(BaseHTTPRequestHandler):
    server_version = "CustomApiAuthDemo/1.0"

    def do_GET(self):
        self._handle_api_request()

    def do_POST(self):
        self._handle_api_request()

    def do_PUT(self):
        self._handle_api_request()

    def do_DELETE(self):
        self._handle_api_request()

    def log_message(self, format, *args):
        print(
            json.dumps(
                {
                    "client": self.client_address[0] if hasattr(self, "client_address") else "-",
                    "request": getattr(self, "requestline", ""),
                    "message": format % args,
                }
            ),
            flush=True,
        )

    def _handle_api_request(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query = parse_qs(parsed_url.query)

        if path == "/health":
            self._send_json(200, {"status": "ok"})
            return

        if path == "/openapi.json":
            self._send_json(200, self._openapi_document())
            return

        if not path.startswith("/api/v1/"):
            self._send_json(404, {"error": "endpoint not found"})
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

        body = self._read_json_body()
        response = self._route_api_request(self.command, path, query, body)
        self._send_json(response["status"], response["body"])

    def _route_api_request(self, method, path, query, body):
        segments = path.strip("/").split("/")

        if method == "GET" and path == "/api/v1/customers":
            customers = list(CUSTOMERS.values())
            status = _first_query_value(query, "status")
            region = _first_query_value(query, "region")
            if status:
                customers = [customer for customer in customers if customer["status"] == status]
            if region:
                customers = [customer for customer in customers if customer["region"] == region]
            return _ok({"customers": customers, "count": len(customers)})

        if method == "GET" and len(segments) == 4 and segments[:3] == ["api", "v1", "customers"]:
            customer = CUSTOMERS.get(segments[3])
            if customer:
                return _ok({"customer": customer})
            return _not_found("customer not found")

        if (
            method == "GET"
            and len(segments) == 5
            and segments[:3] == ["api", "v1", "customers"]
            and segments[4] == "orders"
        ):
            customer_id = segments[3]
            orders = [
                order for order in ORDERS.values() if order["customerId"] == customer_id
            ]
            return _ok({"customerId": customer_id, "orders": orders, "count": len(orders)})

        if method == "GET" and len(segments) == 4 and segments[:3] == ["api", "v1", "orders"]:
            order = ORDERS.get(segments[3])
            if order:
                return _ok({"order": order})
            return _not_found("order not found")

        if method == "POST" and path == "/api/v1/orders":
            return _created(
                {
                    "order": {
                        "id": "ord-new-9001",
                        "customerId": body.get("customerId", "cust-1001"),
                        "status": "created",
                        "items": body.get("items", []),
                    }
                }
            )

        if method == "PUT" and len(segments) == 4 and segments[:3] == ["api", "v1", "orders"]:
            order_id = segments[3]
            return _ok(
                {
                    "order": {
                        "id": order_id,
                        "status": body.get("status", "processing"),
                        "shippingAddress": body.get("shippingAddress", {}),
                    }
                }
            )

        if method == "GET" and path == "/api/v1/invoices":
            invoices = INVOICES
            customer_id = _first_query_value(query, "customerId")
            status = _first_query_value(query, "status")
            if customer_id:
                invoices = [
                    invoice for invoice in invoices if invoice["customerId"] == customer_id
                ]
            if status:
                invoices = [invoice for invoice in invoices if invoice["status"] == status]
            return _ok({"invoices": invoices, "count": len(invoices)})

        if method == "POST" and path == "/api/v1/payments":
            return _created(
                {
                    "payment": {
                        "id": "pay-9001",
                        "invoiceId": body.get("invoiceId", "inv-3001"),
                        "amount": body.get("amount", 245.9),
                        "status": "authorized",
                    }
                }
            )

        if method == "DELETE" and len(segments) == 4 and segments[:3] == ["api", "v1", "sessions"]:
            return _ok({"sessionId": segments[3], "status": "revoked"})

        return _not_found("endpoint not found")

    def _is_authenticated(self):
        return self.headers.get(AUTH_HEADER_NAME) == AUTH_HEADER_VALUE

    def _read_json_body(self):
        content_length = int(self.headers.get("Content-Length", "0") or "0")
        if content_length == 0:
            return {}

        raw_body = self.rfile.read(content_length)
        try:
            return json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError:
            return {}

    def _send_json(self, status, payload):
        response = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def _openapi_document(self):
        return {
            "openapi": "3.0.3",
            "info": {"title": "Custom API Authentication Demo", "version": "1.0.0"},
            "paths": {
                "/api/v1/customers": {"get": {"summary": "List customers"}},
                "/api/v1/customers/{customerId}": {"get": {"summary": "Get customer"}},
                "/api/v1/customers/{customerId}/orders": {
                    "get": {"summary": "List customer orders"}
                },
                "/api/v1/orders/{orderId}": {
                    "get": {"summary": "Get order"},
                    "put": {"summary": "Update order"},
                },
                "/api/v1/orders": {"post": {"summary": "Create order"}},
                "/api/v1/invoices": {"get": {"summary": "List invoices"}},
                "/api/v1/payments": {"post": {"summary": "Create payment"}},
                "/api/v1/sessions/{sessionId}": {
                    "delete": {"summary": "Revoke session"}
                },
            },
        }


def _first_query_value(query, key):
    values = query.get(key, [])
    return values[0] if values else None


def _ok(body):
    return {"status": 200, "body": body}


def _created(body):
    return {"status": 200, "body": body}


def _not_found(message):
    return {"status": 404, "body": {"error": message}}


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
        ),
        flush=True,
    )
    server.serve_forever()


if __name__ == "__main__":
    run()
