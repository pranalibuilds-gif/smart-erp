from enum import Enum

class RoleType(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    ACCOUNTANT = "ACCOUNTANT"
    OPERATOR = "OPERATOR"
    VIEWER = "VIEWER"

class UserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    PENDING = "PENDING"
