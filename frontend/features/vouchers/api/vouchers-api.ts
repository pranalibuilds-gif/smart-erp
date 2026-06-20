import apiClient from "@/lib/api-client";
import { Voucher, VoucherCreateData } from "../types";
import { ApiResponse } from "../../auth/types";

export const createVoucher = async (data: VoucherCreateData): Promise<Voucher> => {
  const response = await apiClient.post<ApiResponse<Voucher>>("/api/v1/vouchers", data);
  return response.data.data;
};

export const listVouchers = async (): Promise<Voucher[]> => {
  const response = await apiClient.get<ApiResponse<Voucher[]>>("/api/v1/vouchers");
  return response.data.data;
};

export const getVoucher = async (id: string): Promise<Voucher> => {
  const response = await apiClient.get<ApiResponse<Voucher>>(`/api/v1/vouchers/${id}`);
  return response.data.data;
};

export const postVoucher = async (id: string): Promise<Voucher> => {
  const response = await apiClient.post<ApiResponse<Voucher>>(`/api/v1/vouchers/${id}/post`);
  return response.data.data;
};

export const cancelVoucher = async (id: string): Promise<Voucher> => {
  const response = await apiClient.post<ApiResponse<Voucher>>(`/api/v1/vouchers/${id}/cancel`);
  return response.data.data;
};
