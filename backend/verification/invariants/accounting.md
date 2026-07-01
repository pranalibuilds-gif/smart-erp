# Accounting Invariants

| Invariant | Rule | Enforcement |
| :--- | :--- | :--- |
| **Balance Integrity** | Every voucher must have Total Debits == Total Credits. | `VoucherService.create_voucher`, `VoucherService.post_voucher` |
| **Double-Entry Symmetry** | Every financial operation must affect at least two distinct accounting entries. | `VoucherService.create_voucher` (min_length=2) |
| **Financial Immutability** | No new vouchers can be posted or cancelled in a closed Financial Year. | `VoucherService.post_voucher`, `VoucherService.cancel_voucher` |
| **Opening Consistency** | Ledger current balance must always equal Opening Balance + Σ(Transactions). | `VoucherService.post_voucher` (Atomic Update) |
| **Gapless Numbering** | Vouchers within a company/FY/type must have sequential, non-repeating numbers. | `VoucherService._generate_voucher_number` (Pessimistic Locking) |
