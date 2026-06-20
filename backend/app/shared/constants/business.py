from enum import Enum

class VoucherType(str, Enum):
    SALES = "SALES"
    PURCHASE = "PURCHASE"
    PAYMENT = "PAYMENT"
    RECEIPT = "RECEIPT"
    CONTRA = "CONTRA"
    JOURNAL = "JOURNAL"
    OPENING = "OPENING"

class VoucherStatus(str, Enum):
    DRAFT = "DRAFT"
    POSTED = "POSTED"
    CANCELLED = "CANCELLED"

class ItemType(str, Enum):
    PRODUCT = "PRODUCT"
    SERVICE = "SERVICE"

class AccountNature(str, Enum):
    ASSET = "ASSET"
    LIABILITY = "LIABILITY"
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"

class BalanceType(str, Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"
