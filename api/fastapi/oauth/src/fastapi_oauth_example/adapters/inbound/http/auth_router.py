from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from fastapi_oauth_example.application.dto.user_dto import (
    TokenDTO,
    UserRegistrationDTO,
    UserResponseDTO,
)
from fastapi_oauth_example.application.use_cases.login_user_use_case import (
    LoginUserUseCase,
)
from fastapi_oauth_example.application.use_cases.register_user_use_case import (
    RegisterUserUseCase,
)
from fastapi_oauth_example.infrastructure.di.dependencies import (
    get_current_user,
    get_login_user_use_case,
    get_register_user_use_case,
)

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


@router.post(
    "/register",
    response_model=UserResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email and password",
    responses={
        201: {
            "description": "User successfully created",
            "content": {
                "application/json": {
                    "example": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "username": "john_doe",
                        "email": "john@example.com",
                        "is_active": True,
                    }
                }
            },
        },
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
    description="Authenticate user and return JWT access token",
    responses={
        200: {
            "description": "Successfully authenticated",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                    }
                }
            },
        },
        401: {"description": "Invalid credentials"},
    },
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    use_case: LoginUserUseCase = Depends(get_login_user_use_case),
):
    try:
        from fastapi_oauth_example.application.dto.user_dto import UserLoginDTO

        dto = UserLoginDTO(username=form_data.username, password=form_data.password)
        return await use_case.execute(dto)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


@router.post("/token", response_model=TokenDTO, deprecated=True)
async def token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    use_case: LoginUserUseCase = Depends(get_login_user_use_case),
):
    try:
        from fastapi_oauth_example.application.dto.user_dto import UserLoginDTO

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
        200: {
            "description": "User profile retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "username": "john_doe",
                        "email": "john@example.com",
                        "is_active": True,
                    }
                }
            },
        },
        401: {"description": "Not authenticated"},
    },
)
async def get_current_user_info(
    current_user: UserResponseDTO = Depends(get_current_user),
):
    return current_user
