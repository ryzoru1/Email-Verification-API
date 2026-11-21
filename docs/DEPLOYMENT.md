# Deployment Guide

## Local Development

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy environment template:
   ```bash
   cp .env.example .env
   ```
4. Run the API:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
5. Open docs at `http://localhost:8000/docs`.

## Docker

Build and run:
```bash
docker build -t email-verification-api .
docker run --rm -p 8000:8000 --env-file .env email-verification-api
```

## Production Notes

- Run behind a reverse proxy (Nginx, Traefik, Caddy, etc.) with a valid public HTTPS certificate.
  RapidAPI requires a public HTTPS base URL.
- The product website is bundled into the image and served at `/`, `/terms` and `/privacy`.
  Replace the `your-domain.example` and `[Company name]` placeholders before publishing.
- Set `DEBUG=false` and appropriate `LOG_LEVEL`.
- Configure `RAPIDAPI_PROXY_SECRET` if deploying behind RapidAPI. Copy the value from
  Studio → Hub Listing → Gateway → Firewall Settings. `/api/v1/*` will then require the
  gateway header, while the website and health check stay public.
- Consider disabling SMTP checks in environments that block outbound SMTP (port 25).
- Tune `DNS_TIMEOUT_SECONDS`, `SMTP_TIMEOUT_SECONDS`, and `MAX_BULK_EMAILS` for your workload.
- Add external rate limiting, monitoring, and alerting for commercial usage.

## Public HTTPS with Caddy

```caddyfile
api.example.com {
    reverse_proxy 127.0.0.1:8000
}
```

Point DNS at the server before starting Caddy; it will obtain and renew the certificate.

## Verify the deployment

```bash
curl -sS https://your-domain.example/api/v1/health
curl -sSI -H 'Accept: text/html' https://your-domain.example/ | head -1
curl -sS https://your-domain.example/terms | head -5
```

See `docs/RAPIDAPI.md` for the full marketplace launch checklist.
