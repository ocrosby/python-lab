from fastapi import Request, status
from fastapi.responses import JSONResponse
from auth_service import (
    UserAlreadyExistsException,
    InvalidRefreshTokenException,
    AuthenticationException
)
from service import ItemNotFoundException


async def user_already_exists_handler(
    request: Request,
    exc: UserAlreadyExistsException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(exc)}
    )


async def invalid_refresh_token_handler(
    request: Request,
    exc: InvalidRefreshTokenException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": str(exc)}
    )


async def authentication_exception_handler(
    request: Request,
    exc: AuthenticationException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": str(exc)},
        headers={"WWW-Authenticate": "Bearer"}
    )


async def item_not_found_handler(
    request: Request,
    exc: ItemNotFoundException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)}
    )


def register_exception_handlers(app):
    app.add_exception_handler(UserAlreadyExistsException, user_already_exists_handler)
    app.add_exception_handler(InvalidRefreshTokenException, invalid_refresh_token_handler)
    app.add_exception_handler(AuthenticationException, authentication_exception_handler)
    app.add_exception_handler(ItemNotFoundException, item_not_found_handler)
