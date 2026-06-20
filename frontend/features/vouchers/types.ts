export enum VoucherType {
  SALES = "SALES",
  PURCHASE = "PURCHASE",
  PAYMENT = "PAYMENT",
  RECEIPT = "RECEIPT",
  CONTRA = "CONTRA",
  JOURNAL = "JOURNAL",
  OPENING = "OPENING",
}

export enum VoucherStatus {
  DRAFT = "DRAFT",
  POSTED = "POSTED",
  CANCELLED = "CANCELLED",
}

export interface VoucherEntry {
  id?: string;
  ledger_id: string;
  debit_amount: number;
  credit_amount: number;
  narration?: string;
}

export interface InventoryTransaction {
  id?: string;
  stock_item_id: string;
  quantity: number;
  rate: number;
  amount: number;
  direction: number;
}

export interface Voucher {
  id: string;
  company_id: string;
  financial_year_id: string;
  voucher_type: VoucherType;
  voucher_number: string;
  voucher_date: string;
  status: VoucherStatus;
  narration?: string;
  entries: VoucherEntry[];
  inventory_entries: InventoryTransaction[];
  created_at: string;
  updated_at: string;
}

export interface VoucherCreateData {
  voucher_type: VoucherType;
  voucher_date: string;
  narration?: string;
  entries: {
    ledger_id: string;
    debit_amount: number;
    credit_amount: number;
    narration?: string;
  }[];
  inventory_entries?: {
    stock_item_id: string;
    quantity: number;
    rate: number;
    narration?: string;
  }[];
}
