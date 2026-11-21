from app.utils.email_normalizer import extract_local_part, normalize_email_address


def test_normalize_email_address():
    normalized, domain = normalize_email_address("  USER@Example.COM ")
    assert normalized == "user@example.com"
    assert domain == "example.com"


def test_extract_local_part():
    assert extract_local_part("john.doe@example.com") == "john.doe"
    assert extract_local_part("invalid-email") is None
