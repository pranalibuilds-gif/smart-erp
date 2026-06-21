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

export interface Warehouse {
  id: string;
  name: string;
  code: string;
}

interface MasterState {
  ledgers: Ledger[];
  stockItems: StockItem[];
  warehouses: Warehouse[];
  isLoading: boolean;

  fetchMasters: () => Promise<void>;
}

export const useMasterStore = create<MasterState>((set) => ({
  ledgers: [],
  stockItems: [],
  warehouses: [],
  isLoading: false,

  fetchMasters: async () => {
    set({ isLoading: true });
    try {
      const [ledgersRes, itemsRes, warehousesRes] = await Promise.all([
        apiClient.get("/api/v1/masters/ledgers"),
        apiClient.get("/api/v1/masters/stock-items"),
        apiClient.get("/api/v1/masters/warehouses"),
      ]);
      set({
        ledgers: ledgersRes.data.data,
        stockItems: itemsRes.data.data,
        warehouses: warehousesRes.data.data,
        isLoading: false
      });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },
}));
