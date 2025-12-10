import logging
from fastapi import FastAPI, Request

from dtos import ApiInfoResponse
from settings import get_settings
from middleware import RequestLoggingMiddleware
from dependencies import lifespan_context
from exception_handlers import register_exception_handlers
from routers import auth, items, health
from rate_limiter import limiter, RateLimitExceeded, _rate_limit_exceeded_handler

settings = get_settings()

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(
    title="Project1",
    version="1.0.0",
    contact={
        "name": "Omar Crosby",
        "email": "omar.crosby@gmail.com"
    },
    lifespan=lifespan_context
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(RequestLoggingMiddleware)

register_exception_handlers(app)

app.include_router(auth.router)
app.include_router(items.router)
app.include_router(health.router)


@app.get("/", response_model=ApiInfoResponse)
def read_root(request: Request):
    base_url = str(request.base_url).rstrip('/')
    return ApiInfoResponse(
        name="Project1 API",
        version="1.0.0",
        description="RESTful API for managing items",
        links=[
            {"href": f"{base_url}/api/v1/items", "rel": "items", "method": "GET"},
            {"href": f"{base_url}/api/v1/items", "rel": "create-item", "method": "POST"},
            {"href": f"{base_url}/api/v1/auth/register", "rel": "register", "method": "POST"},
            {"href": f"{base_url}/api/v1/auth/token", "rel": "login", "method": "POST"},
            {"href": f"{base_url}/api/v1/auth/me", "rel": "current-user", "method": "GET"},
            {"href": f"{base_url}/health/liveness", "rel": "health-liveness", "method": "GET"},
            {"href": f"{base_url}/health/readiness", "rel": "health-readiness", "method": "GET"},
            {"href": f"{base_url}/health/startup", "rel": "health-startup", "method": "GET"}
        ]
    )
