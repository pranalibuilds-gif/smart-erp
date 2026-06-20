import apiClient from "@/lib/api-client";
import { Invoice, InvoiceCreateData } from "../types";
import { ApiResponse } from "../../auth/types";

export const createInvoice = async (data: InvoiceCreateData): Promise<Invoice> => {
  const response = await apiClient.post<ApiResponse<Invoice>>("/api/v1/billing/invoices", data);
  return response.data.data;
};

export const listInvoices = async (): Promise<Invoice[]> => {
  const response = await apiClient.get<ApiResponse<Invoice[]>>("/api/v1/billing/invoices");
  return response.data.data;
};

export const getInvoice = async (id: string): Promise<Invoice> => {
  const response = await apiClient.get<ApiResponse<Invoice>>(`/api/v1/billing/invoices/${id}`);
  return response.data.data;
};

export const postInvoice = async (id: string): Promise<Invoice> => {
  const response = await apiClient.post<ApiResponse<Invoice>>(`/api/v1/billing/invoices/${id}/post`);
  return response.data.data;
};

export const cancelInvoice = async (id: string): Promise<Invoice> => {
  const response = await apiClient.post<ApiResponse<Invoice>>(`/api/v1/billing/invoices/${id}/cancel`);
  return response.data.data;
};
