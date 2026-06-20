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

interface CompanyState {
  activeCompany: Company | null;
  companies: Company[];
  isLoading: boolean;

  fetchCompanies: () => Promise<void>;
  setActiveCompany: (company: Company) => void;
  createCompany: (data: any) => Promise<Company>;
}

export const useCompanyStore = create<CompanyState>()(
  persist(
    (set, get) => ({
      activeCompany: null,
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
    }),
    {
      name: "company-storage",
      storage: createJSONStorage(() => localStorage),
    }
  )
);
