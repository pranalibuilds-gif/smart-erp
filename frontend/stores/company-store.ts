import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import apiClient from "@/lib/api-client";

export interface Company {
  id: string;
  name: string;
  legal_name: string;
  slug: string;
  email?: string;
  phone?: string;
  address?: string;
  state?: string;
  country: string;
}

export interface FinancialYear {
  id: string;
  name: string;
  start_date: string;
  end_date: string;
  is_closed: boolean;
}

interface CompanyState {
  activeCompany: Company | null;
  activeFY: FinancialYear | null;
  companies: Company[];
  isLoading: boolean;

  fetchCompanies: () => Promise<void>;
  setActiveCompany: (company: Company) => void;
  setActiveFY: (fy: FinancialYear) => void;
  createCompany: (data: any) => Promise<Company>;
  updateCompany: (id: string, data: any) => Promise<Company>;
}

export const useCompanyStore = create<CompanyState>()(
  persist(
    (set, get) => ({
      activeCompany: null,
      activeFY: null,
      companies: [],
      isLoading: false,

      fetchCompanies: async () => {
        set({ isLoading: true });
        try {
          const response = await apiClient.get("/api/v1/companies");
          set({ companies: response.data.data, isLoading: false });
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      setActiveCompany: (company: Company) => {
        set({ activeCompany: company });
      },

      setActiveFY: (fy: FinancialYear) => {
        set({ activeFY: fy });
      },

      createCompany: async (data: any) => {
        set({ isLoading: true });
        try {
          const response = await apiClient.post("/api/v1/companies", data);
          const newCompany = response.data.data;
          set((state) => ({
            companies: [...state.companies, newCompany],
            isLoading: false
          }));
          return newCompany;
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      updateCompany: async (id: string, data: any) => {
        set({ isLoading: true });
        try {
          const response = await apiClient.put(`/api/v1/companies/${id}`, data);
          const updated = response.data.data;
          set((state) => ({
            companies: state.companies.map(c => c.id === id ? updated : c),
            activeCompany: state.activeCompany?.id === id ? updated : state.activeCompany,
            isLoading: false
          }));
          return updated;
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },
    }),
    {
      name: "company-storage",
      storage: createJSONStorage(() => localStorage),
    }
  )
);
