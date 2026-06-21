import uuid
from datetime import datetime, timezone
from typing import List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update
from .models import Notification, DomainEvent, UserNotificationPreference
from app.modules.auth.models import UserCompanyRole


class NotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def publish_event(
        self,
        company_id: uuid.UUID,
        event_type: str,
        entity_type: str,
        entity_id: uuid.UUID,
        payload: dict = None
    ):
        """
        Main entry point for business services to trigger automation.
        """
        event = DomainEvent(
            company_id=company_id,
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            payload=payload
        )
        self.db.add(event)
        await self.db.flush()

        # Process event (could be backgrounded later)
        await self._process_event(event)

    async def _process_event(self, event: DomainEvent):
        """
        Internal logic to turn events into user notifications.
        """
        # 1. Determine target users (usually admins + relevant staff)
        # For now, let's notify all admins of the company
        from app.modules.auth.models import Role
        stmt = (
            select(UserCompanyRole.user_id)
            .join(Role, Role.id == UserCompanyRole.role_id)
            .where(and_(
                UserCompanyRole.company_id == event.company_id,
                Role.name == "ADMIN"
            ))
        )
        res = await self.db.execute(stmt)
        admin_ids = res.scalars().all()

        for user_id in admin_ids:
            # Check preferences
            pref_stmt = select(UserNotificationPreference).where(and_(
                UserNotificationPreference.user_id == user_id,
                UserNotificationPreference.company_id == event.company_id,
                UserNotificationPreference.event_type == event.event_type
            ))
            pref_res = await self.db.execute(pref_stmt)
            pref = pref_res.scalar_one_or_none()

            if pref and not pref.is_enabled:
                continue

            # Create notification
            title, message = self._format_notification(event)
            notification = Notification(
                user_id=user_id,
                company_id=event.company_id,
                title=title,
                message=message,
                event_type=event.event_type,
                entity_id=event.entity_id
            )
            self.db.add(notification)

    def _format_notification(self, event: DomainEvent) -> tuple[str, str]:
        if event.event_type == "stock.low":
            item_name = event.payload.get("item_name", "An item")
            qty = event.payload.get("current_quantity", 0)
            return ("Low Stock Alert", f"{item_name} has reached {qty} units, which is below reorder level.")

        if event.event_type == "invoice.posted":
            inv_no = event.payload.get("invoice_number", "Invoice")
            return ("Invoice Posted", f"{inv_no} has been successfully posted to accounts.")

        if event.event_type == "team.invite_accepted":
            email = event.payload.get("email", "A new user")
            return ("Team Update", f"{email} has joined your company.")

        return ("System Notification", f"Event {event.event_type} occurred.")

    async def get_user_notifications(self, user_id: uuid.UUID, company_id: uuid.UUID, limit: int = 20):
        stmt = (
            select(Notification)
            .where(and_(Notification.user_id == user_id, Notification.company_id == company_id))
            .order_by(Notification.created_at.desc())
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def mark_as_read(self, notification_id: uuid.UUID, user_id: uuid.UUID):
        stmt = (
            update(Notification)
            .where(and_(Notification.id == notification_id, Notification.user_id == user_id))
            .values(is_read=True)
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def mark_all_as_read(self, user_id: uuid.UUID, company_id: uuid.UUID):
        stmt = (
            update(Notification)
            .where(and_(Notification.user_id == user_id, Notification.company_id == company_id))
            .values(is_read=True)
        )
        await self.db.execute(stmt)
        await self.db.commit()
