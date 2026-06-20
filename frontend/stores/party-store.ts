import { create } from "zustand";
import apiClient from "@/lib/api-client";

export interface Party {
  id: string;
  name: string;
  display_name?: string;
  mobile?: string;
  email?: string;
  gstin?: string;
  pan?: string;
  address?: string;
  credit_limit: number;
  is_customer: boolean;
  is_supplier: boolean;
  is_active: boolean;
  ledger_id: string;
  outstanding_balance: number;
}

interface PartyState {
  parties: Party[];
  isLoading: boolean;

  fetchParties: (type?: string) => Promise<void>;
  createParty: (data: any) => Promise<Party>;
  updateParty: (id: string, data: any) => Promise<Party>;
  deleteParty: (id: string) => Promise<void>;
}

export const usePartyStore = create<PartyState>((set) => ({
  parties: [],
  isLoading: false,

  fetchParties: async (type = "all") => {
    set({ isLoading: true });
    try {
      const response = await apiClient.get(`/api/v1/parties?party_type=${type}`);
      set({ parties: response.data.data, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  createParty: async (data) => {
    const response = await apiClient.post("/api/v1/parties", data);
    const newParty = response.data.data;
    set((state) => ({ parties: [newParty, ...state.parties] }));
    return newParty;
  },

  updateParty: async (id, data) => {
    const response = await apiClient.patch(`/api/v1/parties/${id}`, data);
    const updated = response.data.data;
    set((state) => ({
      parties: state.parties.map((p) => (p.id === id ? updated : p)),
    }));
    return updated;
  },

  deleteParty: async (id) => {
    await apiClient.delete(`/api/v1/parties/${id}`);
    set((state) => ({
      parties: state.parties.filter((p) => p.id !== id),
    }));
  },
}));
