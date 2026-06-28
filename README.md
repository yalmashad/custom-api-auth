# F5 API Discovery Custom Authentication Demo

This project provides a small API service and a standalone Python traffic generator for an F5 API discovery POC. The API uses a deliberately non-standard header authentication scheme so discovery tooling can classify a custom API authentication type.

## Authentication Behavior

The API expects this custom header:

```text
X-Demo-Authenticated: f5-poc-secret
```

Requests with the correct header value return `200`. Requests with the header missing or with the wrong value return `401`.

The header name and value are configurable through environment variables:

```text
AUTH_HEADER_NAME=X-Demo-Authenticated
AUTH_HEADER_VALUE=f5-poc-secret
```

## API Endpoints

All API endpoints require the custom header:

```text
GET  /api/accounts
GET  /api/orders
GET  /api/profile
POST /api/payments
```

The health endpoint does not require authentication:

```text
GET /health
```

## Run The API With Docker Compose

From a fresh EC2 instance with Docker and Docker Compose installed:

```bash
git clone <your-repo-url>
cd api-auth-discovery
docker compose up --build
```

The API listens on port `8080`:

```text
http://<ec2-public-ip>:8080
```

Docker Compose starts only the API service. The traffic generator is intentionally decoupled from Docker so it can run from your laptop or a separate EC2 instance and point to the F5 Distributed Cloud load balancer.

## Manual API Tests

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

## Standalone Traffic Generator

The traffic generator is a separate Python script:

```text
traffic_generator.py
```

It uses only the Python standard library. You can copy or run this single file from your laptop or an EC2 instance.

Common options:

```text
--base-url
--success-rate
--total-requests
--interval-seconds
--timeout
```

`TOTAL_REQUESTS=0` means run continuously. Set it to a positive number for a finite test.

Run against the local API:

```bash
python3 traffic_generator.py \
  --base-url http://localhost:8080 \
  --total-requests 100 \
  --success-rate 0.70 \
  --interval-seconds 0.2
```

Run from your laptop or EC2 against the F5 load balancer:

```bash
python3 traffic_generator.py \
  --base-url https://<f5-load-balancer-hostname> \
  --total-requests 1000 \
  --success-rate 0.70 \
  --interval-seconds 0.5
```

You can also configure it with environment variables:

```text
API_BASE_URL=https://<f5-load-balancer-hostname>
SUCCESS_RATE=0.70
INTERVAL_SECONDS=0.5
TOTAL_REQUESTS=1000
REQUEST_TIMEOUT=5
```

## Run Without Docker

The project uses only the Python standard library.

Start the API:

```bash
python3 -m demo_api.server
```

Generate traffic:

```bash
python3 traffic_generator.py --base-url http://localhost:8080 --success-rate 0.70
```

## Local Validation

Use these steps before pushing to GitHub.

1. Validate the Docker Compose file:

```bash
docker compose config
```

2. Build the API image:

```bash
docker compose build
```

3. Start the API:

```bash
docker compose up --build demo-api
```

4. In another terminal, confirm `200` for valid auth:

```bash
curl -i -H "X-Demo-Authenticated: f5-poc-secret" \
  http://localhost:8080/api/accounts
```

5. Confirm `401` for missing auth:

```bash
curl -i http://localhost:8080/api/accounts
```

6. Confirm `401` for wrong auth:

```bash
curl -i -H "X-Demo-Authenticated: wrong-value" \
  http://localhost:8080/api/accounts
```

7. Run a short standalone traffic-generator check:

```bash
python3 traffic_generator.py \
  --base-url http://localhost:8080 \
  --total-requests 20 \
  --interval-seconds 0
```

## Keeping Codex Projects Under One Folder

Codex uses the folder you open or start the thread from as the workspace.

For new projects, create the folder under your preferred parent directory first:

```bash
mkdir -p /Users/y.elmashad/Documents/Codex
cd /Users/y.elmashad/Documents/Codex
mkdir my-new-project
cd my-new-project
```

Then open that folder in the Codex desktop app. In the app, use the folder/workspace picker or open-folder action and select:

```text
/Users/y.elmashad/Documents/Codex/my-new-project
```

If you start Codex from a terminal, run it after changing into the project directory.
