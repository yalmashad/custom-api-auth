import argparse
import itertools
import json
import os
import random
import time
from urllib import error, request


DEFAULT_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8080")
AUTH_HEADER_NAME = os.getenv("AUTH_HEADER_NAME", "X-Demo-Authenticated")
AUTH_HEADER_VALUE = os.getenv("AUTH_HEADER_VALUE", "f5-poc-secret")

REQUESTS = [
    ("GET", "/api/v1/customers?status=active&region=emea", None),
    ("GET", "/api/v1/customers/cust-1001", None),
    ("GET", "/api/v1/customers/cust-1001/orders?limit=10", None),
    ("GET", "/api/v1/orders/ord-7001", None),
    ("GET", "/api/v1/invoices?customerId=cust-1001&status=open", None),
    (
        "POST",
        "/api/v1/orders",
        {
            "customerId": "cust-1001",
            "items": [
                {"sku": "router-100", "quantity": 2},
                {"sku": "support-basic", "quantity": 1},
            ],
        },
    ),
    (
        "PUT",
        "/api/v1/orders/ord-7002",
        {
            "status": "processing",
            "shippingAddress": {
                "line1": "100 Market Street",
                "city": "London",
                "country": "GB",
            },
        },
    ),
    (
        "POST",
        "/api/v1/payments",
        {"invoiceId": "inv-3001", "amount": 245.9, "currency": "USD"},
    ),
    ("DELETE", "/api/v1/sessions/sess-abc123", None),
]

_invalid_header_modes = itertools.cycle(["missing", "wrong"])


def choose_auth_mode(sample, success_rate):
    return "valid" if sample < success_rate else "invalid"


def build_request_headers(auth_mode, secret):
    headers = {
        "Accept": "application/json",
        "User-Agent": "custom-api-auth-traffic-generator/1.0",
    }

    if auth_mode == "valid":
        headers[AUTH_HEADER_NAME] = secret
        return headers

    invalid_mode = next(_invalid_header_modes)
    if invalid_mode == "wrong":
        headers[AUTH_HEADER_NAME] = f"invalid-{secret}"
    return headers


def send_request(base_url, method, path, body, auth_mode, timeout):
    headers = build_request_headers(auth_mode, AUTH_HEADER_VALUE)
    payload = None

    if body is not None:
        payload = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    api_request = request.Request(
        f"{base_url.rstrip('/')}{path}",
        data=payload,
        headers=headers,
        method=method,
    )

    started = time.monotonic()
    try:
        with request.urlopen(api_request, timeout=timeout) as response:
            response.read()
            status = response.status
    except error.HTTPError as exc:
        exc.read()
        status = exc.code
    latency_ms = round((time.monotonic() - started) * 1000, 2)

    return {
        "method": method,
        "path": path,
        "status": status,
        "authMode": auth_mode,
        "latencyMs": latency_ms,
    }


def run_traffic(base_url, success_rate, total_requests, interval_seconds, timeout):
    sent = 0
    while total_requests == 0 or sent < total_requests:
        method, path, body = random.choice(REQUESTS)
        auth_mode = choose_auth_mode(random.random(), success_rate)
        result = send_request(base_url, method, path, body, auth_mode, timeout)
        print(json.dumps(result), flush=True)
        sent += 1
        time.sleep(interval_seconds)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate mixed 2xx and 401 traffic for the custom-auth demo API."
    )
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument(
        "--success-rate",
        type=float,
        default=float(os.getenv("SUCCESS_RATE", "0.70")),
        help="Fraction of requests with the valid custom auth header.",
    )
    parser.add_argument(
        "--total-requests",
        type=int,
        default=int(os.getenv("TOTAL_REQUESTS", "0")),
        help="Number of requests to send. Use 0 to run forever.",
    )
    parser.add_argument(
        "--interval-seconds",
        type=float,
        default=float(os.getenv("INTERVAL_SECONDS", "1")),
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=float(os.getenv("REQUEST_TIMEOUT", "5")),
    )
    return parser.parse_args()


def main():
    args = parse_args()
    if not 0 <= args.success_rate <= 1:
        raise SystemExit("--success-rate must be between 0 and 1")

    run_traffic(
        args.base_url,
        args.success_rate,
        args.total_requests,
        args.interval_seconds,
        args.timeout,
    )


if __name__ == "__main__":
    main()
