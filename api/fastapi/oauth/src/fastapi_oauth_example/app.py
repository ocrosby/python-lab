from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from fastapi_oauth_example.infrastructure.config.settings import settings
from fastapi_oauth_example.infrastructure.di.dependencies import database
from fastapi_oauth_example.infrastructure.security.rate_limiter import RateLimiter
from fastapi_oauth_example.infrastructure.web.auth_router import router as auth_router
from fastapi_oauth_example.infrastructure.web.middleware import (
    LoggingMiddleware,
    RateLimitMiddleware,
    RequestIDMiddleware,
    SecurityHeadersMiddleware,
    TimingMiddleware,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.create_tables()
    yield


app = FastAPI(
    title="FastAPI OAuth Example",
    description=(
        "A FastAPI example with OAuth2 JWT authentication and secure REST API design"
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json",
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.allowed_hosts,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

app.add_middleware(
    GZipMiddleware,
    minimum_size=settings.gzip_minimum_size,
    compresslevel=settings.gzip_compression_level,
)

rate_limiter = RateLimiter(requests_per_minute=settings.rate_limit_requests_per_minute)
app.add_middleware(RateLimitMiddleware, rate_limiter=rate_limiter)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(TimingMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RequestIDMiddleware)

app.include_router(auth_router)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
