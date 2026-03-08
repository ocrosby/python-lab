from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from fastapi_oauth_example.application.dto.user_dto import (
    EmailVerificationDTO,
    MFASetupResponseDTO,
    MFAVerifyDTO,
    PasswordResetDTO,
    PasswordResetRequestDTO,
    RefreshTokenDTO,
    SessionResponseDTO,
    TokenDTO,
    UserLoginDTO,
    UserRegistrationDTO,
    UserResponseDTO,
)
from fastapi_oauth_example.application.use_cases.email_verification_use_case import (
    SendEmailVerificationUseCase,
    VerifyEmailUseCase,
)
from fastapi_oauth_example.application.use_cases.login_user_use_case import (
    LoginUserUseCase,
)
from fastapi_oauth_example.application.use_cases.logout_use_case import LogoutUseCase
from fastapi_oauth_example.application.use_cases.mfa_use_cases import (
    EnableMFAUseCase,
    SetupMFAUseCase,
)
from fastapi_oauth_example.application.use_cases.password_reset_use_case import (
    RequestPasswordResetUseCase,
    ResetPasswordUseCase,
)
from fastapi_oauth_example.application.use_cases.refresh_token_use_case import (
    RefreshTokenUseCase,
)
from fastapi_oauth_example.application.use_cases.register_user_use_case import (
    RegisterUserUseCase,
)
from fastapi_oauth_example.application.use_cases.session_use_cases import (
    ListSessionsUseCase,
    RevokeSessionUseCase,
)
from fastapi_oauth_example.domain.value_objects.user_id import UserId
from fastapi_oauth_example.infrastructure.di.dependencies import (
    get_current_user,
    get_enable_mfa_use_case,
    get_list_sessions_use_case,
    get_login_user_use_case,
    get_logout_use_case,
    get_refresh_token_use_case,
    get_register_user_use_case,
    get_request_password_reset_use_case,
    get_reset_password_use_case,
    get_revoke_session_use_case,
    get_send_email_verification_use_case,
    get_setup_mfa_use_case,
    get_verify_email_use_case,
    oauth2_scheme,
)

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


@router.post(
    "/register",
    response_model=UserResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email and password",
    responses={
        201: {"description": "User successfully created"},
        400: {"description": "Bad request - validation error"},
    },
)
async def register(
    dto: UserRegistrationDTO,
    use_case: RegisterUserUseCase = Depends(get_register_user_use_case),
):
    try:
        return await use_case.execute(dto)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.post(
    "/login",
    response_model=TokenDTO,
    summary="Login user",
    description="Authenticate with username, password, and optional MFA code",
    responses={
        200: {"description": "Successfully authenticated"},
        401: {"description": "Invalid credentials"},
    },
)
async def login(
    request: Request,
    dto: UserLoginDTO,
    use_case: LoginUserUseCase = Depends(get_login_user_use_case),
):
    try:
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("User-Agent")
        return await use_case.execute(dto, ip_address=ip_address, user_agent=user_agent)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


@router.post("/token", response_model=TokenDTO, deprecated=True)
async def token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    use_case: LoginUserUseCase = Depends(get_login_user_use_case),
):
    try:
        dto = UserLoginDTO(username=form_data.username, password=form_data.password)
        return await use_case.execute(dto)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


@router.get(
    "/me",
    response_model=UserResponseDTO,
    summary="Get current user",
    description="Retrieve the authenticated user's profile information",
    responses={
        200: {"description": "User profile retrieved successfully"},
        401: {"description": "Not authenticated"},
    },
)
async def get_current_user_info(
    current_user: UserResponseDTO = Depends(get_current_user),
):
    return current_user


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout",
    description=(
        "Invalidate the current access token and optionally revoke the refresh token"
    ),
)
async def logout(
    request: Request,
    token: str = Depends(oauth2_scheme),
    current_user: UserResponseDTO = Depends(get_current_user),
    use_case: LogoutUseCase = Depends(get_logout_use_case),
    dto: RefreshTokenDTO | None = Body(default=None),
):
    ip_address = request.client.host if request.client else None
    refresh_token = dto.refresh_token if dto else None
    await use_case.execute(token, current_user.id, refresh_token, ip_address)


