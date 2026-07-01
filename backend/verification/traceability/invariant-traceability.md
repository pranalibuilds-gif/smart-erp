# Invariant Traceability Matrix

This matrix maps core business invariants to their enforcement mechanisms, detection tools, and the rigorous verification methods applied during the audit.

| Invariant | Enforcement Layer | Detection / Reconciliation | Verified | Mutation Tested | Fault Injected |
| :--- | :--- | :--- | :---: | :---: | :---: |
| **Double-Entry Balance** | `VoucherService` | `AuditEngine.audit_ledger_balances` | ✅ | ✅ | ✅ |
| **No Negative Stock** | `InventoryPostingService` | `AuditEngine.audit_inventory_integrity` | ✅ | ✅ | ✅ |
| **Company Isolation** | Repository Filters + Router Context | `test_stage3_tenant_boundaries.py` | ✅ | ✅ | N/A |
| **FY Immutability** | `FinancialYearService` | `test_illegal_fy_operations` | ✅ | ✅ | ✅ |
| **Gapless Numbering** | `VoucherSequence` (Pessimistic Locking) | `test_vouchers_sequential_no` | ✅ | ✅ | ✅ |
| **Sub-ledger Consistency** | `InventoryPostingService` | `AuditEngine.audit_inventory_integrity` | ✅ | ✅ | ✅ |
| **Payment Allocation** | `BankingService` | Outstanding Invoice Reports | ✅ | ✅ | ✅ |
| **Search Index Integrity** | `SearchService` (Async Soft-Fail) | Global Search API | ✅ | N/A | ✅ |
| **Audit Completeness** | `AuditService` | Audit Log API | ✅ | N/A | ✅ |

### Notes on Verification Depth

*   **Verified**: Invariant holds across the entire property-based and stateful fuzzing test corpus.
*   **Mutation Tested**: Invariant enforcement was intentionally broken, and the test suite correctly identified the defect.
*   **Fault Injected**: Application or database failure was injected during invariant update, and atomicity (rollback) was confirmed.
