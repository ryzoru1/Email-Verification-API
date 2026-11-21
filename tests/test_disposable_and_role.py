from app.services.disposable_checker import is_disposable_domain
from app.services.role_checker import is_role_based_email


def test_disposable_domain_detection():
    assert is_disposable_domain("mailinator.com") is True
    assert is_disposable_domain("sub.mailinator.com") is True
    assert is_disposable_domain("example.com") is False


def test_role_based_detection():
    assert is_role_based_email("support@example.com") is True
    assert is_role_based_email("admin@example.com") is True
    assert is_role_based_email("john.doe@example.com") is False
    assert is_role_based_email("info+sales@example.com") is True
