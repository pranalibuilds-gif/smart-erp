import apiClient from "@/lib/api-client";
import { User, ApiResponse } from "../types";

export const getMe = async (): Promise<User> => {
  const response = await apiClient.get<ApiResponse<User>>("/api/v1/auth/me");
  return response.data.data;
};
