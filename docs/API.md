# API Reference

Base URL (local): `http://localhost:8000`

## Authentication

Depending on deployment configuration:

- `X-API-Key`: Required when `API_KEY` is set in environment variables.
- `X-RapidAPI-Proxy-Secret`: Required when `RAPIDAPI_PROXY_SECRET` is set (recommended for RapidAPI proxy deployments). RapidAPI injects this at the gateway; consumers never send it themselves.
- `X-RapidAPI-Key`: Sent by RapidAPI clients; accepted as traffic context but not treated as a secret by this API.
- `X-RapidAPI-Host`: Also sent by RapidAPI clients; accepted but not validated.

## Endpoints

### `GET /`
Returns the product website when the request asks for HTML (`Accept: text/html`).
API clients receive service metadata and useful links.

### `GET /terms`
Terms of use page (HTML).

### `GET /privacy`
Privacy policy page (HTML).

### `GET /api/v1/health`
Health check endpoint.

**Response**
```json
{
  "status": "ok",
  "service": "Email Verification API",
  "version": "1.0.0",
  "environment": "development"
}
```

### `GET /api/v1/ping`
Simple liveness endpoint.

### `POST /api/v1/verify`
Verifies a single email address.

**Request body**
```json
{
  "email": "user@example.com",
  "smtp_check": false
}
```

- `email` (string, required): Email address to verify.
- `smtp_check` (boolean, optional): Overrides server default `ENABLE_SMTP_CHECK`.

**Response fields**
- `email`: Original input
- `normalized_email`: Normalized form
- `status`: `valid | invalid | risky | unknown`
- `score`: 0-100 confidence score
- `reason`: Human-readable explanation
- `domain`: Extracted domain
- `checks`: Detailed check booleans/results
  - `syntax`, `domain_exists`, `mx_records`, `disposable`, `role_based`, `smtp`
- `suggestions`: Actionable hints

### `POST /api/v1/verify/bulk`
Verifies multiple email addresses in one request.

**Request body**
```json
{
  "emails": ["user@example.com", "test@mailinator.com"],
  "smtp_check": false
}
```

**Limits**
- Maximum emails per request controlled by `MAX_BULK_EMAILS` (default 100).

**Response**
- `total`: Number of processed emails
- `results`: Array of single verification results
- `summary`: Aggregate counts and average score

## Error Responses

Errors follow FastAPI's default format:

```json
{
  "detail": "Error message"
}
```

Common cases:
- `400 Bad Request`: Empty input or bulk limit exceeded
- `401 Unauthorized`: Missing/invalid API key or RapidAPI proxy secret
- `422 Unprocessable Entity`: Invalid request schema
