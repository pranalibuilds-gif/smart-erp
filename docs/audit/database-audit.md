# Phase 0.3 — Database Integrity Audit

## 1. Table Inventory & Constraint Verification

Verified against the current schema in `backend/app/modules/*/models.py`.

| Table | PK | Key Foreign Keys | Unique Constraints |
| :--- | :--- | :--- | :--- |
| `users` | `id` | - | `email` |
| `companies` | `id` | - | `slug` |
| `user_company_roles` | `(user_id, company_id)` | `users`, `companies`, `roles` | - |
| `financial_years` | `id` | `companies` | `(company_id, start_date)` |
| `ledgers` | `id` | `companies`, `account_groups` | - |
| `parties` | `id` | `companies`, `ledgers` | `(company_id, name)` |
| `vouchers` | `id` | `companies`, `financial_years` | `(company_id, fy_id, type, number)` |
| `voucher_entries` | `id` | `vouchers`, `ledgers` | - |
| `invoices` | `id` | `companies`, `parties`, `vouchers` | `(company_id, fy_id, invoice_number)` |
| `invoice_items` | `id` | `invoices`, `stock_items` | - |
| `stock_items` | `id` | `companies`, `units`, `stock_groups` | `(company_id, name)` |
| `stock_balances` | `id` | `warehouses`, `stock_items` | `(warehouse_id, stock_item_id)` |
| `bank_accounts` | `id` | `companies`, `ledgers` | `(company_id, account_number)` |
| `payment_allocations` | `id` | `vouchers`, `invoices` | - |
| `audit_logs` | `id` | `companies` | - |

## 2. Cascade Policy Audit

| Relation | Action | Expected | Match? |
| :--- | :--- | :--- | :--- |
| `User` -> `RefreshToken` | `CASCADE` | `CASCADE` | **YES** |
| `Company` -> *Tenant Data* | `CASCADE` | `CASCADE` | **YES** |
| `FinancialYear` -> `Voucher` | `RESTRICT` | `RESTRICT` | **YES** |
| `Ledger` -> `VoucherEntry` | `RESTRICT` | `RESTRICT` | **YES** |
| `Voucher` -> `VoucherEntry` | `CASCADE` | `CASCADE` | **YES** |
| `Invoice` -> `InvoiceItem` | `CASCADE` | `CASCADE` | **YES** |
| `User` -> `Voucher` | *N/A (No FK)* | `NO CASCADE` | **YES** |

## 3. Index Strategy

Verified critical indexes for multi-tenant performance and common lookups:

- **Tenant Isolation**: All tables have `ix_tablename_company_id`.
- **Voucher Search**: `(company_id, financial_year_id, status)` index on `vouchers`.
- **Inventory Performance**: `(stock_item_id, warehouse_id)` index on `inventory_transactions`.
- **Audit Trail**: `created_at` and `user_id` indexes on `audit_logs`.

## 4. Integrity Query Result
Running the following locally confirms zero orphan records:
```sql
-- Check for orphan VoucherEntries
SELECT COUNT(*) FROM voucher_entries ve 
LEFT JOIN vouchers v ON ve.voucher_id = v.id 
WHERE v.id IS NULL;
-- Result: 0
```
