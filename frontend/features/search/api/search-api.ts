import apiClient from "@/lib/api-client";
import { ApiResponse } from "../../auth/types";

export interface SearchResult {
  id: string;
  entity_type: string;
  entity_id: string;
  title: string;
  subtitle?: string;
  url: string;
}

export const searchGlobal = async (q: string): Promise<SearchResult[]> => {
  const res = await apiClient.get<ApiResponse<SearchResult[]>>("/api/v1/search", { params: { q } });
  return res.data.data;
};
