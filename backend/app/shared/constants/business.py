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

class DocumentType(str, Enum):
    SALES = "SALES"
    PURCHASE = "PURCHASE"
    SALES_RETURN = "SALES_RETURN"
    PURCHASE_RETURN = "PURCHASE_RETURN"
    QUOTATION = "QUOTATION"

class InvoiceStatus(str, Enum):
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

class LedgerType(str, Enum):
    GENERAL = "GENERAL"
    CASH = "CASH"
    BANK = "BANK"

class ChequeStatus(str, Enum):
    ISSUED = "ISSUED"
    DEPOSITED = "DEPOSITED"
    CLEARED = "CLEARED"
    BOUNCED = "BOUNCED"
    CANCELLED = "CANCELLED"

class InvitationStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"
