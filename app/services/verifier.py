from __future__ import annotations

from typing import Iterable, List, Optional, Tuple

from app.core.config import get_settings
from app.schemas.email import EmailVerificationResult, VerificationChecks, VerificationStatus
from app.services.disposable_checker import is_disposable_domain
from app.services.dns_checker import check_domain_and_mx
from app.services.role_checker import is_role_based_email
from app.services.smtp_checker import check_smtp_deliverability
from app.services.syntax_checker import check_syntax
from app.utils.email_normalizer import normalize_email_address


class EmailVerifierService:
    """Coordinates all email verification checks and scoring."""

    def __init__(self) -> None:
        self.settings = get_settings()

    def verify_email(self, email: str, smtp_check: Optional[bool] = None) -> EmailVerificationResult:
        raw_email = (email or "").strip()
        syntax = check_syntax(raw_email)

        normalized_email, domain = normalize_email_address(raw_email)
        if syntax.is_valid and syntax.normalized_email:
            normalized_email = syntax.normalized_email
            domain = syntax.domain

        # Defaults for checks
        domain_exists = False
        has_mx = False
        disposable = False
        role_based = False
        smtp_result: Optional[bool] = None
        mx_hosts: List[str] = []

        suggestions: List[str] = []

        if not syntax.is_valid:
            reason = syntax.reason or "Invalid email syntax."
            checks = VerificationChecks(
                syntax=False,
                domain_exists=False,
                mx_records=False,
                disposable=False,
                role_based=False,
                smtp=None,
            )
            return EmailVerificationResult(
                email=raw_email,
                normalized_email=normalized_email,
                status=VerificationStatus.INVALID,
                score=0,
                reason=reason,
                domain=domain,
                checks=checks,
                suggestions=["Check for typos and use a valid email format like name@example.com."],
            )

        disposable = is_disposable_domain(domain)
        role_based = is_role_based_email(normalized_email)

        dns_result = check_domain_and_mx(domain or "", timeout_seconds=self.settings.dns_timeout_seconds)
        domain_exists = dns_result.domain_exists
        has_mx = dns_result.has_mx
        mx_hosts = dns_result.mx_hosts

        perform_smtp = self.settings.enable_smtp_check if smtp_check is None else bool(smtp_check)
        smtp_message = None
        if perform_smtp and has_mx:
            smtp = check_smtp_deliverability(
                recipient_email=normalized_email,
                mx_hosts=mx_hosts,
                timeout_seconds=self.settings.smtp_timeout_seconds,
            )
            smtp_result = smtp.is_deliverable
            smtp_message = smtp.message

        checks = VerificationChecks(
            syntax=True,
            domain_exists=domain_exists,
            mx_records=has_mx,
            disposable=disposable,
            role_based=role_based,
            smtp=smtp_result,
        )

        status, score, reason = self._score_result(
            domain_exists=domain_exists,
            has_mx=has_mx,
            disposable=disposable,
            role_based=role_based,
            smtp_result=smtp_result,
            dns_error=dns_result.error,
            smtp_message=smtp_message,
        )

        if disposable:
            suggestions.append("Avoid disposable email addresses for account creation or transactional messages.")
        if role_based:
            suggestions.append("Role-based addresses may be shared mailboxes; verify recipient intent for outreach.")
        if not has_mx and domain_exists:
            suggestions.append("Domain exists but no MX records were found; delivery may be unreliable.")
        if smtp_result is False:
            suggestions.append("SMTP check indicates the mailbox may not accept mail.")

        return EmailVerificationResult(
            email=raw_email,
            normalized_email=normalized_email,
            status=status,
            score=score,
            reason=reason,
            domain=domain,
            checks=checks,
            suggestions=suggestions,
        )

    def verify_bulk(self, emails: Iterable[str], smtp_check: Optional[bool] = None) -> List[EmailVerificationResult]:
        return [self.verify_email(email, smtp_check=smtp_check) for email in emails]

    @staticmethod
    def _score_result(
        domain_exists: bool,
        has_mx: bool,
        disposable: bool,
        role_based: bool,
        smtp_result: Optional[bool],
        dns_error: Optional[str],
        smtp_message: Optional[str],
    ) -> Tuple[VerificationStatus, int, str]:
        score = 0

        # Syntax already validated at this point.
        score += 30
        if domain_exists:
            score += 20
        if has_mx:
            score += 30
        if smtp_result is True:
            score += 15
        elif smtp_result is None:
            score += 5  # unknown/inconclusive or not performed
        else:
            score -= 20

        if role_based:
            score -= 10
        if disposable:
            score -= 40

        score = max(0, min(100, score))

        # Determine status and reason.
        if disposable:
            return (
                VerificationStatus.RISKY,
                score,
                "Email syntax and domain appear valid, but the domain is a known disposable provider.",
            )

        if not domain_exists:
            reason = "Domain does not exist or could not be resolved."
            if dns_error:
                reason = f"Domain check failed: {dns_error}."
            return (VerificationStatus.INVALID, score, reason)

        if not has_mx:
            reason = "Domain exists but no MX records were found."
            if dns_error:
                reason = f"{reason} ({dns_error})."
            return (VerificationStatus.RISKY, score, reason)

        if smtp_result is False:
            reason = "SMTP mailbox check rejected the recipient."
            if smtp_message:
                reason = smtp_message
            return (VerificationStatus.INVALID, score, reason)

        if smtp_result is True:
            base = "Email appears deliverable based on syntax, DNS, MX, and SMTP checks."
        else:
            base = "Email appears valid based on syntax, DNS, and MX checks."
            if smtp_message:
                base = f"{base} SMTP result inconclusive: {smtp_message}."

        if role_based:
            return (
                VerificationStatus.RISKY,
                score,
                f"{base} The address is role-based and may not belong to an individual.",
            )

        return (VerificationStatus.VALID, score, base)