@router.post(
    "/refresh",
    response_model=TokenDTO,
    summary="Refresh access token",
    description="Exchange a valid refresh token for a new access token",
    responses={
        200: {"description": "New access token issued"},
        401: {"description": "Invalid or revoked refresh token"},
    },
)
async def refresh(
    dto: RefreshTokenDTO,
    use_case: RefreshTokenUseCase = Depends(get_refresh_token_use_case),
):
    try:
        return await use_case.execute(dto)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


@router.post(
    "/password-reset/request",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Request password reset",
    description="Send a password reset email if the address is registered",
)
async def request_password_reset(
    dto: PasswordResetRequestDTO,
    use_case: RequestPasswordResetUseCase = Depends(
        get_request_password_reset_use_case
    ),
):
    await use_case.execute(dto)


@router.post(
    "/password-reset/confirm",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Confirm password reset",
    description="Set a new password using the token from the reset email",
    responses={
        204: {"description": "Password updated"},
        400: {"description": "Invalid, expired, or already-used token"},
    },
)
async def confirm_password_reset(
    dto: PasswordResetDTO,
    use_case: ResetPasswordUseCase = Depends(get_reset_password_use_case),
):
    try:
        await use_case.execute(dto)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.post(
    "/email/verify",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Verify email address",
    description="Confirm email ownership using the token from the verification email",
    responses={
        204: {"description": "Email verified"},
        400: {"description": "Invalid, expired, or already-used token"},
    },
)
async def verify_email(
    dto: EmailVerificationDTO,
    use_case: VerifyEmailUseCase = Depends(get_verify_email_use_case),
):
    try:
        await use_case.execute(dto)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.post(
    "/email/resend-verification",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Resend verification email",
    description="Send a new verification email to the authenticated user",
    responses={
        204: {"description": "Verification email sent"},
        400: {"description": "User already verified"},
    },
)
async def resend_email_verification(
    current_user: UserResponseDTO = Depends(get_current_user),
    use_case: SendEmailVerificationUseCase = Depends(
        get_send_email_verification_use_case
    ),
):
    try:
        await use_case.execute(UserId(value=current_user.id))
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.post(
    "/mfa/setup",
    response_model=MFASetupResponseDTO,
    summary="Set up MFA",
    description="Generate a TOTP secret and QR code URI for authenticator apps",
)
async def setup_mfa(
    current_user: UserResponseDTO = Depends(get_current_user),
    use_case: SetupMFAUseCase = Depends(get_setup_mfa_use_case),
):
    try:
        return await use_case.execute(UserId(value=current_user.id))
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.post(
    "/mfa/verify",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Enable MFA",
    description="Verify a TOTP code to activate MFA on the account",
    responses={
        204: {"description": "MFA enabled"},
        400: {"description": "Invalid TOTP code or MFA not set up"},
    },
)
async def verify_mfa(
    dto: MFAVerifyDTO,
    current_user: UserResponseDTO = Depends(get_current_user),
    use_case: EnableMFAUseCase = Depends(get_enable_mfa_use_case),
):
    try:
        await use_case.execute(UserId(value=current_user.id), dto)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.get(
    "/sessions",
    response_model=list[SessionResponseDTO],
    summary="List active sessions",
    description="Return all active sessions for the authenticated user",
)
async def list_sessions(
    current_user: UserResponseDTO = Depends(get_current_user),
    use_case: ListSessionsUseCase = Depends(get_list_sessions_use_case),
):
    return await use_case.execute(UserId(value=current_user.id))


@router.delete(
    "/sessions/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke a session",
    description="Terminate a specific session and revoke its refresh token",
    responses={
        204: {"description": "Session revoked"},
        404: {"description": "Session not found"},
    },
)
async def revoke_session(
    session_id: UUID,
    current_user: UserResponseDTO = Depends(get_current_user),
    use_case: RevokeSessionUseCase = Depends(get_revoke_session_use_case),
):
    try:
        await use_case.execute(UserId(value=current_user.id), session_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
