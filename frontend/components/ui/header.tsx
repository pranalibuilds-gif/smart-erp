"use client";

import { Bell } from "lucide-react";
import { useNotificationStore } from "@/stores/notification-store";
import { useEffect, useState } from "react";
import { Badge } from "./badge";
import { Button } from "./button";
import { formatDistanceToNow } from "date-fns";
import { cn } from "@/lib/utils";

export function Header() {
  const { notifications, unreadCount, fetchNotifications, readOne, readAll } = useNotificationStore();
  const [showDropdown, setShowDropdown] = useState(false);

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 60000); // Polling every minute
    return () => clearInterval(interval);
  }, [fetchNotifications]);

  return (
    <header className="h-16 border-b bg-white flex items-center justify-end px-8 relative">
      <div className="relative">
        <Button variant="ghost" size="icon" onClick={() => setShowDropdown(!showDropdown)}>
          <Bell className="h-5 w-5" />
          {unreadCount > 0 && (
            <Badge className="absolute -top-1 -right-1 px-1.5 py-0.5 min-w-[20px] h-[20px] flex items-center justify-center bg-red-500 hover:bg-red-600">
              {unreadCount}
            </Badge>
          )}
        </Button>

        {showDropdown && (
          <div className="absolute right-0 mt-2 w-80 bg-white border rounded-lg shadow-xl z-50 overflow-hidden">
            <div className="p-4 border-b flex justify-between items-center bg-gray-50">
               <h3 className="font-bold text-sm">Notifications</h3>
               <button className="text-xs text-blue-600 hover:underline" onClick={() => readAll()}>Mark all as read</button>
            </div>
            <div className="max-h-96 overflow-y-auto">
               {notifications.length === 0 ? (
                  <div className="p-8 text-center text-gray-400 text-sm">No notifications</div>
               ) : (
                  notifications.map(n => (
                    <div
                      key={n.id}
                      className={cn(
                        "p-4 border-b last:border-0 hover:bg-gray-50 cursor-pointer transition-colors",
                        !n.is_read && "bg-blue-50/50"
                      )}
                      onClick={() => !n.is_read && readOne(n.id)}
                    >
                       <p className="text-sm font-bold">{n.title}</p>
                       <p className="text-xs text-gray-600 mt-1">{n.message}</p>
                       <p className="text-[10px] text-gray-400 mt-2 italic">{formatDistanceToNow(new Date(n.created_at), { addSuffix: true })}</p>
                    </div>
                  ))
               )}
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
