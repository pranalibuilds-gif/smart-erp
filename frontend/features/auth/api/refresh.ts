import apiClient from "@/lib/api-client";
import { AuthResponse, ApiResponse } from "../types";

export const refresh = async (refreshToken: string): Promise<AuthResponse> => {
  const response = await apiClient.post<ApiResponse<AuthResponse>>("/api/v1/auth/refresh", {
    refresh_token: refreshToken,
  });
  return response.data.data;
};
