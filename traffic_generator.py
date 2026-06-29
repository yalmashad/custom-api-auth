import argparse
import base64
import hashlib
import hmac
import itertools
import json
import os
import random
import time
from urllib import error, request


DEFAULT_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8080")
AUTH_HEADER_NAME = os.getenv("AUTH_HEADER_NAME", "X-Demo-Authenticated")
AUTH_HEADER_VALUE = os.getenv("AUTH_HEADER_VALUE", "f5-poc-secret")
JWT_SECRET = os.getenv("JWT_SECRET", "f5-jwt-demo-secret")
JWT_ISSUER = os.getenv("JWT_ISSUER", "custom-api-auth-demo")

CUSTOM_AUTH_REQUESTS = [
    ("custom-header", "GET", "/api/v1/customers?status=active&region=emea", None),
    ("custom-header", "GET", "/api/v1/customers/cust-1001", None),
    ("custom-header", "GET", "/api/v1/customers/cust-1001/orders?limit=10", None),
    ("custom-header", "GET", "/api/v1/orders/ord-7001", None),
    ("custom-header", "GET", "/api/v1/invoices?customerId=cust-1001&status=open", None),
    (
        "custom-header",
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
        "custom-header",
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
        "custom-header",
        "POST",
        "/api/v1/payments",
        {"invoiceId": "inv-3001", "amount": 245.9, "currency": "USD"},
    ),
    ("custom-header", "DELETE", "/api/v1/sessions/sess-abc123", None),
]

JWT_AUTH_REQUESTS = [
    ("jwt", "GET", "/api/v1/reports/sales-summary?period=last-30-days", None),
    ("jwt", "GET", "/api/v1/security/audit-events?severity=high", None),
]

REQUESTS = CUSTOM_AUTH_REQUESTS + JWT_AUTH_REQUESTS
_invalid_header_modes = itertools.cycle(["missing", "wrong"])


def choose_auth_mode(sample, success_rate):
    return "valid" if sample < success_rate else "invalid"


def build_request_headers(auth_scheme, auth_mode):
    headers = {
        "Accept": "application/json",
        "User-Agent": "custom-api-auth-traffic-generator/1.0",
    }

    if auth_scheme == "jwt":
        return _build_jwt_headers(headers, auth_mode)
    return _build_custom_auth_headers(headers, auth_mode)


def _build_custom_auth_headers(headers, auth_mode):
    if auth_mode == "valid":
        headers[AUTH_HEADER_NAME] = AUTH_HEADER_VALUE
        return headers

    invalid_mode = next(_invalid_header_modes)
    if invalid_mode == "wrong":
        headers[AUTH_HEADER_NAME] = f"invalid-{AUTH_HEADER_VALUE}"
    return headers


def _build_jwt_headers(headers, auth_mode):
    if auth_mode == "valid":
        headers["Authorization"] = f"Bearer {create_jwt()}"
        return headers

    invalid_mode = next(_invalid_header_modes)
    if invalid_mode == "wrong":
        headers["Authorization"] = f"Bearer {create_jwt(secret='wrong-secret')}"
    return headers


def send_request(base_url, auth_scheme, method, path, body, auth_mode, timeout):
    headers = build_request_headers(auth_scheme, auth_mode)
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
        "authScheme": auth_scheme,
        "method": method,
        "path": path,
        "status": status,
        "authMode": auth_mode,
        "latencyMs": latency_ms,
    }


def run_traffic(base_url, success_rate, total_requests, interval_seconds, timeout):
    sent = 0
    while total_requests == 0 or sent < total_requests:
        auth_scheme, method, path, body = random.choice(REQUESTS)
        auth_mode = choose_auth_mode(random.random(), success_rate)
        result = send_request(
            base_url,
            auth_scheme,
            method,
            path,
            body,
            auth_mode,
            timeout,
        )
        print(json.dumps(result), flush=True)
        sent += 1
        time.sleep(interval_seconds)


def create_jwt(secret=JWT_SECRET, expires_in_seconds=3600):
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "iss": JWT_ISSUER,
        "sub": "traffic-generator",
        "aud": "custom-api-auth-demo",
        "scope": "reports:read audit:read",
        "iat": int(time.time()),
        "exp": int(time.time()) + expires_in_seconds,
    }
    encoded_header = _base64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    encoded_payload = _base64url_encode(
        json.dumps(payload, separators=(",", ":")).encode("utf-8")
    )
    signing_input = f"{encoded_header}.{encoded_payload}".encode("utf-8")
    signature = _base64url_encode(
        hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    )
    return f"{encoded_header}.{encoded_payload}.{signature}"


def _base64url_encode(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


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
