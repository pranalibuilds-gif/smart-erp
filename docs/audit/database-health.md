# Phase 5 Database Health Audit

**Status**: UNDER REVIEW
**Date**: 2026-06-27

## 1. Indexing Audit

| Table | Current Indexes | Recommendation | Reason |
| :--- | :--- | :--- | :--- |
| **AuditLog** | `company_id`, `user_id`, `entity_type`, `action` | Add index on `created_at`. | Sorted log retrieval is common. |
| **Voucher** | `company_id`, `financial_year_id`, `voucher_type`, `voucher_number` | Add composite index `(company_id, financial_year_id, status)`. | High-frequency filtering by FY and Status. |
| **Invoice** | `company_id`, `financial_year_id`, `party_id`, `invoice_number`, `status` | Add composite index `(company_id, status)`. | Dashboard and listing optimization. |
| **InventoryTransaction** | `voucher_id`, `warehouse_id`, `stock_item_id` | Add composite `(stock_item_id, warehouse_id)`. | Stock balance recomputation speed. |

## 2. N+1 Query Audit

- **Vouchers**: `list_vouchers` uses `selectinload` for entries and inventory. **GOOD**.
- **Invoices**: `list_invoices` uses `selectinload` for items. **GOOD**.
- **Reporting**: Trial Balance and Ledger Integrity scan use aggregation queries. **GOOD**.
- **Missing**: `Invoice` and `VoucherEntry` lists should eager load `Party` and `Ledger` names to avoid N+1 during rendering.

## 3. Storage Strategy
- All monetary fields use `Numeric(15, 2)` for exact precision. **GOOD**.
- All timestamps use `DateTime(timezone=True)`. **GOOD**.
- UUIDs used for all primary keys to facilitate multi-tenant sharding if needed. **GOOD**.
