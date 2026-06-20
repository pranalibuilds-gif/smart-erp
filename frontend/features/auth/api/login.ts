import apiClient from "@/lib/api-client";
import { AuthResponse, ApiResponse } from "../types";
import { LoginCredentials } from "../schemas";

export const login = async (credentials: LoginCredentials): Promise<AuthResponse> => {
  const response = await apiClient.post<ApiResponse<AuthResponse>>("/api/v1/auth/login", credentials);
  return response.data.data;
};
