import { create } from "zustand";
import { persist } from "zustand/middleware";

interface CompanyState {
  activeCompanyId: string | null;
  activeFinancialYearId: string | null;
  setActiveCompany: (id: string) => void;
  setActiveFinancialYear: (id: string) => void;
}

export const useCompanyStore = create<CompanyState>()(
  persist(
    (set) => ({
      activeCompanyId: null,
      activeFinancialYearId: null,
      setActiveCompany: (id) => set({ activeCompanyId: id }),
      setActiveFinancialYear: (id) => set({ activeFinancialYearId: id }),
    }),
    {
      name: "company-storage",
    }
  )
);
