# Phase 0.5 — Service Boundary Audit

| Service | Allowed Responsibilities | Boundary Leaks |
| :--- | :--- | :--- |
| `AuthService` | Identity, Auth, JWT | None. |
| `CompanyService` | Tenant management, FY creation | Seeding defaults (Expected) |
| `VoucherService` | Double-entry logic, sequences | None. |
| `ReportService` | Read-only analytics | None. |
| `NotificationService` | Domain events to User Alerts | None. |
| `SearchService` | Index management | None. |

## Boundary Integrity Result: **PASS**
The Feature-based Modular Monolith structure is well-maintained. Interaction between modules (e.g., Voucher -> Inventory) happens via shared service injection or internal dependencies, not raw DB manipulation of other modules' tables.
