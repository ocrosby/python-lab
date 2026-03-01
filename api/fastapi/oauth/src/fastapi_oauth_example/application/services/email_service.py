from abc import ABC, abstractmethod


class EmailService(ABC):
    @abstractmethod
    async def send_verification_email(self, to_email: str, token: str) -> None:
        pass

    @abstractmethod
    async def send_password_reset_email(self, to_email: str, token: str) -> None:
        pass


class ConsoleEmailService(EmailService):
    async def send_verification_email(self, to_email: str, token: str) -> None:
        print("=== Email Verification ===")
        print(f"To: {to_email}")
        print(f"Verification Token: {token}")
        print(f"Link: http://localhost:8000/auth/verify-email?token={token}")
        print("=" * 50)

    async def send_password_reset_email(self, to_email: str, token: str) -> None:
        print("=== Password Reset ===")
        print(f"To: {to_email}")
        print(f"Reset Token: {token}")
        print(f"Link: http://localhost:8000/auth/reset-password?token={token}")
        print("=" * 50)
