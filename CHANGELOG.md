# Changelog

All notable changes to this project will be documented in this file.

## [1.1.0] - 2026-11-17

### Added
- Bundled product website served at `/`, with terms at `/terms` and privacy at `/privacy`.
- RapidAPI listing document (`rapidapi-listing.json`) and importable OpenAPI 3.0.2 spec.
- Full launch checklist, proxy-secret verification commands and listing copy in `docs/RAPIDAPI.md`.
- Website tests and HTML content negotiation for the root endpoint.

### Changed
- API secret comparisons now use constant-time comparison.
- RapidAPI consumer headers are accepted without being treated as secrets.

## [1.0.0] - 2026-11-16

### Added
- Initial release of Email Verification API.
- Single email verification endpoint (`POST /api/v1/verify`).
- Bulk email verification endpoint (`POST /api/v1/verify/bulk`).
- Syntax validation and normalization.
- DNS and MX record checks.
- Disposable domain detection.
- Role-based address detection.
- Optional SMTP mailbox deliverability check.
- Health and root endpoints.
- API key and RapidAPI proxy secret authentication support.
- Docker support and deployment documentation.
- RapidAPI Hub integration guide.
- Test suite for core checks and API endpoints.
