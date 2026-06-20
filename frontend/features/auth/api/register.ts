import apiClient from "@/lib/api-client";
import { AuthResponse, ApiResponse } from "../types";
import { RegisterData } from "../schemas";

export const register = async (data: RegisterData): Promise<AuthResponse> => {
  const response = await apiClient.post<ApiResponse<AuthResponse>>("/api/v1/auth/register", data);
  return response.data.data;
};
