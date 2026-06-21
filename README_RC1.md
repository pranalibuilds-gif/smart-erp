# SmartERP v1.0 Release Candidate (RC1)

## 1. Functional Coverage Matrix

| Module          | Status   | Integration Tested | Manual Verified |
| --------------- | -------- | ------------------ | --------------- |
| Auth & RBAC     | Complete | Yes                | Yes             |
| Multi-Tenancy   | Complete | Yes                | Yes             |
| Masters         | Complete | Yes                | Yes             |
| Parties         | Complete | Yes                | Yes             |
| Voucher Engine  | Complete | Yes                | Yes             |
| Billing         | Complete | Yes                | Yes             |
| Reports         | Complete | Yes                | Yes             |
| PDF Generation  | Complete | Yes                | Yes             |
| Audit Logging   | Complete | Yes                | Yes             |
| Warehouses      | Complete | Yes                | Yes             |
| FY Closing      | Complete | Yes                | Yes             |
| Banking         | Complete | Yes                | Yes             |
| Team Management | Complete | Yes                | Yes             |
| Notifications   | Complete | Yes                | Yes             |
| Global Search   | Complete | Yes                | Yes             |

---

## 2. Business Scenario Verification

### Scenario 1: Core Lifecycle
- [x] Create Company & Seed Defaults
- [x] Create Party & Stock Item
- [x] Purchase Stock (WAC = 10.00)
- [x] Sell Stock (WAC remains 10.00, Margin recorded)
- [x] Record Payment Receipt
- [x] Verify Trial Balance / Balance Sheet
- [x] Close Financial Year (Rollover successful)

### Scenario 2: Multi-Warehouse
- [x] Purchase into 'Main'
- [x] Transfer from 'Main' to 'Branch'
- [x] Sell from 'Branch'
- [x] Verify Warehouse Stock Summary

### Scenario 3: Collaborative RBAC
- [x] Invite user as ACCOUNTANT
- [x] Verify ACCOUNTANT can post vouchers but not manage team
- [x] Verify COMPANY ISOLATION (User A cannot access Company B data)

---

## 3. Production Risk Mitigation

### Secrets & Security
- [x] `JWT_SECRET_KEY` and `DATABASE_URL` extracted to environment variables.
- [x] Refresh tokens stored as SHA-256 hashes.
- [x] JWT Algorithm locked to HS256.
- [x] No sensitive data found in application logs.

### Data Privacy
- [x] All APIs strictly scoped via `X-Company-ID` and membership checks.
- [x] Global Search results filtered by `company_id`.
- [x] PDF generation validates invoice ownership.

---

## 4. Codebase Baseline

### Backend
- **Models**: 38
- **Endpoints**: ~80
- **Services**: 15
- **Integration Tests**: 11 files (covers core business paths)

### Frontend
- **Pages**: 33
- **Components**: 21 (Modularized)
- **State Stores**: 5 (Zustand-based)

---

## 5. Documentation
- [x] Architecture Overview (README.md)
- [x] Docker Orchestration (docker-compose.yml)
- [x] CI/CD Pipeline (.github/workflows/ci.yml)
- [x] Deployment Environment Config (.env.example)

---

**Sign-off Status**: **RC1 READY**
Date: 2026-06-22
Baseline Commit: `5a22fb7`
