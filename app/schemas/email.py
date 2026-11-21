from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class VerificationStatus(str, Enum):
    VALID = "valid"
    INVALID = "invalid"
    RISKY = "risky"
    UNKNOWN = "unknown"


class EmailVerifyRequest(BaseModel):
    email: str = Field(..., description="Email address to verify.", examples=["user@example.com"])
    smtp_check: Optional[bool] = Field(
        default=None,
        description="Override server SMTP check setting for this request.",
    )

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip()


class BulkEmailVerifyRequest(BaseModel):
    emails: List[str] = Field(..., description="List of email addresses to verify.")
    smtp_check: Optional[bool] = Field(
        default=None,
        description="Override server SMTP check setting for this request.",
    )

    @field_validator("emails")
    @classmethod
    def normalize_emails(cls, values: List[str]) -> List[str]:
        return [v.strip() for v in values if v and v.strip()]


class VerificationChecks(BaseModel):
    syntax: bool = Field(..., description="Whether the email syntax is valid.")
    domain_exists: bool = Field(..., description="Whether the domain resolves.")
    mx_records: bool = Field(..., description="Whether MX records were found.")
    disposable: bool = Field(..., description="Whether the domain is a known disposable provider.")
    role_based: bool = Field(..., description="Whether the local part looks role-based.")
    smtp: Optional[bool] = Field(
        default=None,
        description="SMTP mailbox check result when enabled; null if not performed.",
    )


class EmailVerificationResult(BaseModel):
    email: str
    normalized_email: str
    status: VerificationStatus
    score: int = Field(..., ge=0, le=100, description="Deliverability confidence score.")
    reason: str
    domain: Optional[str] = None
    checks: VerificationChecks
    suggestions: List[str] = Field(default_factory=list)


class BulkEmailVerificationResult(BaseModel):
    total: int
    results: List[EmailVerificationResult]
    summary: dict


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    environment: str
