import apiClient from "@/lib/api-client";
import { ApiResponse } from "../../auth/types";
import { Voucher } from "../../vouchers/types";

export interface BankAccount {
  id: string;
  ledger_id: string;
  account_name: string;
  account_number: string;
  bank_name: string;
  ifsc_code?: string;
  is_active: boolean;
}

export const listBankAccounts = async (): Promise<BankAccount[]> => {
  const res = await apiClient.get<ApiResponse<BankAccount[]>>("/api/v1/banking/bank-accounts");
  return res.data.data;
};

export const createPayment = async (data: any): Promise<Voucher> => {
  const res = await apiClient.post<ApiResponse<Voucher>>("/api/v1/banking/payments", data);
  return res.data.data;
};

export const createReceipt = async (data: any): Promise<Voucher> => {
  const res = await apiClient.post<ApiResponse<Voucher>>("/api/v1/banking/receipts", data);
  return res.data.data;
};

export const getInvoiceOutstanding = async (invoiceId: string): Promise<number> => {
  const res = await apiClient.get<ApiResponse<number>>(`/api/v1/banking/invoices/${invoiceId}/outstanding`);
  return res.data.data;
};
