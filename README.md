# SmartERP

A professional, modular, keyboard-first ERP system for small to medium businesses.

## Architecture Overview

### Tech Stack
- **Backend**: FastAPI (Python 3.11+), SQLAlchemy 2.0 (Async), PostgreSQL, Pydantic v2.
- **Frontend**: Next.js 14 (App Router), Tailwind CSS, Shadcn UI, Zustand.
- **Deployment**: Docker, GitHub Actions (CI).

### Core Design Principles
1. **Multi-Tenancy**: Mandatory `X-Company-ID` and `X-Financial-Year-ID` headers for all requests. Strict logical isolation between companies.
2. **Event-Driven**: Decoupled modules using internal Domain Events for cross-service triggers (e.g., Low Stock notifications).
3. **Double-Entry Accounting**: `VoucherEntry` is the immutable source of truth. Ledger caches are snapshots for high performance.
4. **Weighted Average Cost (WAC)**: Real-time inventory valuation synchronized with accounting.
5. **Traceability**: Append-only Audit Log with JSON snapshots of all state changes.

## Module Structure

- `app/modules/auth`: Identity, JWT sessions with rotation, and contextual RBAC.
- `app/modules/companies`: Multi-company management and Financial Year lifecycle.
- `app/modules/masters`: Accounting groups, Ledgers, Units, and Stock Items.
- `app/modules/parties`: Customer and Supplier unified management.
- `app/modules/vouchers`: Transactional engine (Accounting & Inventory integration).
- `app/modules/billing`: Sales and Purchase documents with PDF generation.
- `app/modules/inventory`: Multi-warehouse support, Transfers, and Adjustments.
- `app/modules/reports`: Financial statements (P&L, Balance Sheet) and Stock Analytics.
- `app/modules/audit`: Permanent change tracking.
- `app/modules/notifications`: Internal event-driven alert system.
- `app/modules/search`: High-performance universal search index.

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Node.js 20+
- Python 3.11+

### Local Development

1. **Setup Backend**:
   ```bash
   cd backend
   uv sync
   # Set environment variables in .env
   uv run alembic upgrade head
   uv run uvicorn app.main:app --reload
   ```

2. **Setup Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

### Running Tests
```bash
cd backend
uv run pytest
```

## License
Proprietary. All rights reserved.
