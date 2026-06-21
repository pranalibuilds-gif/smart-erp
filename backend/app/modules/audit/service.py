import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .models import AuditLog


class AuditService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def log_action(
        self,
        user_id: Optional[uuid.UUID],
        company_id: Optional[uuid.UUID],
        entity_type: str,
        entity_id: Optional[uuid.UUID],
        action: str,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        # Convert any non-serializable objects (like UUIDs or dates) to strings
        def sanitize(d: Optional[Dict[str, Any]]):
            if not d: return None
            return {k: str(v) if isinstance(v, (uuid.UUID, datetime)) else v for k, v in d.items()}

        log = AuditLog(
            user_id=user_id,
            company_id=company_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            old_values=sanitize(old_values),
            new_values=sanitize(new_values),
            ip_address=ip_address,
            user_agent=user_agent
        )
        self.db.add(log)
        # We don't commit here usually, let the parent service handle it
        await self.db.flush()
        return log

    async def get_logs(
        self,
        company_id: uuid.UUID,
        entity_type: Optional[str] = None,
        entity_id: Optional[uuid.UUID] = None,
        limit: int = 100
    ):
        stmt = select(AuditLog).where(AuditLog.company_id == company_id)
        if entity_type:
            stmt = stmt.where(AuditLog.entity_type == entity_type)
        if entity_id:
            stmt = stmt.where(AuditLog.entity_id == entity_id)

        stmt = stmt.order_by(AuditLog.created_at.desc()).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()
