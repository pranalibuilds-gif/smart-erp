from enum import Enum

class VoucherType(str, Enum):
    SALES = "SALES"
    PURCHASE = "PURCHASE"
    PAYMENT = "PAYMENT"
    RECEIPT = "RECEIPT"
    CONTRA = "CONTRA"
    JOURNAL = "JOURNAL"

class ItemType(str, Enum):
    PRODUCT = "PRODUCT"
    SERVICE = "SERVICE"
