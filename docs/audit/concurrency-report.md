# Phase 2 Concurrency & Integrity Report

**Status**: PASS
**Date**: 2026-06-27

## 1. Concurrency Audit Summary
The objective was to verify the correctness of the ERP under heavy contention. We simulated parallel voucher posting, concurrent inventory sales, and simultaneous financial year closing.

## 2. Shared Resources & Hardening

### A. Ledger Balances
- **Risk**: Lost updates where multiple transactions update the same ledger simultaneously.
- **Remediation**: Consolidated all ledger updates into a single `SELECT ... FOR UPDATE` query at the start of the transaction, using `ORDER BY id` to guarantee a deterministic locking sequence. This eliminated observed deadlocks (RB-007).

### B. Voucher Numbering
- **Risk**: Duplicate voucher numbers under parallel creation.
- **Remediation**: Confirmed `VoucherSequence` uses row-level locking (`with_for_update`). Stressed with 20 parallel requests; all received unique, sequential numbers.

### C. Inventory Stocks
- **Risk**: Over-selling stock (Negative Stock) due to race conditions.
- **Remediation**: Implemented deterministic locking order for `StockItem` and `StockBalance` rows. Verified that concurrent sales exceeding available stock correctly reject the overage (RB-012).

### D. Financial Year Closure
- **Risk**: Posting a voucher while the admin is closing the year.
- **Remediation**: The `close_and_rollover` service now acquires an exclusive lock on the `FinancialYear` row before performing validation. `post_voucher` also locks the FY row, serializing these high-risk operations.

## 3. Remediated Concurrency Blockers

| ID | Description | Severity | Fix |
| :--- | :--- | :--- | :--- |
| **RB-006** | Double Invoice Posting | Critical | Added `with_for_update` to Invoice fetch and removed intermediate commits to ensure atomicity. |
| **RB-007** | Ledger Deadlock | High | Normalized locking order using `ORDER BY id` in SQL. |
| **RB-008** | FY Closing Race | High | Serialized FY operations by locking the FinancialYear row. |
| **RB-010** | Non-Atomic Transactions | Medium | Refactored Service layers to remove intermediate `db.commit()` calls. |

## 4. Integrity Invariants Verified
- [x] **No Duplicate Numbering**: Sequential numbers preserved.
- [x] **No Lost Updates**: Ledger balances equal sum of entries.
- [x] **No Negative Stock**: Warehouse-level enforcement held under load.
- [x] **Atomic Commits**: Vouchers never exist without their entries.
