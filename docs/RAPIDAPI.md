# RapidAPI Listing & Launch Guide

This API is packaged to be sold on [RapidAPI Hub](https://rapidapi.com/). The backend, the
product website and the terms/privacy pages are served from the same deployment, so the
RapidAPI base URL and the Product Website can point at the same public HTTPS host.

## What ships with the API

| Asset | Path | Purpose |
|---|---|---|
| Listing metadata | `rapidapi-listing.json` | Name, copy, tags, plans, endpoints and launch checklist |
| Hub icon / logo | `website/assets/rapidapi-icon-512.png` | 512x512 square icon for the RapidAPI Hub profile |
| OpenAPI 3.0.2 spec | `openapi.json` | Import into RapidAPI Studio |
| Product website | `website/index.html` | Home page served at `/` to browsers |
| Terms | `website/terms.html` | Served at `/terms`; paste this URL into Hub Listing |
| Privacy | `website/privacy.html` | Served at `/privacy` |
| Website assets | `website/assets/` | CSS, copy script and favicon served at `/assets/*` |
| Health check | `GET /api/v1/health` | RapidAPI health check and uptime monitors |
| Public API docs | `/docs`, `/redoc`, `/openapi.json` | FastAPI-generated docs for direct testing |

The website is served at `/` only when the request asks for HTML. API clients that send
`Accept: */*` (curl, SDKs) still receive the JSON service index.

## Before you publish: replace placeholders

Search the project for `your-domain.example` and `[Company name]` / `[Jurisdiction]`:

```bash
grep -RIn "your-domain.example\|\[Company name\]\|\[Jurisdiction\]" \
  website openapi.json rapidapi-listing.json docs
```

Update:

- `website/index.html` — domain in the cURL sample, contact email, RapidAPI CTA links.
- `website/terms.html` and `website/privacy.html` — company name, jurisdiction, contact email.
- `openapi.json` — `servers[0].url`, contact URL/email, terms URL.
- `rapidapi-listing.json` — website, terms, privacy, base URL, health URL, repo.

Also update the plan limits on the website if they differ from the plans you create in Studio.

## 1. Deploy to a public HTTPS host

RapidAPI needs a publicly reachable HTTPS base URL with a valid certificate. No VPN, no
self-signed certificate, no HTTP-only endpoint.

### Docker

```bash
docker build -t email-verification-api .
docker run -d --name email-api --restart unless-stopped \
  -p 127.0.0.1:8000:8000 --env-file .env email-verification-api
```

### Reverse proxy (Caddy example)

```caddyfile
api.example.com {
    reverse_proxy 127.0.0.1:8000
}
```

Caddy obtains and renews the TLS certificate automatically. Point the domain's DNS at the
server before starting it.

### Verify before touching RapidAPI

```bash
curl -sS https://your-domain.example/api/v1/health
# {"status":"ok","service":"Email Verification API","version":"1.0.0","environment":"production"}

curl -sSI -H 'Accept: text/html' https://your-domain.example/ | head -1
# HTTP/2 200

curl -sS https://your-domain.example/terms | head -5
curl -sS https://your-domain.example/privacy | head -5
```

## 2. Configure the RapidAPI proxy secret

In RapidAPI Studio, open the API → **Hub Listing → Gateway → Firewall Settings** and copy
the `X-RapidAPI-Proxy-Secret` value. Put it in the deployment environment:

```dotenv
RAPIDAPI_PROXY_SECRET=the-value-from-studio
# Keep API_KEY empty for a RapidAPI-only deployment.
API_KEY=
```

Redeploy/restart the service. With the secret set, `/api/v1/*` rejects requests that did not
come through your RapidAPI gateway. `/`, `/terms`, `/privacy` and `/api/v1/health` stay
public so the listing website and health check work.

Test that the gateway header is enforced:

```bash
# Should be 401
curl -sS -o /dev/null -w '%{http_code}\n' https://your-domain.example/api/v1/verify \
  -H 'content-type: application/json' -d '{"email":"user@example.com"}'

# Should be 200 (simulates the RapidAPI gateway)
curl -sS https://your-domain.example/api/v1/verify \
  -H 'content-type: application/json' \
  -H "X-RapidAPI-Proxy-Secret: $RAPIDAPI_PROXY_SECRET" \
  -d '{"email":"user@example.com"}'
```

Never put the proxy secret in consumer-facing documentation. RapidAPI adds it at the
gateway; consumers only use `X-RapidAPI-Key` and `X-RapidAPI-Host`.

## 3. Create the listing

1. Go to [rapidapi.com/provider](https://rapidapi.com/provider) → **Add New API**.
2. Use the copy from `rapidapi-listing.json`:
   - **Name:** Email Verification API
   - **Short description:** Validate email addresses with syntax, DNS/MX, disposable-domain,
     role-based and optional SMTP checks in one fast request.
   - **Category:** Data
   - **Tags:** email, validation, data-quality, fraud-prevention, marketing.
3. Set the **Base URL** to `https://your-domain.example`.
4. Set **Website** to `https://your-domain.example/`.
5. Set **Terms of use** to `https://your-domain.example/terms`.
6. Add the support email from the listing document.
7. Enable **Health check** at `https://your-domain.example/api/v1/health`.
8. Import `openapi.json` from the **Endpoints** tab. If the import tool rejects the file,
   create the four endpoints manually from the same spec.
9. Open each imported endpoint and paste a real sample response. RapidAPI shows these
   examples to consumers, and empty examples look unfinished.
10. Run **Test Endpoint** for `GET /api/v1/health`, `POST /api/v1/verify` and
    `POST /api/v1/verify/bulk`.

## 4. Plans and quotas

Suggested launch configuration (adjust after checking your costs):

| Plan | Price | Requests / month | Rate limit | Bulk max |
|---|---:|---:|---:|---:|
| Basic | Free | 1,000 | 60/min | 10 emails |
| Pro | $19.99 | 25,000 | 300/min | 50 emails |
| Ultra | $79.99 | 250,000 | 1,000/min | 100 emails |

Set `MAX_BULK_EMAILS` on the backend to the largest bulk size you offer. RapidAPI enforces
the plan quotas and billing; the backend does not meter plans.

## 5. Listing copy

**Short description**

> Validate email addresses with syntax, DNS/MX, disposable-domain, role-based and optional
> SMTP checks in one fast request.

**Long description**

> Email Verification API helps you catch bad addresses before they reach your database. Send
> one address or a batch and get a stable status, a 0-100 confidence score, a plain-language
> reason and a detailed check breakdown covering syntax, domain resolution, MX records,
> disposable domains, role-based local parts and optional SMTP probing. Use it for signup
> validation, lead-list cleaning, CRM hygiene and fraud reduction.

**Use cases:** signup form validation, lead-list cleaning, CRM/data-quality automation,
fraud and abuse reduction, marketing list hygiene.

**Status definitions:** `valid`, `invalid`, `risky`, `unknown`. Explain that SMTP is
best-effort and `score` is a signal, not a guarantee.

## 6. Consumer example for the listing

```bash
curl --request POST \
  --url "https://email-verification-api.p.rapidapi.com/api/v1/verify" \
  --header "content-type: application/json" \
  --header "X-RapidAPI-Key: $RAPIDAPI_KEY" \
  --header "X-RapidAPI-Host: email-verification-api.p.rapidapi.com" \
  --data '{"email":"user@example.com"}'
```

Use the host shown in your own RapidAPI dashboard.

## 7. Pre-publish checklist

- [ ] HTTPS certificate valid and no redirect from HTTPS to HTTP.
- [ ] `GET /api/v1/health` returns 200 without a proxy secret.
- [ ] `/`, `/terms` and `/privacy` render correctly in a browser and on mobile.
- [ ] Placeholders replaced in the website, terms, privacy, OpenAPI and listing document.
- [ ] `RAPIDAPI_PROXY_SECRET` set; unauthenticated `/api/v1/verify` returns 401.
- [ ] Authorized request returns 200 and a complete response.
- [ ] OpenAPI import produced the expected endpoints and parameters.
- [ ] Every endpoint has a real sample response in Studio.
- [ ] Plans and website plan limits match.
- [ ] Website, terms and support contact are set in Hub Listing.
- [ ] RapidAPI Test Endpoint passes for the health check and both verify endpoints.
- [ ] A clean client with a real consumer key succeeds after publishing.

## 8. Common rejection or review problems

- Base URL is HTTP, self-signed, VPN-only or returns a 5xx.
- Health check points at `/` and gets HTML or JSON that the checker does not expect.
- The listing has no website, terms or support contact.
- Endpoints have no descriptions, parameters or sample responses.
- The API claims guaranteed deliverability when SMTP is best-effort.
- Bulk endpoint limits are lower than the listing promises.
- The proxy secret is published in consumer docs.

## 9. Operations

- Keep SMTP off by default (`ENABLE_SMTP_CHECK=false`) unless your network supports
  reliable outbound port 25.
- Keep the disposable-domain list current.
- Monitor DNS resolver health, latency and 401/429 rates.
- Add external rate limiting or WAF rules for extra protection if needed.
- Review `docs/DEPLOYMENT.md` for the general deployment notes.
