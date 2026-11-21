from collections import Counter

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import get_settings
from app.core.security import verify_api_access
from app.schemas.email import (
    BulkEmailVerificationResult,
    BulkEmailVerifyRequest,
    EmailVerificationResult,
    EmailVerifyRequest,
)
from app.services.verifier import EmailVerifierService

router = APIRouter(tags=["Verification"])


def get_verifier_service() -> EmailVerifierService:
    return EmailVerifierService()


@router.post(
    "/verify",
    response_model=EmailVerificationResult,
    summary="Verify a single email address",
    dependencies=[Depends(verify_api_access)],
)
async def verify_email(
    payload: EmailVerifyRequest,
    verifier: EmailVerifierService = Depends(get_verifier_service),
) -> EmailVerificationResult:
    """Verify a single email address and return status, score, and detailed checks."""
    if not payload.email.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is required.")
    return verifier.verify_email(payload.email, smtp_check=payload.smtp_check)


@router.post(
    "/verify/bulk",
    response_model=BulkEmailVerificationResult,
    summary="Verify multiple email addresses",
    dependencies=[Depends(verify_api_access)],
)
async def verify_emails_bulk(
    payload: BulkEmailVerifyRequest,
    verifier: EmailVerifierService = Depends(get_verifier_service),
) -> BulkEmailVerificationResult:
    """Verify multiple email addresses in one request."""
    settings = get_settings()
    emails = [e for e in payload.emails if e and e.strip()]
    if not emails:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one email is required.")
    if len(emails) > settings.max_bulk_emails:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Too many emails. Maximum allowed per request is {settings.max_bulk_emails}.",
        )

    results = verifier.verify_bulk(emails, smtp_check=payload.smtp_check)
    counts = Counter(result.status.value for result in results)
    summary = {
        "valid": counts.get("valid", 0),
        "invalid": counts.get("invalid", 0),
        "risky": counts.get("risky", 0),
        "unknown": counts.get("unknown", 0),
        "average_score": round(sum(r.score for r in results) / len(results), 2) if results else 0,
    }
    return BulkEmailVerificationResult(total=len(results), results=results, summary=summary)
