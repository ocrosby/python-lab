from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_oauth_example.infrastructure.persistence.models import AuditLogModel


class AuditLogger:
    async def log_event(
        self,
        session: AsyncSession,
        event_type: str,
        user_id: UUID | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        details: str | None = None,
    ) -> None:
        audit_log = AuditLogModel(
            user_id=user_id,
            event_type=event_type,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details,
            created_at=datetime.utcnow(),
        )
        session.add(audit_log)
        await session.commit()
