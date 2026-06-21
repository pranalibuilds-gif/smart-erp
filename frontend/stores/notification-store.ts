import { create } from "zustand";
import { getNotifications, markAsRead, markAllAsRead, Notification } from "@/features/notifications/api/notification-api";

interface NotificationState {
  notifications: Notification[];
  unreadCount: number;
  isLoading: boolean;

  fetchNotifications: () => Promise<void>;
  readOne: (id: string) => Promise<void>;
  readAll: () => Promise<void>;
}

export const useNotificationStore = create<NotificationState>((set, get) => ({
  notifications: [],
  unreadCount: 0,
  isLoading: false,

  fetchNotifications: async () => {
    set({ isLoading: true });
    try {
      const data = await getNotifications();
      set({
        notifications: data,
        unreadCount: data.filter(n => !n.is_read).length,
        isLoading: false
      });
    } catch (error) {
      set({ isLoading: false });
    }
  },

  readOne: async (id: string) => {
    await markAsRead(id);
    const { notifications } = get();
    const updated = notifications.map(n => n.id === id ? { ...n, is_read: true } : n);
    set({
      notifications: updated,
      unreadCount: updated.filter(n => !n.is_read).length
    });
  },

  readAll: async () => {
    await markAllAsRead();
    const { notifications } = get();
    const updated = notifications.map(n => ({ ...n, is_read: true }));
    set({
      notifications: updated,
      unreadCount: 0
    });
  }
}));
