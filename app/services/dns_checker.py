from dataclasses import dataclass
from typing import List, Optional

import dns.exception
import dns.resolver


@dataclass
class DNSCheckResult:
    domain_exists: bool
    has_mx: bool
    mx_hosts: List[str]
    error: Optional[str] = None


def check_domain_and_mx(domain: str, timeout_seconds: int = 5) -> DNSCheckResult:
    """Check whether a domain exists and has MX records.

    Strategy:
    - Try resolving MX records first.
    - If MX lookup fails with NoAnswer/NXDOMAIN, fall back to A/AAAA to determine existence.
    """
    if not domain:
        return DNSCheckResult(domain_exists=False, has_mx=False, mx_hosts=[], error="Missing domain")

    resolver = dns.resolver.Resolver(configure=True)
    resolver.lifetime = timeout_seconds
    resolver.timeout = timeout_seconds

    mx_hosts: List[str] = []
    mx_error: Optional[str] = None

    try:
        answers = resolver.resolve(domain, "MX")
        for rdata in answers:
            host = str(rdata.exchange).rstrip(".").lower()
            if host:
                mx_hosts.append(host)
        if mx_hosts:
            return DNSCheckResult(domain_exists=True, has_mx=True, mx_hosts=mx_hosts)
    except dns.resolver.NXDOMAIN:
        return DNSCheckResult(domain_exists=False, has_mx=False, mx_hosts=[], error="Domain does not exist")
    except dns.resolver.NoAnswer:
        mx_error = "No MX records"
    except dns.resolver.NoNameservers:
        mx_error = "No nameservers available"
    except dns.exception.Timeout:
        mx_error = "DNS lookup timed out"
    except Exception as exc:  # noqa: BLE001
        mx_error = f"MX lookup failed: {exc}"

    # Fallback: domain may exist without MX (some setups accept mail via A record).
    domain_exists = False
    try:
        resolver.resolve(domain, "A")
        domain_exists = True
    except Exception:  # noqa: BLE001
        try:
            resolver.resolve(domain, "AAAA")
            domain_exists = True
        except Exception:  # noqa: BLE001
            domain_exists = False

    return DNSCheckResult(
        domain_exists=domain_exists,
        has_mx=False,
        mx_hosts=[],
        error=mx_error if not domain_exists else mx_error,
    )
