# Phase 0.1 — Domain Model Audit

This document verifies the purpose, dependencies, and business rules of the core entities in SmartERP.

## 1. Auth Module

### User
- **Purpose**: Represents an identity capable of accessing the system.
- **Owner Module**: Auth
- **Dependencies**: None.
- **Rules**: Must have a unique email. `is_superuser` flag grants global bypass of RBAC.
- **Deletion**: Soft-fail/Deactivation preferred. Hard delete cascades to `refresh_tokens`.

### Role & Permission
- **Purpose**: Defines access rights. Roles are containers for Permissions.
- **Owner Module**: Auth
- **Dependencies**: None.
- **Rules**: `Role.name` and `Permission.name` are unique.
- **Deletion**: RESTRICT if assigned.

### UserCompanyRole
- **Purpose**: Contextual RBAC link. Exactly one role per user per company.
- **Owner Module**: Auth / Companies
- **Rules**: Primary Key is `(user_id, company_id)`.

## 2. Core Module

### Company
- **Purpose**: Root tenant entity for data isolation.
- **Owner Module**: Companies
- **Dependencies**: None.
- **Rules**: Must have a unique `slug`. Default country is "India".
- **Deletion**: CASCADE to all tenant data (FinancialYears, Vouchers, etc.).

### FinancialYear
- **Purpose**: Defines the accounting period.
- **Owner Module**: Companies
- **Dependencies**: Company.
- **Rules**: Start and End dates should typically cover 12 months. `is_closed` flag locks the period.
- **Deletion**: RESTRICT if transactions exist.

## 3. Masters Module

### AccountGroup
- **Purpose**: Hierarchical classification for the Chart of Accounts.
- **Owner Module**: Masters
- **Dependencies**: Company, parent AccountGroup.
- **Rules**: Circular references are prohibited in service layer.

### Ledger
- **Purpose**: Specific accounts for recording transactions (Cash, Sales, Party Ledgers).
- **Owner Module**: Masters
- **Dependencies**: Company, AccountGroup.
- **Rules**: Opening balance must have a `balance_type` (DEBIT/CREDIT).

### StockItem
- **Purpose**: Inventory items for trading or production.
- **Owner Module**: Masters
- **Dependencies**: Company, Unit.
- **Rules**: Tracks `average_cost` (WAC) and `current_quantity`.

### Warehouse
- **Purpose**: Physical storage location.
- **Owner Module**: Masters
- **Dependencies**: Company.
- **Rules**: `name` and `code` must be unique per company.

## 4. Parties Module

### Party
- **Purpose**: External entities (Customers/Suppliers) the company transacts with.
- **Owner Module**: Parties
- **Dependencies**: Company, Ledger.
- **Rules**: Each party is linked to a unique Ledger. Name must be unique per company.
- **Deletion**: RESTRICT if transactions exist in the linked ledger.

## 5. Vouchers & Accounting

### Voucher
- **Purpose**: The source of truth for an accounting transaction.
- **Owner Module**: Vouchers
- **Dependencies**: Company, FinancialYear.
- **Rules**: Must have >=2 `VoucherEntry` rows. Total Debit must equal Total Credit. Immutable after posting.
- **Deletion**: Only cancellation allowed. No hard delete for posted vouchers.

### VoucherEntry
- **Purpose**: Individual debit/credit lines within a voucher.
- **Owner Module**: Vouchers
- **Dependencies**: Voucher, Ledger.
- **Rules**: Amount must be positive. Linked to exactly one Ledger.
- **Deletion**: CASCADE from Voucher.

### InventoryTransaction
- **Purpose**: Physical stock movement linked to a voucher.
- **Owner Module**: Vouchers / Inventory
- **Dependencies**: Voucher, StockItem, Warehouse.
- **Rules**: `direction` (1 for In, -1 for Out) determines stock impact.

## 6. Billing

### Invoice
- **Purpose**: Professional document for Sales/Purchase.
- **Owner Module**: Billing
- **Dependencies**: Company, Party, Voucher.
- **Rules**: Linked to exactly one `Voucher` for accounting impact.
- **Deletion**: CASCADE to InvoiceItems. Voucher should be cancelled separately.

### InvoiceItem
- **Purpose**: Line items within an invoice.
- **Owner Module**: Billing
- **Dependencies**: Invoice, StockItem, Warehouse.
- **Rules**: Captures snapshots of price, tax, and item details at the time of creation.

## 7. Banking

### PaymentAllocation
- **Purpose**: Links a Payment/Receipt Voucher to one or more Invoices.
- **Owner Module**: Banking
- **Dependencies**: Voucher, Invoice.
- **Rules**: Amount allocated cannot exceed the voucher total or invoice outstanding.

## 8. Notifications

### DomainEvent
- **Purpose**: Internal audit trail of business events for asynchronous processing.
- **Owner Module**: Notifications
- **Dependencies**: Company.
- **Rules**: Immutable record of system state changes.

### Notification
- **Purpose**: In-app alerts for users.
- **Owner Module**: Notifications
- **Dependencies**: User, Company.
- **Rules**: Generated from DomainEvents based on user preferences.

## 9. Search

### SearchDocument
- **Purpose**: Flattened searchable index of system entities.
- **Owner Module**: Search
- **Dependencies**: Company.
- **Rules**: Contains concatenated text for global keyword search.

## 10. Audit & Activity

### AuditLog
- **Purpose**: Permanent trail of system changes.
- **Owner Module**: Audit
- **Dependencies**: Company, User.
- **Rules**: Immutable. Records JSON snapshots of `old_values` and `new_values`.
