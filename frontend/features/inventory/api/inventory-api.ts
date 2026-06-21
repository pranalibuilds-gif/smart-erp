import apiClient from "@/lib/api-client";
import { ApiResponse } from "../../auth/types";

export interface StockAdjustment {
  id: string;
  adjustment_no: string;
  adjustment_date: string;
  warehouse_id: string;
  status: string;
  reason?: string;
  notes?: string;
  voucher_id?: string;
  items: {
    id: string;
    stock_item_id: string;
    system_quantity: number;
    physical_quantity: number;
    difference_quantity: number;
    rate_snapshot: number;
  }[];
}

export const createAdjustment = async (data: any): Promise<StockAdjustment> => {
  const res = await apiClient.post<ApiResponse<StockAdjustment>>("/api/v1/inventory/adjustments", data);
  return res.data.data;
};

export const listAdjustments = async (): Promise<StockAdjustment[]> => {
  const res = await apiClient.get<ApiResponse<StockAdjustment[]>>("/api/v1/inventory/adjustments");
  return res.data.data;
};

export const getAdjustment = async (id: string): Promise<StockAdjustment> => {
  const res = await apiClient.get<ApiResponse<StockAdjustment>>(`/api/v1/inventory/adjustments/${id}`);
  return res.data.data;
};

export const postAdjustment = async (id: string): Promise<StockAdjustment> => {
  const res = await apiClient.post<ApiResponse<StockAdjustment>>(`/api/v1/inventory/adjustments/${id}/post`);
  return res.data.data;
};

export const cancelAdjustment = async (id: string): Promise<StockAdjustment> => {
  const res = await apiClient.post<ApiResponse<StockAdjustment>>(`/api/v1/inventory/adjustments/${id}/cancel`);
  return res.data.data;
};

// Transfers
export interface StockTransfer {
  id: string;
  transfer_no: string;
  transfer_date: string;
  from_warehouse_id: string;
  to_warehouse_id: string;
  status: string;
  notes?: string;
  items: {
    id: string;
    stock_item_id: string;
    quantity: number;
    rate_snapshot: number;
  }[];
}

export const createTransfer = async (data: any): Promise<StockTransfer> => {
  const res = await apiClient.post<ApiResponse<StockTransfer>>("/api/v1/inventory/transfers", data);
  return res.data.data;
};

export const listTransfers = async (): Promise<StockTransfer[]> => {
  const res = await apiClient.get<ApiResponse<StockTransfer[]>>("/api/v1/inventory/transfers");
  return res.data.data;
};

export const getTransfer = async (id: string): Promise<StockTransfer> => {
  const res = await apiClient.get<ApiResponse<StockTransfer>>(`/api/v1/inventory/transfers/${id}`);
  return res.data.data;
};

export const postTransfer = async (id: string): Promise<StockTransfer> => {
  const res = await apiClient.post<ApiResponse<StockTransfer>>(`/api/v1/inventory/transfers/${id}/post`);
  return res.data.data;
};

export const cancelTransfer = async (id: string): Promise<StockTransfer> => {
  const res = await apiClient.post<ApiResponse<StockTransfer>>(`/api/v1/inventory/transfers/${id}/cancel`);
  return res.data.data;
};
