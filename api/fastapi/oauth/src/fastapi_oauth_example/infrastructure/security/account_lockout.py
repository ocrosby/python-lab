from datetime import datetime, timedelta

from fastapi_oauth_example.domain.entities.user import User
from fastapi_oauth_example.domain.repositories.user_repository import UserRepository


class AccountLockoutService:
    def __init__(self, max_attempts: int = 5, lockout_duration_minutes: int = 15):
        self.max_attempts = max_attempts
        self.lockout_duration_minutes = lockout_duration_minutes

    async def record_failed_attempt(
        self, user: User, user_repository: UserRepository
    ) -> None:
        user.failed_login_attempts += 1

        if user.failed_login_attempts >= self.max_attempts:
            user.locked_until = datetime.utcnow() + timedelta(
                minutes=self.lockout_duration_minutes
            )

        await user_repository.update(user)

    async def reset_failed_attempts(
        self, user: User, user_repository: UserRepository
    ) -> None:
        user.failed_login_attempts = 0
        user.locked_until = None
        await user_repository.update(user)

    def is_locked(self, user: User) -> bool:
        if user.locked_until is None:
            return False
        return datetime.utcnow() < user.locked_until
