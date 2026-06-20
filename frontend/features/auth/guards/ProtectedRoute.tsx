"use client";

import { useAuthStore } from "@/stores/auth-store";
import { useCompanyStore } from "@/stores/company-store";
import { useRouter, usePathname } from "next/navigation";
import { useEffect } from "react";

export const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated } = useAuthStore();
  const { activeCompany } = useCompanyStore();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!isAuthenticated) {
      router.replace("/login");
    } else if (!activeCompany && !pathname.startsWith("/company")) {
      // If logged in but no company selected, and not already on a company setup page
      router.replace("/company/select");
    }
  }, [isAuthenticated, activeCompany, router, pathname]);

  if (!isAuthenticated) {
    return null;
  }

  // If we are redirected to company select, don't show the protected content yet
  if (!activeCompany && !pathname.startsWith("/company")) {
    return null;
  }

  return <>{children}</>;
};
