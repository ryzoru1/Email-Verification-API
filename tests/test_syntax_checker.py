from app.services.syntax_checker import check_syntax


def test_valid_email_syntax():
    result = check_syntax("User.Name+tag@Example.com")
    assert result.is_valid is True
    assert result.normalized_email == "User.Name+tag@example.com" or result.normalized_email.endswith("@example.com")
    assert result.domain == "example.com"


def test_invalid_email_syntax():
    result = check_syntax("not-an-email")
    assert result.is_valid is False
    assert result.reason
