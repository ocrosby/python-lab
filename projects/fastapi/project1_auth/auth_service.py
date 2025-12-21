from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
import secrets
import asyncio
from jose import JWTError, jwt
import bcrypt

from models import UserCreate, UserInDB, TokenData
from repository import UserRepository, RefreshTokenRepository


class AuthenticationException(Exception):
    pass


class UserAlreadyExistsException(Exception):
    pass


class InvalidRefreshTokenException(Exception):
    pass


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        refresh_token_repository: RefreshTokenRepository,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7
    ):
        self._user_repository = user_repository
        self._refresh_token_repository = refresh_token_repository
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._access_token_expire_minutes = access_token_expire_minutes
        self._refresh_token_expire_days = refresh_token_expire_days

    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return await asyncio.to_thread(
            bcrypt.checkpw,
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )

    async def get_password_hash(self, password: str) -> str:
        hashed = await asyncio.to_thread(
            bcrypt.hashpw,
            password.encode('utf-8'),
            bcrypt.gensalt()
        )
        return hashed.decode('utf-8')

    async def authenticate_user(self, username: str, password: str) -> Optional[UserInDB]:
        user = self._user_repository.get_by_username(username)
        if not user:
            return None
        if not await self.verify_password(password, user.hashed_password):
            return None
        return user

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=self._access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self._secret_key, algorithm=self._algorithm)
        return encoded_jwt

    def decode_token(self, token: str) -> TokenData:
        try:
            payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
            username = payload.get("sub")
            if username is None or not isinstance(username, str):
                raise AuthenticationException("Invalid token")
            return TokenData(username=username)
        except JWTError:
            raise AuthenticationException("Invalid token")

    async def register_user(self, user: UserCreate) -> UserInDB:
        existing_user = self._user_repository.get_by_username(user.username)
        if existing_user:
            raise UserAlreadyExistsException(f"Username {user.username} already exists")
        
        existing_email = self._user_repository.get_by_email(user.email)
        if existing_email:
            raise UserAlreadyExistsException(f"Email {user.email} already registered")
        
        hashed_password = await self.get_password_hash(user.password)
        return self._user_repository.create(user, hashed_password)

    def get_user_by_username(self, username: str) -> Optional[UserInDB]:
        return self._user_repository.get_by_username(username)

    async def create_refresh_token(self, user_id: int, token_family: Optional[str] = None) -> str:
        if token_family is None:
            token_family = await asyncio.to_thread(secrets.token_urlsafe, 32)
        
        token = await asyncio.to_thread(secrets.token_urlsafe, 64)
        expires_at = datetime.now(timezone.utc) + timedelta(days=self._refresh_token_expire_days)
        
        self._refresh_token_repository.create(user_id, token, token_family, expires_at)
        return token

    async def create_token_pair(self, user: UserInDB) -> Tuple[str, str, str]:
        access_token = self.create_access_token(data={"sub": user.username})
        token_family = await asyncio.to_thread(secrets.token_urlsafe, 32)
        refresh_token = await self.create_refresh_token(user.id, token_family)
        return access_token, refresh_token, token_family

    async def refresh_access_token(self, refresh_token: str) -> Tuple[str, str]:
        stored_token = self._refresh_token_repository.get_by_token(refresh_token)
        
        if stored_token is None:
            raise InvalidRefreshTokenException("Refresh token not found")
        
        if stored_token.revoked:
            self._refresh_token_repository.revoke_family(stored_token.token_family)
            raise InvalidRefreshTokenException("Refresh token has been revoked (possible token theft detected)")
        
        if stored_token.expires_at < datetime.now(timezone.utc):
            raise InvalidRefreshTokenException("Refresh token has expired")
        
        self._refresh_token_repository.revoke_by_token(refresh_token)
        
        user = self._user_repository.get_by_id(stored_token.user_id)
        if user is None:
            raise AuthenticationException("User not found")
        
        if not user.is_active:
            raise AuthenticationException("User is inactive")
        
        new_access_token = self.create_access_token(data={"sub": user.username})
        new_refresh_token = await self.create_refresh_token(user.id, stored_token.token_family)
        
        return new_access_token, new_refresh_token

    def revoke_refresh_token(self, refresh_token: str) -> bool:
        return self._refresh_token_repository.revoke_by_token(refresh_token)

    def revoke_all_user_tokens(self, user_id: int) -> int:
        return self._refresh_token_repository.revoke_all_for_user(user_id)
