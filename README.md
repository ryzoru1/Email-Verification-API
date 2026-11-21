# Email Verification API (Python / FastAPI)

A production-ready **Email Verification API** built with Python and FastAPI, designed for direct deployment and distribution on **RapidAPI Hub**.

It validates email addresses using multiple checks to help reduce fake signups, improve deliverability, and clean contact lists.

## Features

- **Single & Bulk Verification** endpoints
- **Syntax validation** and email normalization
- **Domain & MX record checks** (DNS-based)
- **Disposable email domain detection**
- **Role-based address detection** (e.g. `support@`, `info@`)
- **Optional SMTP mailbox check** (best-effort, configurable)
- **Confidence score (0-100)** with detailed check breakdown
- **RapidAPI-ready authentication support** (`X-RapidAPI-Proxy-Secret`)
- **API key support** for private/direct deployments
- **Product website included** (`/`, `/terms`, `/privacy`) so the listing has a real site
- **OpenAPI docs** (`/docs`, `/redoc`, `/openapi.json`) and an importable `openapi.json`
- **Dockerized** for easy deployment
- **Test suite** and documentation included

## Use Cases

- Signup and registration form validation
- Lead list cleaning and enrichment pipelines
- Fraud and abuse prevention
- Marketing email hygiene
- CRM/data quality automation

## Project Structure

```text
.
├── app/
│   ├── api/v1/                 # API versioning, routers, endpoints
│   ├── core/                   # Config, logging, security
│   ├── data/                   # Disposable domains & role prefixes
│   ├── middleware/             # Request timing middleware
│   ├── schemas/                # Pydantic request/response models
│   ├── services/               # Verification logic and orchestration
│   └── utils/                  # Normalization helpers
├── docs/                       # API, deployment, RapidAPI, architecture docs
├── examples/                   # Python and cURL usage examples
├── scripts/                    # Dev/prod run scripts
├── tests/                      # Pytest test suite
├── website/                    # Product site, terms, privacy, assets
├── openapi.json                # OpenAPI 3.0.2 spec for RapidAPI import
├── rapidapi-listing.json       # Listing copy, plans and launch checklist
├── .env.example                # Environment variable template
├── Dockerfile                  # Container build
├── LICENSE                     # MIT license
└── README.md
```

## Quick Start

### 1. Prerequisites
- Python **3.8+** (any version greater than 3.7)
- `pip`
- (Optional) Docker

### 2. Clone and install
```bash
git clone <your-repo-url>
cd email_verfication_api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure environment
```bash
cp .env.example .env
```
Edit `.env` as needed (API keys, SMTP check settings, limits, etc.).

### 4. Run the API
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open:
- Website: `http://localhost:8000/`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Health: `http://localhost:8000/api/v1/health`
- Terms / privacy: `http://localhost:8000/terms` · `http://localhost:8000/privacy`

## API Endpoints

### `GET /`
Serves the product website to browsers. API clients (`Accept: */*`) get service metadata.

### `GET /terms` and `GET /privacy`
Terms of use and privacy policy, ready to link from the RapidAPI listing.

### `GET /api/v1/health`
Returns service status and version.

### `POST /api/v1/verify`
Verifies a single email address.

**Request**
```json
{
  "email": "user@example.com",
  "smtp_check": false
}
```

**Response (example)**
```json
{
  "email": "user@example.com",
  "normalized_email": "user@example.com",
  "status": "valid",
  "score": 85,
  "reason": "Email appears valid based on syntax, DNS, and MX checks.",
  "domain": "example.com",
  "checks": {
    "syntax": true,
    "domain_exists": true,
    "mx_records": true,
    "disposable": false,
    "role_based": false,
    "smtp": null
  },
  "suggestions": []
}
```

### `POST /api/v1/verify/bulk`
Verifies multiple email addresses in one request.

**Request**
```json
{
  "emails": ["user@example.com", "support@example.com", "test@mailinator.com"],
  "smtp_check": false
}
```

**Response includes**
- `total`
- `results[]` (same shape as single verification)
- `summary` (counts and average score)

> Bulk request size is limited by `MAX_BULK_EMAILS` (default: 100).

## Verification Statuses

- `valid` - Email passes core checks and appears deliverable/acceptable
- `invalid` - Syntax/domain/recipient checks indicate the email is not usable
- `risky` - Email is technically plausible but has risk signals (disposable, role-based, no MX, inconclusive SMTP)
- `unknown` - Reserved for inconclusive cases (implementation may return `risky` with explanation in many scenarios)

## Authentication

The API supports multiple modes:

