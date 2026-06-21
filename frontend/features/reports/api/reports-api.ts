import apiClient from "@/lib/api-client";
import { ApiResponse } from "../../auth/types";

export const getTrialBalance = async () => {
  const res = await apiClient.get<ApiResponse<any>>("/api/v1/reports/trial-balance");
  return res.data.data;
};

export const getGeneralLedger = async (ledgerId: string) => {
  const res = await apiClient.get<ApiResponse<any>>(`/api/v1/reports/general-ledger/${ledgerId}`);
  return res.data.data;
};

export const getStockSummary = async () => {
  const res = await apiClient.get<ApiResponse<any>>("/api/v1/reports/stock-summary");
  return res.data.data;
};

export const getDashboardMetrics = async () => {
  const res = await apiClient.get<ApiResponse<any>>("/api/v1/reports/dashboard-metrics");
  return res.data.data;
};
