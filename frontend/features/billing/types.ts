export enum DocumentType {
  SALES = "SALES",
  PURCHASE = "PURCHASE",
  SALES_RETURN = "SALES_RETURN",
  PURCHASE_RETURN = "PURCHASE_RETURN",
  QUOTATION = "QUOTATION",
}

export enum InvoiceStatus {
  DRAFT = "DRAFT",
  POSTED = "POSTED",
  CANCELLED = "CANCELLED",
}

export interface InvoiceItem {
  id?: string;
  stock_item_id?: string;
  item_name: string;
  item_code?: string;
  unit_name?: string;
  hsn_code?: string;
  quantity: number;
  rate: number;
  tax_rate: number;
  taxable_amount: number;
  tax_amount: number;
  total_amount: number;
}

export interface Invoice {
  id: string;
  company_id: string;
  financial_year_id: string;
  party_id: string;
  voucher_id?: string;
  document_type: DocumentType;
  invoice_number: string;
  invoice_date: string;
  status: InvoiceStatus;
  taxable_amount: number;
  tax_amount: number;
  total_amount: number;
  narration?: string;
  items: InvoiceItem[];
  created_at: string;
  updated_at: string;
}

export interface InvoiceCreateData {
  party_id: string;
  document_type: DocumentType;
  invoice_date: string;
  narration?: string;
  items: {
    stock_item_id?: string;
    item_name: string;
    item_code?: string;
    unit_name?: string;
    hsn_code?: string;
    quantity: number;
    rate: number;
    tax_rate: number;
  }[];
}