| Header | When required | Purpose |
|---|---|---|
| `X-API-Key` | If `API_KEY` is set | Direct/private API access control |
| `X-RapidAPI-Proxy-Secret` | If `RAPIDAPI_PROXY_SECRET` is set | Restrict access to RapidAPI proxy traffic; injected by RapidAPI, not sent by consumers |
| `X-RapidAPI-Key` | Sent by RapidAPI clients | Identifies RapidAPI requests (not a backend secret) |

If neither `API_KEY` nor `RAPIDAPI_PROXY_SECRET` is configured, auth checks are skipped (useful for local development).

## Configuration

Copy `.env.example` to `.env` and configure as needed:

| Variable | Default | Description |
|---|---|---|
| `APP_NAME` | `Email Verification API` | Service name |
| `APP_VERSION` | `1.0.0` | Service version |
| `APP_ENV` | `development` | Environment label |
| `DEBUG` | `false` | Debug mode flag |
| `LOG_LEVEL` | `INFO` | Logging level |
| `API_KEY` | *(empty)* | Optional direct API key |
| `RAPIDAPI_PROXY_SECRET` | *(empty)* | Optional RapidAPI proxy secret validation |
| `ENABLE_SMTP_CHECK` | `false` | Enable SMTP mailbox probing by default |
| `SMTP_TIMEOUT_SECONDS` | `10` | SMTP timeout (seconds) |
| `DNS_TIMEOUT_SECONDS` | `5` | DNS resolver timeout (seconds) |
| `MAX_BULK_EMAILS` | `100` | Max emails per bulk request |
| `REQUEST_TIMEOUT_SECONDS` | `30` | General request timeout setting |
| `CORS_ALLOW_ORIGINS` | `*` | CORS origins (CSV or `*`) |
| `CORS_ALLOW_METHODS` | `*` | CORS methods (CSV or `*`) |
| `CORS_ALLOW_HEADERS` | `*` | CORS headers (CSV or `*`) |

### SMTP Check Notes
SMTP verification is **best-effort** and may be blocked or rate-limited by mail providers. Many servers return inconclusive responses or reject probing. For production/RapidAPI deployments, it is often best to keep `ENABLE_SMTP_CHECK=false` unless your infrastructure supports reliable outbound SMTP checks.

## RapidAPI Hub Deployment (Selling the API)

This project is designed to be listed on RapidAPI Hub. The product website, terms and privacy
pages are served by the API itself, so the listing's Website and Terms fields can point at the
same HTTPS host as the base URL.

### Recommended setup
1. Deploy the API behind public HTTPS (Docker or any Python hosting platform).
2. Replace the `your-domain.example` and `[Company name]` placeholders in `website/`,
   `openapi.json` and `rapidapi-listing.json`.
3. Set `RAPIDAPI_PROXY_SECRET` in your environment.
4. Configure RapidAPI to forward `X-RapidAPI-Proxy-Secret` to your backend.
5. Expose endpoints:
   - `GET /api/v1/health`
   - `POST /api/v1/verify`
   - `POST /api/v1/verify/bulk`
6. Import [`openapi.json`](openapi.json) into RapidAPI Studio.
7. Create pricing plans/quotas in RapidAPI (example: Basic/Pro/Ultra) and align the website plan table.
8. Set Website `https://your-domain.example/` and Terms `https://your-domain.example/terms`.

See **[docs/RAPIDAPI.md](docs/RAPIDAPI.md)** for the complete launch checklist, proxy-secret
test commands and example plan tiers. Listing copy and plans live in
[`rapidapi-listing.json`](rapidapi-listing.json).

## Docker

### Build
```bash
docker build -t email-verification-api .
```

### Run
```bash
docker run --rm -p 8000:8000 --env-file .env email-verification-api
```

## Running Tests

```bash
pytest -q
```

(Install dev dependencies first if needed: `pip install -r requirements.txt`)

## Examples

- Python client: [`examples/python_client.py`](examples/python_client.py)
- cURL examples: [`examples/curl_examples.sh`](examples/curl_examples.sh)

## Documentation

- [API Reference](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [RapidAPI Hub Guide](docs/RAPIDAPI.md)
- [OpenAPI spec](openapi.json)
- [RapidAPI listing document](rapidapi-listing.json)
- [Architecture Overview](docs/ARCHITECTURE.md)
- [Changelog](CHANGELOG.md)
- [Contributing](CONTRIBUTING.md)

## Limitations

- SMTP deliverability checks are not guaranteed to be accurate for all providers.
- Disposable domain detection relies on a curated static list and may not catch every temporary email service.
- DNS resolution depends on network/resolver availability and timeout settings.

## License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.
