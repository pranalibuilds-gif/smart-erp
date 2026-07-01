# Phase 0B — Evidence Audit: ORM Loading Strategy

| Model | Relationship | Strategy |
| :--- | :--- | :--- |
| AuditLog | user | lazy (default) |
| RefreshToken | permissions | lazy (default) |
| BankStatementLine | ledger | lazy (default) |
| BankStatementLine | voucher | lazy (default) |
| BankStatementLine | invoice | lazy (default) |
| BankStatementLine | lines | lazy (default) |
| BankStatementLine | bank_ledger | lazy (default) |
| BankStatementLine | statement | lazy (default) |
| BankStatementLine | voucher | lazy (default) |
| InvoiceItem | items | lazy (default) |
| InvoiceItem | party | lazy (default) |
| InvoiceItem | voucher | lazy (default) |
| InvoiceItem | invoice | lazy (default) |
| CompanyInvitation | financial_years | lazy (default) |
| CompanyInvitation | company | lazy (default) |
| CompanyInvitation | company | lazy (default) |
| CompanyInvitation | role | lazy (default) |
| CompanyInvitation | invited_by | lazy (default) |
| StockTransferItem | items | lazy (default) |
| StockTransferItem | warehouse | lazy (default) |
| StockTransferItem | voucher | lazy (default) |
| StockTransferItem | adjustment | lazy (default) |
| StockTransferItem | stock_item | lazy (default) |
| StockTransferItem | items | lazy (default) |
| StockTransferItem | from_warehouse | lazy (default) |
| StockTransferItem | to_warehouse | lazy (default) |
| StockTransferItem | transfer | lazy (default) |
| StockTransferItem | stock_item | lazy (default) |
| StockBalance | parent | lazy (default) |
| StockBalance | group | lazy (default) |
| StockBalance | parent | lazy (default) |
| StockBalance | stock_group | lazy (default) |
| StockBalance | unit | lazy (default) |
| UserNotificationPreference | user | lazy (default) |
| Party | ledger | lazy (default) |
| VoucherSequence | entries | lazy (default) |
| VoucherSequence | inventory_entries | lazy (default) |
| VoucherSequence | voucher | lazy (default) |
| VoucherSequence | ledger | lazy (default) |
| VoucherSequence | voucher | lazy (default) |
| VoucherSequence | warehouse | lazy (default) |
| VoucherSequence | stock_item | lazy (default) |