import { create } from "zustand";
import apiClient from "@/lib/api-client";

export interface Ledger {
  id: string;
  name: string;
  current_balance: number;
}

export interface StockItem {
  id: string;
  name: string;
  current_quantity: number;
  average_cost: number;
}

interface MasterState {
  ledgers: Ledger[];
  stockItems: StockItem[];
  isLoading: boolean;

  fetchMasters: () => Promise<void>;
}

export const useMasterStore = create<MasterState>((set) => ({
  ledgers: [],
  stockItems: [],
  isLoading: false,

  fetchMasters: async () => {
    set({ isLoading: true });
    try {
      const [ledgersRes, itemsRes] = await Promise.all([
        apiClient.get("/api/v1/masters/ledgers"),
        apiClient.get("/api/v1/masters/stock-items"),
      ]);
      set({
        ledgers: ledgersRes.data.data,
        stockItems: itemsRes.data.data,
        isLoading: false
      });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },
}));
