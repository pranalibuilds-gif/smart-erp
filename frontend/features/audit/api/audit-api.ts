import apiClient from "@/lib/api-client";
import { ApiResponse } from "../../auth/types";

export interface AuditLog {
  id: string;
  user_id?: string;
  user_full_name?: string;
  entity_type: string;
  entity_id?: string;
  action: string;
  old_values?: any;
  new_values?: any;
  created_at: string;
}

export const getAuditLogs = async (params: { entity_type?: string, entity_id?: string, limit?: number } = {}) => {
  const res = await apiClient.get<ApiResponse<AuditLog[]>>("/api/v1/audit/logs", { params });
  return res.data.data;
};
