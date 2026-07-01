# Accounting Permissions
ACCOUNT_GROUP_VIEW = "account_group:view"
ACCOUNT_GROUP_CREATE = "account_group:create"
ACCOUNT_GROUP_UPDATE = "account_group:update"
ACCOUNT_GROUP_DELETE = "account_group:delete"

LEDGER_VIEW = "ledger:view"
LEDGER_CREATE = "ledger:create"
LEDGER_UPDATE = "ledger:update"
LEDGER_DELETE = "ledger:delete"

# Inventory Permissions
UNIT_VIEW = "unit:view"
UNIT_CREATE = "unit:create"
UNIT_UPDATE = "unit:update"
UNIT_DELETE = "unit:delete"

STOCK_GROUP_VIEW = "stock_group:view"
STOCK_GROUP_CREATE = "stock_group:create"
STOCK_GROUP_UPDATE = "stock_group:update"
STOCK_GROUP_DELETE = "stock_group:delete"

STOCK_ITEM_VIEW = "stock_item:view"
STOCK_ITEM_CREATE = "stock_item:create"
STOCK_ITEM_UPDATE = "stock_item:update"
STOCK_ITEM_DELETE = "stock_item:delete"

# Party Permissions
PARTY_VIEW = "party:view"
PARTY_CREATE = "party:create"
PARTY_UPDATE = "party:update"
PARTY_DELETE = "party:delete"

# Voucher Permissions
VOUCHER_VIEW = "voucher:view"
VOUCHER_CREATE = "voucher:create"
VOUCHER_UPDATE = "voucher:update"
VOUCHER_DELETE = "voucher:delete"
VOUCHER_POST = "voucher:post"
VOUCHER_CANCEL = "voucher:cancel"

# Team Permissions
TEAM_VIEW = "team:view"
TEAM_INVITE = "team:invite"
TEAM_MANAGE = "team:manage"

# Settings Permissions
SETTINGS_VIEW = "settings:view"
SETTINGS_UPDATE = "settings:update"
COMPANY_VIEW = "company:view"
COMPANY_MANAGE = "company:manage"

# Search Permissions
SEARCH_USE = "search:use"

# Report Permissions
REPORT_VIEW = "report:view"

# Billing Permissions
INVOICE_VIEW = "invoice:view"
INVOICE_CREATE = "invoice:create"
INVOICE_POST = "invoice:post"

# Master aliases
MASTERS_VIEW = "masters:view"
MASTERS_MANAGE = "masters:manage"

# Banking Permissions
BANKING_VIEW = "banking:view"
BANKING_MANAGE = "banking:manage"
BANKING_TRANSACT = "banking:transact"

# Audit Permissions
AUDIT_VIEW = "audit:view"

# Inventory Transaction Permissions
INVENTORY_VIEW = "inventory:view"
INVENTORY_MANAGE = "inventory:manage"

ALL_PERMISSIONS = [
    ACCOUNT_GROUP_VIEW, ACCOUNT_GROUP_CREATE, ACCOUNT_GROUP_UPDATE, ACCOUNT_GROUP_DELETE,
    LEDGER_VIEW, LEDGER_CREATE, LEDGER_UPDATE, LEDGER_DELETE,
    UNIT_VIEW, UNIT_CREATE, UNIT_UPDATE, UNIT_DELETE,
    STOCK_GROUP_VIEW, STOCK_GROUP_CREATE, STOCK_GROUP_UPDATE, STOCK_GROUP_DELETE,
    STOCK_ITEM_VIEW, STOCK_ITEM_CREATE, STOCK_ITEM_UPDATE, STOCK_ITEM_DELETE,
    PARTY_VIEW, PARTY_CREATE, PARTY_UPDATE, PARTY_DELETE,
    VOUCHER_VIEW, VOUCHER_CREATE, VOUCHER_UPDATE, VOUCHER_DELETE, VOUCHER_POST, VOUCHER_CANCEL,
    TEAM_VIEW, TEAM_INVITE, TEAM_MANAGE,
    SETTINGS_VIEW, SETTINGS_UPDATE, COMPANY_VIEW, COMPANY_MANAGE,
    SEARCH_USE, REPORT_VIEW, INVOICE_VIEW, INVOICE_CREATE, INVOICE_POST, MASTERS_VIEW, MASTERS_MANAGE,
    BANKING_VIEW, BANKING_MANAGE, BANKING_TRANSACT, AUDIT_VIEW,
    INVENTORY_VIEW, INVENTORY_MANAGE
]
