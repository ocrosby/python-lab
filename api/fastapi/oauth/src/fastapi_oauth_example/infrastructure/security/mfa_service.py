import base64
import secrets


class MFAService:
    def generate_secret(self) -> str:
        return base64.b32encode(secrets.token_bytes(20)).decode("utf-8")

    def generate_qr_code(
        self, username: str, secret: str, issuer: str = "FastAPI OAuth"
    ) -> str:
        uri = f"otpauth://totp/{issuer}:{username}?secret={secret}&issuer={issuer}"
        return uri

    def verify_code(self, secret: str, code: str) -> bool:
        import hmac
        import struct
        import time

        key = base64.b32decode(secret, casefold=True)
        counter = int(time.time()) // 30

        for offset in range(-1, 2):
            counter_with_offset = counter + offset
            msg = struct.pack(">Q", counter_with_offset)
            hmac_digest = hmac.new(key, msg, "sha1").digest()
            o = hmac_digest[-1] & 0x0F
            truncated = struct.unpack(">I", hmac_digest[o : o + 4])[0] & 0x7FFFFFFF
            totp_value = truncated % 1000000

            if str(totp_value).zfill(6) == code:
                return True

        return False
