# Phase 0.2 — Architecture Drift Detection

Verification of design decisions vs implementation.

| Decision | Expected Behavior | Actual Implementation | Match? | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Contextual RBAC | One role per user per company | PK on `(user_id, company_id)` | **YES** | Solid implementation. |
| Session Strategy | Refresh Token Rotation | Hash stored, deleted on rotation | **YES** | SHA-256 hashing used. |
| Party Model | One ledger per party | `Party.ledger_id` is unique | **YES** | Strict FK relation. |
| Voucher Engine | Double Entry Balance | Dr == Cr check in service | **YES** | Validated before commit. |
| Reporting | Snapshot-based FY closing | `fy_opening_balances` table | **YES** | Closure rolls over data. |
| Audit | Append-only snapshots | AuditService.log_action | **YES** | No update path in code. |
| Events | Decoupled notifications | DomainEvent model + Service | **YES** | Internal event loop verified. |
| Multi-Tenancy | Header-based isolation | `X-Company-ID` dependency | **YES** | Consistently applied. |

### Major Finding: Permission Enforcement
- **Resolved**: Initial audit found many router endpoints failed to use `PermissionRequired`. This was tracked as **RB-001** and has been **Fixed**. Every functional route is now guarded by the `Depends(PermissionRequired(...))` gate.
