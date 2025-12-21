from fastapi import APIRouter, Depends, Response, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from dtos import UserCreateRequest, UserResponse, TokenResponse, RefreshTokenRequest
from models import UserCreate, User
from auth_service import UserAlreadyExistsException, InvalidRefreshTokenException
from settings import get_settings
from response_helpers import set_no_cache_headers
from dependencies import get_auth_service, get_current_active_user
from rate_limiter import limiter

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register(
    request: Request,
    user: UserCreateRequest,
    response: Response,
    auth_service=Depends(get_auth_service)
):
    set_no_cache_headers(response)
    user_create = UserCreate(email=user.email, username=user.username, password=user.password)
    created_user = await auth_service.register_user(user_create)
    return UserResponse(
        id=created_user.id,
        email=created_user.email,
        username=created_user.username,
        is_active=created_user.is_active
    )


@router.post("/token", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    response: Response,
    settings=Depends(get_settings),
    auth_service=Depends(get_auth_service)
):
    set_no_cache_headers(response)
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        from auth_service import AuthenticationException
        raise AuthenticationException("Incorrect username or password")
    access_token, refresh_token, _ = await auth_service.create_token_pair(user)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60
    )


@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
    response: Response
):
    set_no_cache_headers(response)
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        is_active=current_user.is_active
    )


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("20/minute")
async def refresh_token(
    http_request: Request,
    request: RefreshTokenRequest,
    response: Response,
    settings=Depends(get_settings),
    auth_service=Depends(get_auth_service)
):
    set_no_cache_headers(response)
    new_access_token, new_refresh_token = await auth_service.refresh_access_token(request.refresh_token)
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60
    )


@router.post("/revoke", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_token(
    request: RefreshTokenRequest,
    auth_service=Depends(get_auth_service)
):
    auth_service.revoke_refresh_token(request.refresh_token)
    return
