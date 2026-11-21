from typing import Optional, Tuple

from email_validator import EmailNotValidError, validate_email


def normalize_email_address(email: str) -> Tuple[str, Optional[str]]:
    """Normalize an email address and return (normalized_email, domain).

    If normalization fails, returns the stripped lowercased input and None domain.
    """
    raw = (email or "").strip()
    if not raw:
        return "", None
    try:
        # check_deliverability=False here; deliverability checks are handled separately.
        result = validate_email(raw, check_deliverability=False)
        normalized = result.normalized.lower()
        domain = result.domain.lower() if result.domain else None
        return normalized, domain
    except EmailNotValidError:
        lowered = raw.lower()
        if "@" in lowered:
            domain = lowered.rsplit("@", 1)[-1] or None
        else:
            domain = None
        return lowered, domain


def extract_local_part(email: str) -> Optional[str]:
    """Extract the local part from an email address."""
    if "@" not in email:
        return None
    return email.rsplit("@", 1)[0]
