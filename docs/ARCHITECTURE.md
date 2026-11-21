# Architecture Overview

## Project Structure

- `app/main.py` - FastAPI application factory and app instance
- `app/core/` - Configuration, logging, and security utilities
- `app/api/v1/` - Versioned API router and endpoint modules
- `app/schemas/` - Pydantic request/response models
- `app/services/` - Verification business logic (syntax, DNS/MX, disposable, role-based, SMTP, orchestration)
- `app/utils/` - Shared helpers (normalization/parsing)
- `app/data/` - Static datasets (disposable domains, role prefixes)
- `app/middleware/` - Custom middleware (request timing)
- `tests/` - Automated tests
- `docs/` - API, deployment, and RapidAPI documentation

## Verification Flow

1. **Input normalization** - Trim and normalize email/domain where possible.
2. **Syntax check** - Validate format using `email-validator`.
3. **Disposable/role checks** - Flag known disposable domains and role-based local parts.
4. **DNS/MX checks** - Resolve MX records (with A/AAAA fallback for domain existence).
5. **Optional SMTP check** - Best-effort RCPT verification when enabled and MX hosts exist.
6. **Scoring & status** - Compute confidence score and classify as `valid`, `invalid`, `risky`, or `unknown`.

## Design Notes

- SMTP verification is optional because many providers block or obfuscate RCPT probing.
- Disposable and role-based signals are heuristic/rule-based and can be extended.
- The API supports RapidAPI proxy-secret validation for marketplace deployments.
- Stateless design makes the service easy to containerize and scale horizontally.
