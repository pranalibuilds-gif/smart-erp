# Tenancy & Security Invariants

| Invariant | Rule | Enforcement |
| :--- | :--- | :--- |
| **Strict Isolation** | Users cannot read or write data belonging to a company they are not a member of. | `Repository` filters, `Dependencies.get_current_company` |
| **Contextual Authorization** | Permissions are evaluated specifically for the active `X-Company-ID` context. | `PermissionRequired` dependency |
| **Scope Parameter Guard** | Resources referenced in a request (LEDGER, WH, ITEM) must belong to the authorized company. | Service Layer `company_id` validation checks (SEC-002) |
| **Timing Resistance** | Authentication latency must be uniform for valid and invalid emails. | `AuthService` (Dummy bcrypt hashing) |
