"""Unit tests for MFAService."""

import base64

import pytest

from fastapi_oauth_example.infrastructure.security.mfa_service import MFAService


@pytest.fixture
def svc():
    return MFAService()


@pytest.mark.unit
class TestMFAService:
    def test_generate_secret_returns_string(self, svc):
        secret = svc.generate_secret()
        assert isinstance(secret, str)

    def test_generate_secret_is_valid_base32(self, svc):
        secret = svc.generate_secret()
        # Should decode without error
        base64.b32decode(secret, casefold=True)

    def test_generate_secret_length(self, svc):
        secret = svc.generate_secret()
        # 20 bytes base32-encoded = 32 chars
        assert len(secret) == 32

    def test_generate_qr_code_contains_otpauth(self, svc):
        uri = svc.generate_qr_code("alice", "JBSWY3DPEHPK3PXP")
        assert uri.startswith("otpauth://totp/")

    def test_generate_qr_code_contains_username(self, svc):
        uri = svc.generate_qr_code("alice", "JBSWY3DPEHPK3PXP")
        assert "alice" in uri

    def test_generate_qr_code_contains_secret(self, svc):
        secret = "JBSWY3DPEHPK3PXP"
        uri = svc.generate_qr_code("alice", secret)
        assert secret in uri

    def test_verify_code_wrong_code_returns_false(self, svc):
        secret = svc.generate_secret()
        assert svc.verify_code(secret, "000000") is False

    def test_verify_code_bad_format_returns_false(self, svc):
        secret = svc.generate_secret()
        assert svc.verify_code(secret, "abc") is False

    def test_verify_code_correct_code_returns_true(self, svc):
        import hmac
        import struct
        import time

        secret = svc.generate_secret()
        key = base64.b32decode(secret, casefold=True)
        counter = int(time.time()) // 30
        msg = struct.pack(">Q", counter)
        hmac_digest = hmac.new(key, msg, "sha1").digest()
        o = hmac_digest[-1] & 0x0F
        truncated = struct.unpack(">I", hmac_digest[o : o + 4])[0] & 0x7FFFFFFF
        code = str(truncated % 1000000).zfill(6)
        assert svc.verify_code(secret, code) is True
