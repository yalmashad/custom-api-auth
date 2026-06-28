# Custom API Authentication Demo

This repository contains:

- A small API service that uses a custom header for authentication
- A standalone Python traffic generator that sends mixed successful and failed requests

## Authentication

The API expects this header:

```text
X-Demo-Authenticated: f5-poc-secret
```

Behavior:

- Correct header value: `200`
- Missing header: `401`
- Wrong header value: `401`

## API Endpoints

Authenticated endpoints:

```text
GET  /api/accounts
GET  /api/orders
GET  /api/profile
POST /api/payments
```

Health endpoint:

```text
GET /health
```

## Run The API

```bash
docker compose up --build
```

The API listens on:

```text
http://localhost:8080
```

## Test The API

Successful request:

```bash
curl -i -H "X-Demo-Authenticated: f5-poc-secret" \
  http://localhost:8080/api/accounts
```

Failed request:

```bash
curl -i http://localhost:8080/api/accounts
```

Failed request with wrong value:

```bash
curl -i -H "X-Demo-Authenticated: wrong-value" \
  http://localhost:8080/api/accounts
```

## Traffic Generator

Run the standalone traffic generator:

```bash
python3 traffic_generator.py \
  --base-url http://localhost:8080 \
  --total-requests 100 \
  --success-rate 0.70 \
  --interval-seconds 0.2
```

Run it against another API endpoint:

```bash
python3 traffic_generator.py \
  --base-url https://<api-hostname> \
  --total-requests 1000 \
  --success-rate 0.70 \
  --interval-seconds 0.5
```

Use `--total-requests 0` to run continuously.
