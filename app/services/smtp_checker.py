import smtplib
import socket
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class SMTPCheckResult:
    performed: bool
    is_deliverable: Optional[bool]
    message: str


def check_smtp_deliverability(
    recipient_email: str,
    mx_hosts: List[str],
    timeout_seconds: int = 10,
    sender_email: str = "verify@example.com",
) -> SMTPCheckResult:
    """Best-effort SMTP mailbox verification.

    Notes:
    - Many providers block or fake SMTP RCPT checks; results may be inconclusive.
    - This function treats explicit 5xx recipient rejections as undeliverable.
    - Timeouts/connection issues return unknown (None).
    """
    if not mx_hosts:
        return SMTPCheckResult(performed=False, is_deliverable=None, message="No MX hosts available")

    last_message = "SMTP check did not complete"
    for host in mx_hosts:
        try:
            with smtplib.SMTP(host=host, port=25, timeout=timeout_seconds) as server:
                server.ehlo_or_helo_if_needed()
                try:
                    server.starttls()
                    server.ehlo()
                except (smtplib.SMTPException, RuntimeError, ValueError):
                    # STARTTLS not supported or failed; continue without it.
                    pass

                # Use a neutral sender; some servers require a valid domain.
                mail_code, _ = server.mail(sender_email)
                if mail_code >= 500:
                    return SMTPCheckResult(
                        performed=True,
                        is_deliverable=None,
                        message=f"MAIL FROM rejected by {host} (code {mail_code})",
                    )

                rcpt_code, rcpt_msg = server.rcpt(recipient_email)
                if 200 <= rcpt_code < 300:
                    return SMTPCheckResult(
                        performed=True,
                        is_deliverable=True,
                        message=f"Recipient accepted by {host}",
                    )
                if 500 <= rcpt_code < 600:
                    msg = rcpt_msg.decode(errors="ignore") if isinstance(rcpt_msg, bytes) else str(rcpt_msg)
                    return SMTPCheckResult(
                        performed=True,
                        is_deliverable=False,
                        message=f"Recipient rejected by {host} (code {rcpt_code}): {msg}".strip(),
                    )
                # 4xx or other responses are inconclusive.
                msg = rcpt_msg.decode(errors="ignore") if isinstance(rcpt_msg, bytes) else str(rcpt_msg)
                last_message = f"Inconclusive SMTP response from {host} (code {rcpt_code}): {msg}".strip()
        except (socket.timeout, TimeoutError):
            last_message = f"SMTP connection to {host} timed out"
            continue
        except (smtplib.SMTPException, OSError) as exc:
            last_message = f"SMTP check failed on {host}: {exc}"
            continue
        except Exception as exc:  # noqa: BLE001
            last_message = f"Unexpected SMTP error on {host}: {exc}"
            continue

    return SMTPCheckResult(performed=True, is_deliverable=None, message=last_message)
