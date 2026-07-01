import uuid
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.modules.vouchers.models import Voucher, VoucherEntry
from app.modules.masters.models import Ledger, StockItem, StockBalance
from app.modules.billing.models import Invoice
from app.shared.constants.business import VoucherStatus, InvoiceStatus

class IntegrityScanner:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def scan_ledgers(self, company_id: uuid.UUID):
        """Verify cached current_balance matches transaction history."""
        errors = []
        stmt = select(Ledger).where(Ledger.company_id == company_id)
        res = await self.db.execute(stmt)
        ledgers = res.scalars().all()

        for ledger in ledgers:
            # Recompute
            stmt_hist = select(func.sum(VoucherEntry.debit_amount - VoucherEntry.credit_amount)).join(Voucher).where(
                and_(VoucherEntry.ledger_id == ledger.id, Voucher.status == VoucherStatus.POSTED)
            )
            res_hist = await self.db.execute(stmt_hist)
            computed = res_hist.scalar() or Decimal("0.00")

            if abs(Decimal(str(ledger.current_balance)) - computed) > 0.01:
                errors.append(f"Ledger {ledger.name} ({ledger.id}): Cached {ledger.current_balance} != Computed {computed}")

        return errors

    async def scan_vouchers(self, company_id: uuid.UUID):
        """Verify all vouchers are balanced."""
        errors = []
        stmt = select(Voucher).where(Voucher.company_id == company_id)
        res = await self.db.execute(stmt)
        vouchers = res.scalars().all()

        for voucher in vouchers:
            stmt_entries = select(func.sum(VoucherEntry.debit_amount), func.sum(VoucherEntry.credit_amount)).where(VoucherEntry.voucher_id == voucher.id)
            res_entries = await self.db.execute(stmt_entries)
            dr, cr = res_entries.first()
            dr = dr or Decimal("0.00")
            cr = cr or Decimal("0.00")

            if abs(dr - cr) > 0.01:
                errors.append(f"Voucher {voucher.voucher_number} ({voucher.id}): Unbalanced (Dr {dr}, Cr {cr})")

        return errors

    async def scan_invoices(self, company_id: uuid.UUID):
        """Verify posted invoices have exactly one associated voucher."""
        errors = []
        stmt = select(Invoice).where(and_(Invoice.company_id == company_id, Invoice.status == InvoiceStatus.POSTED))
        res = await self.db.execute(stmt)
        invoices = res.scalars().all()

        for invoice in invoices:
            if not invoice.voucher_id:
                errors.append(f"Invoice {invoice.invoice_number} ({invoice.id}): POSTED but missing voucher_id")
            else:
                v = await self.db.get(Voucher, invoice.voucher_id)
                if not v:
                    errors.append(f"Invoice {invoice.invoice_number} ({invoice.id}): Points to non-existent voucher {invoice.voucher_id}")

        return errors
