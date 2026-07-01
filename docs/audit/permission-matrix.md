# Phase 0.11 — Permission Coverage Matrix

This matrix maps every API endpoint to its required domain permission.

## 1. Banking Module
| Endpoint | Action | Permission |
| :--- | :--- | :--- |
| `POST /banking/bank-accounts` | Link Bank Account | `banking:manage` |
| `GET /banking/bank-accounts` | View Bank Accounts | `banking:view` |
| `POST /banking/payments` | Record Payment | `banking:transact` |
| `POST /banking/receipts` | Record Receipt | `banking:transact` |
| `GET /banking/invoices/{id}/outstanding` | Check Outstanding | `banking:view` |
| `POST /banking/statements` | Import Statement | `banking:manage` |
| `POST /banking/statement-lines/{id}/reconcile` | Reconcile Line | `banking:manage` |

## 2. Billing Module
| Endpoint | Action | Permission |
| :--- | :--- | :--- |
| `POST /billing/invoices` | Create Invoice | `invoice:create` |
| `GET /billing/invoices` | List Invoices | `invoice:view` |
| `GET /billing/invoices/{id}` | View Invoice Detail | `invoice:view` |
| `POST /billing/invoices/{id}/post` | Post Invoice | `invoice:post` |
| `POST /billing/invoices/{id}/cancel` | Cancel Invoice | `invoice:cancel` |
| `GET /billing/invoices/{id}/pdf` | Generate PDF | `invoice:view` |

## 3. Masters Module
| Endpoint | Action | Permission |
| :--- | :--- | :--- |
| `POST /masters/account-groups` | Create Group | `masters:manage` |
| `GET /masters/account-groups` | List Groups | `masters:view` |
| `PATCH /masters/account-groups/{id}` | Update Group | `masters:manage` |
| `DELETE /masters/account-groups/{id}` | Delete Group | `masters:manage` |
| `POST /masters/ledgers` | Create Ledger | `masters:manage` |
| `GET /masters/ledgers` | List Ledgers | `masters:view` |
| `GET /masters/ledgers/{id}` | View Ledger | `masters:view` |
| `PATCH /masters/ledgers/{id}` | Update Ledger | `masters:manage` |
| `POST /masters/units` | Create Unit | `masters:manage` |
| `GET /masters/units` | List Units | `masters:view` |
| `PATCH /masters/units/{id}` | Update Unit | `masters:manage` |
| `DELETE /masters/units/{id}` | Delete Unit | `masters:manage` |
| `POST /masters/stock-groups` | Create Stock Group | `masters:manage` |
| `GET /masters/stock-groups` | List Stock Groups | `masters:view` |
| `POST /masters/stock-items` | Create Stock Item | `masters:manage` |
| `GET /masters/stock-items` | List Stock Items | `masters:view` |
| `POST /masters/warehouses` | Create Warehouse | `masters:manage` |
| `GET /masters/warehouses` | List Warehouses | `masters:view` |

## 4. Inventory Module
| Endpoint | Action | Permission |
| :--- | :--- | : :--- |
| `POST /inventory/adjustments` | Create Adjustment | `inventory:manage` |
| `GET /inventory/adjustments` | List Adjustments | `inventory:view` |
| `GET /inventory/adjustments/{id}` | View Adjustment | `inventory:view` |
| `POST /inventory/adjustments/{id}/post` | Post Adjustment | `inventory:manage` |
| `POST /inventory/adjustments/{id}/cancel` | Cancel Adjustment | `inventory:manage` |
| `POST /inventory/transfers` | Create Transfer | `inventory:manage` |
| `GET /inventory/transfers` | List Transfers | `inventory:view` |
| `GET /inventory/transfers/{id}` | View Transfer | `inventory:view` |
| `POST /inventory/transfers/{id}/post` | Post Transfer | `inventory:manage` |
| `POST /inventory/transfers/{id}/cancel` | Cancel Transfer | `inventory:manage` |

## 5. Vouchers Module
| Endpoint | Action | Permission |
| :--- | :--- | :--- |
| `POST /vouchers` | Create Voucher | `voucher:create` |
| `GET /vouchers` | List Vouchers | `voucher:view` |
| `GET /vouchers/{id}` | View Voucher | `voucher:view` |
| `POST /vouchers/{id}/post` | Post Voucher | `voucher:post` |
| `POST /vouchers/{id}/cancel` | Cancel Voucher | `voucher:cancel` |

## 6. Parties Module
| Endpoint | Action | Permission |
| :--- | :--- | :--- |
| `POST /parties` | Create Party | `party:create` |
| `GET /parties` | List Parties | `party:view` |
| `GET /parties/{id}` | View Party | `party:view` |
| `PATCH /parties/{id}` | Update Party | `party:update` |
| `DELETE /parties/{id}` | Delete Party | `party:delete` |

## 7. Reports Module
| Endpoint | Action | Permission |
| :--- | :--- | :--- |
| `GET /reports/trial-balance` | View Trial Balance | `report:view` |
| `GET /reports/general-ledger/{id}` | View Ledger | `report:view` |
| `GET /reports/stock-summary` | View Stock | `report:view` |
| `GET /reports/dashboard-metrics` | View KPI | `report:view` |
| `GET /reports/profit-loss` | View P&L | `report:view` |
| `GET /reports/balance-sheet` | View Balance Sheet | `report:view` |
| `GET /reports/trial-balance/excel` | Export Excel | `report:export` |
| `GET /reports/warehouse-stock/{id}` | View WH Stock | `report:view` |
| `GET /reports/transfer-history` | View History | `report:view` |

## 8. Team & Company Settings
| Endpoint | Action | Permission |
| :--- | :--- | :--- |
| `PUT /companies/{id}` | Update Company | `company:manage` |
| `POST /companies/{id}/financial-years/{id}/close` | Close FY | `company:manage` |
| `GET /companies/{id}/members` | View Team | `team:view` |
| `POST /companies/{id}/invite` | Invite Member | `team:invite` |
| `GET /companies/{id}/invitations` | View Invites | `team:view` |

## 9. Search & Activity
| Endpoint | Action | Permission |
| :--- | :--- | :--- |
| `GET /search` | Global Search | `search:use` |
| `GET /audit/logs` | View Audit Logs | `audit:view` |

## 10. Notifications
| Endpoint | Action | Permission |
| :--- | :--- | :--- |
| `GET /notifications` | View Alerts | `notification:view` |
| `POST /notifications/{id}/read` | Mark Read | `notification:update` |
| `POST /notifications/read-all` | Mark All Read | `notification:update` |
