from typing import Optional

from app.data.disposable_domains import DISPOSABLE_DOMAINS


def is_disposable_domain(domain: Optional[str]) -> bool:
    """Return True if the domain is in the disposable domain list."""
    if not domain:
        return False
    domain = domain.lower().strip()
    if domain in DISPOSABLE_DOMAINS:
        return True
    # Check parent domains (e.g. sub.mailinator.com)
    parts = domain.split(".")
    for i in range(1, len(parts) - 1):
        candidate = ".".join(parts[i:])
        if candidate in DISPOSABLE_DOMAINS:
            return True
    return False
