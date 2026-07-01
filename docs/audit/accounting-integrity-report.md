# Phase 3 Accounting Integrity Report

**Status**: PASS
**Date**: 2026-06-27

## 1. Executive Summary
Phase 3 focused on business-level correctness. We validated that the complex accounting and inventory rules (partial payments, WAC, FY rollover) produce mathematically accurate and reconciled outcomes.

## 2. Integrity Domain findings

### A. Partial Payments & Allocations
- **Finding**: Initial implementation allowed allocating more than the invoice's current outstanding balance.
- **Fix**: Added an explicit check in `BankingService` to verify that `allocated_amount <= get_invoice_outstanding()`.
- **Regression**: `tests/accounting/test_partial_payments.py`

### B. Weighted Average Cost (WAC)
- **Finding**: WAC was correctly calculated during inward movements and preserved during outward movements.
- **Verification**: Verified with mixed quantities and high-variance rates (e.g., 10@100 + 1@1000).
- **Regression**: `tests/accounting/test_wac.py`

### C. Financial Year Rollover
- **Finding**: Verified that Assets and Liabilities carry forward correctly while Income/Expense accounts reset to zero. Profit/Loss is correctly transferred to the Capital account opening balance in the subsequent year.
- **Regression**: `tests/accounting/test_fy_rollover.py`

### D. Snapshot Accuracy
- **Finding**: Historical documents correctly preserve item names at the time of transaction even if the master record is renamed.
- **Regression**: `tests/accounting/test_snapshot_accuracy.py`

## 3. Remediated Business Blockers

| ID | Description | Severity | Fix |
| :--- | :--- | :--- | :--- |
| **RB-011** | Over-allocation Allowed | High | Outstanding balance check added to Banking service. |
| **RB-012** | Missing Accountant Permissions | Medium | Accountant role lacked `banking:view` and `masters:view` required for operational workflows. |

## 4. Property-Based Verification
- [x] **Trial Balance Always Zeros**: Randomized journals confirmed that sum(Dr) - sum(Cr) across all ledgers remains 0.00.
- [x] **No Negative Outstanding**: Hardened allocation logic prevents negative invoice balances.
