import uuid
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import List, Sequence, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import joinedload
from fastapi import HTTPException

from .models import CompanyInvitation
from .schemas.team import CompanyInvitationCreate
from app.modules.auth.models import User, Role, UserCompanyRole
from app.modules.audit.service import AuditService
from app.modules.notifications.service import NotificationService
from app.shared.constants.business import InvitationStatus


class TeamService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.audit_service = AuditService(db)
        self.notification_service = NotificationService(db)

    def _hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    async def invite_user(
        self,
        company_id: uuid.UUID,
        user_id: uuid.UUID,
        data: CompanyInvitationCreate
    ) -> tuple[CompanyInvitation, str]:
        # Check for existing pending invitation
        stmt = select(CompanyInvitation).where(
            and_(
                CompanyInvitation.company_id == company_id,
                CompanyInvitation.email == data.email,
                CompanyInvitation.status == InvitationStatus.PENDING
            )
        )
        res = await self.db.execute(stmt)
        if res.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="An invitation is already pending for this email")

        # Generate token
        token = secrets.token_urlsafe(32)
        token_hash = self._hash_token(token)

        invitation = CompanyInvitation(
            company_id=company_id,
            email=data.email,
            role_id=data.role_id,
            token_hash=token_hash,
            status=InvitationStatus.PENDING,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
            invited_by_id=user_id,
            created_by=user_id,
            updated_by=user_id
        )
        self.db.add(invitation)
        await self.db.commit()
        await self.db.refresh(invitation)

        await self.audit_service.log_action(
            user_id=user_id,
            company_id=company_id,
            entity_type="TEAM",
            entity_id=invitation.id,
            action="INVITE",
            new_values={"email": data.email, "role_id": str(data.role_id)}
        )
        await self.db.commit()

        return invitation, token

    async def get_members(self, company_id: uuid.UUID) -> List[dict]:
        stmt = (
            select(User, Role, UserCompanyRole)
            .join(UserCompanyRole, User.id == UserCompanyRole.user_id)
            .join(Role, Role.id == UserCompanyRole.role_id)
            .where(UserCompanyRole.company_id == company_id)
        )
        res = await self.db.execute(stmt)
        members = []
        for user, role, ucr in res:
            members.append({
                "user_id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "role_name": role.name,
                "is_owner": ucr.is_owner,
                "last_active_at": user.last_active_at
            })
        return members

    async def get_invitations(self, company_id: uuid.UUID) -> List[CompanyInvitation]:
        stmt = (
            select(CompanyInvitation)
            .options(joinedload(CompanyInvitation.role), joinedload(CompanyInvitation.invited_by))
            .where(CompanyInvitation.company_id == company_id)
            .order_by(CompanyInvitation.created_at.desc())
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def accept_invitation(self, token: str, user_id: uuid.UUID):
        token_hash = self._hash_token(token)
        stmt = select(CompanyInvitation).where(CompanyInvitation.token_hash == token_hash)
        res = await self.db.execute(stmt)
        invitation = res.scalar_one_or_none()

        if not invitation:
            raise HTTPException(status_code=404, detail="Invalid invitation token")

        if invitation.status != InvitationStatus.PENDING:
            raise HTTPException(status_code=400, detail=f"Invitation is already {invitation.status}")

        if invitation.expires_at < datetime.now(timezone.utc):
            invitation.status = InvitationStatus.EXPIRED
            await self.db.commit()
            raise HTTPException(status_code=400, detail="Invitation has expired")

        # Create membership
        user_company_role = UserCompanyRole(
            user_id=user_id,
            company_id=invitation.company_id,
            role_id=invitation.role_id,
            is_owner=False
        )
        self.db.add(user_company_role)

        invitation.status = InvitationStatus.ACCEPTED
        invitation.accepted_at = datetime.now(timezone.utc)

        await self.db.commit()

        await self.audit_service.log_action(
            user_id=user_id,
            company_id=invitation.company_id,
            entity_type="TEAM",
            entity_id=user_id,
            action="JOIN",
            new_values={"invitation_id": str(invitation.id)}
        )

        # Trigger: Team Invite Accepted
        await self.notification_service.publish_event(
            company_id=invitation.company_id,
            event_type="team.invite_accepted",
            entity_type="USER",
            entity_id=user_id,
            payload={"email": invitation.email}
        )
        await self.db.commit()

    async def revoke_invitation(self, company_id: uuid.UUID, user_id: uuid.UUID, invitation_id: uuid.UUID):
        invitation = await self.db.get(CompanyInvitation, invitation_id)
        if not invitation or invitation.company_id != company_id:
             raise HTTPException(status_code=404, detail="Invitation not found")

        invitation.status = InvitationStatus.REVOKED
        await self.db.commit()

        await self.audit_service.log_action(
            user_id=user_id,
            company_id=company_id,
            entity_type="TEAM",
            entity_id=invitation.id,
            action="REVOKE_INVITE"
        )
        await self.db.commit()
