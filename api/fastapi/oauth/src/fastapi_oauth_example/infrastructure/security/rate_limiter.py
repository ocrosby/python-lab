from datetime import datetime, timedelta

from fastapi import HTTPException, Request, status


class RateLimiter:
    def __init__(self, requests_per_minute: int = 5):
        self.requests_per_minute = requests_per_minute
        self.requests: dict[str, list[datetime]] = {}

    async def check_rate_limit(self, request: Request, identifier: str) -> None:
        now = datetime.utcnow()
        cutoff = now - timedelta(minutes=1)

        if identifier not in self.requests:
            self.requests[identifier] = []

        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier] if req_time > cutoff
        ]

        if len(self.requests[identifier]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later.",
            )

        self.requests[identifier].append(now)
