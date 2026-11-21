from app.data.role_prefixes import ROLE_BASED_PREFIXES
from app.utils.email_normalizer import extract_local_part


def is_role_based_email(email: str) -> bool:
    """Return True if the email local part appears to be role-based."""
    local_part = extract_local_part(email)
    if not local_part:
        return False
    normalized = local_part.lower().strip()
    # Remove tag part if present (user+tag@example.com)
    normalized = normalized.split("+", 1)[0]
    return normalized in ROLE_BASED_PREFIXES
