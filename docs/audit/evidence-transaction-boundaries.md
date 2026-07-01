# Phase 0B — Evidence Audit: Transaction Boundaries

| Service | Method | DB Flush/Commit Calls |
| :--- | :--- | :--- |
| AuditService | log_action | begin_nested, flush |
| BankingService | create_payment_or_receipt | commit |
| BankingService | import_bank_statement | flush, commit |
| BankingService | reconcile_line | commit |
| InvoiceService | create_invoice | flush, commit, commit |
| InvoiceService | post_invoice | flush, commit, commit |
| InvoiceService | cancel_invoice | commit, commit |
| CompanyService | create_company | flush, commit, commit, flush, flush |
| CompanyService | update_company | commit, commit |
| StockTransferService | create_adjustment | flush, commit |
| StockTransferService | post_adjustment | commit, commit |
| StockTransferService | cancel_adjustment | commit, commit |
| StockTransferService | create_transfer | flush, commit |
| StockTransferService | post_transfer | commit, commit |
| StockTransferService | cancel_transfer | commit, commit |
| MastersService | update_account_group | commit |
| MastersService | delete_account_group | commit |
| MastersService | update_ledger | commit |
| MastersService | update_unit | commit |
| MastersService | delete_unit | commit |
| NotificationService | publish_event | flush |
| NotificationService | mark_as_read | commit |
| NotificationService | mark_all_as_read | commit |
| PartyService | create_party | flush, commit, commit |
| PartyService | update_party | commit |
| PartyService | delete_party | commit |
| SearchService | update_index | begin_nested, flush |
| VoucherService | _generate_voucher_number | begin_nested, flush |
| VoucherService | create_voucher | flush, flush, commit |
| VoucherService | post_voucher | flush, commit |
| VoucherService | cancel_voucher | flush, commit |