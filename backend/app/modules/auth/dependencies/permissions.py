from typing import List
from fastapi import Depends, HTTPException, status
from app.modules.auth.models import User, Role
from .current_user import get_current_user
from .current_role import get_current_company_role

class PermissionRequired:
    def __init__(self, permission_name: str):
        self.permission_name = permission_name

    async def __call__(
        self,
        current_user: User = Depends(get_current_user),
        role: Role | None = Depends(get_current_company_role)
    ) -> bool:
        """
        Validates that the user has the required permission in the active company.
        Superusers bypass this check.
        """
        if current_user.is_superuser:
            return True

        if not role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No role assigned in this context"
            )

        # permissions were loaded via selectinload in current_role.py
        user_permissions = [p.name for p in role.permissions]

        if self.permission_name not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {self.permission_name} required"
            )

        return True
