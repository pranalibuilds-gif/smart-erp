import apiClient from "@/lib/api-client";
import { ApiResponse } from "../types";

export const logout = async (refreshToken: string): Promise<void> => {
  await apiClient.post<ApiResponse<null>>("/api/v1/auth/logout", {
    refresh_token: refreshToken,
  });
};
