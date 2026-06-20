import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import { User } from "@/features/auth/types";
import { login as loginApi } from "@/features/auth/api/login";
import { register as registerApi } from "@/features/auth/api/register";
import { refresh as refreshApi } from "@/features/auth/api/refresh";
import { logout as logoutApi } from "@/features/auth/api/logout";
import { LoginCredentials, RegisterData } from "@/features/auth/schemas";

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null; // We need this to refresh
  isAuthenticated: boolean;

  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  refreshSession: () => Promise<void>;
  setAuth: (user: User, accessToken: string, refreshToken: string) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,

      setAuth: (user, accessToken, refreshToken) =>
        set({ user, accessToken, refreshToken, isAuthenticated: true }),

      login: async (credentials) => {
        const data = await loginApi(credentials);
        set({
          user: data.user,
          accessToken: data.access_token,
          refreshToken: data.refresh_token,
          isAuthenticated: true,
        });
      },

      register: async (data) => {
        const response = await registerApi(data);
        set({
          user: response.user,
          accessToken: response.access_token,
          refreshToken: response.refresh_token,
          isAuthenticated: true,
        });
      },

      logout: async () => {
        const { refreshToken } = get();
        if (refreshToken) {
          try {
            await logoutApi(refreshToken);
          } catch (error) {
            console.error("Logout API failed", error);
          }
        }
        set({ user: null, accessToken: null, refreshToken: null, isAuthenticated: false });
      },

      refreshSession: async () => {
        const { refreshToken } = get();
        if (!refreshToken) throw new Error("No refresh token");

        try {
          const data = await refreshApi(refreshToken);
          set({
            user: data.user,
            accessToken: data.access_token,
            refreshToken: data.refresh_token,
            isAuthenticated: true,
          });
        } catch (error) {
          set({ user: null, accessToken: null, refreshToken: null, isAuthenticated: false });
          throw error;
        }
      },
    }),
    {
      name: "auth-storage",
      storage: createJSONStorage(() => localStorage),
    }
  )
);
