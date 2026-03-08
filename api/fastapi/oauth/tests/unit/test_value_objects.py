"""Unit tests for domain value objects."""

from uuid import UUID, uuid4

import pytest

from fastapi_oauth_example.domain.value_objects.email import Email
from fastapi_oauth_example.domain.value_objects.user_id import UserId


@pytest.mark.unit
class TestEmail:
    def test_valid_email_created(self):
        email = Email(value="user@example.com")
        assert email.value == "user@example.com"

    def test_str_returns_value(self):
        email = Email(value="hello@test.org")
        assert str(email) == "hello@test.org"

    def test_equality(self):
        assert Email(value="a@b.com") == Email(value="a@b.com")

    def test_inequality(self):
        assert Email(value="a@b.com") != Email(value="c@d.com")

    def test_invalid_email_raises(self):
        with pytest.raises(ValueError):
            Email(value="not-an-email")

    def test_empty_string_raises(self):
        with pytest.raises(ValueError):
            Email(value="")


@pytest.mark.unit
class TestUserId:
    def test_created_with_uuid(self):
        uid = uuid4()
        user_id = UserId(value=uid)
        assert user_id.value == uid

    def test_value_is_uuid_type(self):
        user_id = UserId(value=uuid4())
        assert isinstance(user_id.value, UUID)

    def test_equality(self):
        uid = uuid4()
        assert UserId(value=uid) == UserId(value=uid)

    def test_inequality(self):
        assert UserId(value=uuid4()) != UserId(value=uuid4())

    def test_str_returns_str_of_uuid(self):
        uid = uuid4()
        assert str(UserId(value=uid)) == str(uid)
