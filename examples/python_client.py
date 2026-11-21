"""Example Python client for the Email Verification API."""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import httpx


BASE_URL = os.getenv("EMAIL_VERIFY_API_BASE_URL", "http://localhost:8000")
API_KEY = os.getenv("EMAIL_VERIFY_API_KEY", "")


def _headers() -> Dict[str, str]:
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["X-API-Key"] = API_KEY
    return headers


def verify_email(email: str, smtp_check: Optional[bool] = None) -> Dict[str, Any]:
    payload: Dict[str, Any] = {"email": email}
    if smtp_check is not None:
        payload["smtp_check"] = smtp_check

    with httpx.Client(timeout=30.0) as client:
        response = client.post(f"{BASE_URL}/api/v1/verify", json=payload, headers=_headers())
        response.raise_for_status()
        return response.json()


def verify_bulk(emails: List[str], smtp_check: Optional[bool] = None) -> Dict[str, Any]:
    payload: Dict[str, Any] = {"emails": emails}
    if smtp_check is not None:
        payload["smtp_check"] = smtp_check

    with httpx.Client(timeout=30.0) as client:
        response = client.post(f"{BASE_URL}/api/v1/verify/bulk", json=payload, headers=_headers())
        response.raise_for_status()
        return response.json()


if __name__ == "__main__":
    print(verify_email("user@example.com"))
    print(verify_bulk(["user@example.com", "support@example.com", "test@mailinator.com"]))
