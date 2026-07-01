# Phase 0B — Evidence Audit: Deletion & Cancellation Matrix

This matrix documents the policy for data removal and voiding across the system.

| Entity | Can Delete? | Deletion Policy | Can Cancel? | Cancellation Policy |
| :--- | :---: | :--- | :---: | :--- |
| **User** | **NO** | Only `is_active = false`. Identity must persist for audit logs. | **N/A** | - |
| **Company** | **YES** | `CASCADE` delete allowed only for account closure. | **N/A** | - |
| **FinancialYear** | **NO** | `RESTRICT` if transactions exist. | **N/A** | - |
| **AccountGroup** | **YES** | Allowed if no children and no ledgers linked. | **N/A** | - |
| **Ledger** | **NO** | `RESTRICT` if `VoucherEntry` exists. | **N/A** | - |
| **Party** | **NO** | `RESTRICT` if ledger has transactions. | **N/A** | - |
| **StockItem** | **NO** | `RESTRICT` if `InventoryTransaction` exists. | **N/A** | - |
| **Warehouse** | **NO** | `RESTRICT` if stock history exists. | **N/A** | - |
| **Voucher** | **DRAFT ONLY** | Drafts can be deleted. | **YES** | Posted vouchers are voided; Dr/Cr reversed. |
| **Invoice** | **DRAFT ONLY** | Drafts can be deleted. | **YES** | Marks status as CANCELLED. |
| **AuditLog** | **NEVER** | Permanent append-only record. | **N/A** | - |
| **DomainEvent**| **NEVER** | System log of actions. | **N/A** | - |

## Verification Logic
- **RESTRICT** is enforced via Database Foreign Key constraints (`ondelete="RESTRICT"`).
- **Draft Deletion** is enforced in the Service layer (e.g., `VoucherService.delete_voucher` checks `status == DRAFT`).
- **Soft Deactivation** (Users/Parties) is handled via `is_active` boolean flag.
