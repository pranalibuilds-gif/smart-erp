"use client";

import { useEffect, useState } from "react";
import { useAuthStore } from "@/stores/auth-store";

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated, refreshSession } = useAuthStore();
  const [isHydrated, setIsHydrated] = useState(false);

  // Handle store hydration
  useEffect(() => {
    // This effect ensures we only run auth checks after Zustand has rehydrated from localStorage
    const unsub = useAuthStore.persist.onFinishHydration(() => {
      setIsHydrated(true);
    });

    // If already hydrated (e.g. during client-side navigation)
    if (useAuthStore.persist.hasHydrated()) {
      setIsHydrated(true);
    }

    return () => unsub();
  }, []);

  // Attempt to refresh session on mount if authenticated
  useEffect(() => {
    if (isHydrated && isAuthenticated) {
      refreshSession().catch(() => {
        console.log("Session recovery failed, user must log in again.");
      });
    }
  }, [isHydrated, isAuthenticated, refreshSession]);

  if (!isHydrated) {
    return null; // Or a loading spinner
  }

  return <>{children}</>;
};
