import apiClient from "@/lib/api-client";
import { ApiResponse } from "../../auth/types";

export interface Notification {
  id: string;
  title: string;
  message: string;
  is_read: boolean;
  event_type?: string;
  entity_id?: string;
  created_at: string;
}

export const getNotifications = async (): Promise<Notification[]> => {
  const res = await apiClient.get<ApiResponse<Notification[]>>("/api/v1/notifications");
  return res.data.data;
};

export const markAsRead = async (id: string): Promise<void> => {
  await apiClient.post(`/api/v1/notifications/${id}/read`);
};

export const markAllAsRead = async (): Promise<void> => {
  await apiClient.post("/api/v1/notifications/read-all");
};
