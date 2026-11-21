from dataclasses import dataclass
from typing import Optional

from email_validator import EmailNotValidError, validate_email


@dataclass
class SyntaxCheckResult:
    is_valid: bool
    normalized_email: Optional[str]
    domain: Optional[str]
    reason: Optional[str] = None


def check_syntax(email: str) -> SyntaxCheckResult:
    """Validate email syntax and normalize the address."""
    try:
        result = validate_email(email, check_deliverability=False)
        return SyntaxCheckResult(
            is_valid=True,
            normalized_email=result.normalized.lower(),
            domain=result.domain.lower() if result.domain else None,
        )
    except EmailNotValidError as exc:
        return SyntaxCheckResult(
            is_valid=False,
            normalized_email=None,
            domain=None,
            reason=str(exc),
        )
