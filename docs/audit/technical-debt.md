# Phase 0.10 — Technical Debt Register

Inventory of known implementation shortcuts and unresolved issues.

| ID | Issue | Severity | Impact | Plan |
| :--- | :--- | :--- | :--- | :--- |
| **TD-001** | *Resolved: Permission enforcement implemented* | - | - | - |
| **TD-002** | Sequential voucher numbers lock sequence table | **LOW** | Performance | Consider cached sequences for v2. |
| **TD-003** | PDF generation is synchronous | **MEDIUM** | Scaling | Move to background task if load increases. |
| **TD-004** | Email invitations don't send real emails | **LOW** | UX | Integrate SMTP provider. |
| **TD-006** | Relationship Lazy Loading Risk | **HIGH** | Performance | Most relationships use lazy loading. While reports use optimized SQL, master-detail views (e.g., Invoice Detail) may trigger N+1 as load increases. | Verify and convert critical paths to `selectinload`. |

## Debt Density Result: **STABLE**
Apart from the critical permission gap (TD-001), the system has no structural debt that prevents production stability.
