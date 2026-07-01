# Phase 0B — Evidence Audit: Enum Stability

| Enum Class | Members | Persisted in DB? |
| :--- | :--- | :--- |
| VoucherType | SALES, PURCHASE, PAYMENT, RECEIPT, CONTRA, JOURNAL, OPENING | YES |
| VoucherStatus | DRAFT, POSTED, CANCELLED | YES |
| DocumentType | SALES, PURCHASE, SALES_RETURN, PURCHASE_RETURN, QUOTATION | YES |
| InvoiceStatus | DRAFT, POSTED, CANCELLED | YES |
| ItemType | PRODUCT, SERVICE | YES |
| AccountNature | ASSET, LIABILITY, INCOME, EXPENSE | YES |
| BalanceType | DEBIT, CREDIT | YES |
| LedgerType | GENERAL, CASH, BANK | YES |
| ChequeStatus | ISSUED, DEPOSITED, CLEARED, BOUNCED, CANCELLED | YES |
| InvitationStatus | PENDING, ACCEPTED, EXPIRED, REVOKED | YES |
| RoleType | SUPER_ADMIN, ADMIN, ACCOUNTANT, OPERATOR, VIEWER | YES |
| UserStatus | ACTIVE, INACTIVE, PENDING | YES |