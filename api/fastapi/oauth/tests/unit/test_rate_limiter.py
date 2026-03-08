"""Unit tests for RateLimiter."""

from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from fastapi_oauth_example.infrastructure.security.rate_limiter import RateLimiter


@pytest.mark.unit
class TestRateLimiter:
    async def test_allows_requests_under_limit(self):
        limiter = RateLimiter(requests_per_minute=5)
        request = MagicMock()
        for _ in range(4):
            await limiter.check_rate_limit(request, "client")

    async def test_raises_429_when_limit_exceeded(self):
        limiter = RateLimiter(requests_per_minute=2)
        request = MagicMock()
        await limiter.check_rate_limit(request, "client")
        await limiter.check_rate_limit(request, "client")
        with pytest.raises(HTTPException) as exc_info:
            await limiter.check_rate_limit(request, "client")
        assert exc_info.value.status_code == 429

    async def test_different_identifiers_tracked_separately(self):
        limiter = RateLimiter(requests_per_minute=1)
        request = MagicMock()
        await limiter.check_rate_limit(request, "ip1")
        await limiter.check_rate_limit(request, "ip2")
