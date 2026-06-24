"use client";

import { Bell, Search, Settings, HelpCircle, Menu, User, Command } from "lucide-react";
import { useNotificationStore } from "@/stores/notification-store";
import { useEffect, useState } from "react";
import { Badge } from "./badge";
import { Button, buttonVariants } from "./button";
import { formatDistanceToNow } from "date-fns";
import { cn } from "@/lib/utils";
import { useCompanyStore } from "@/stores/company-store";
import Link from "next/link";

export function Header() {
  const { notifications, unreadCount, fetchNotifications, readOne, readAll } = useNotificationStore();
  const { activeCompany, activeFY } = useCompanyStore();
  const [showDropdown, setShowDropdown] = useState(false);

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 60000);
    return () => clearInterval(interval);
  }, [fetchNotifications]);

  return (
    <header className="h-[72px] border-b bg-white flex items-center justify-between px-8 sticky top-0 z-30 shadow-sm shadow-slate-100">
      <div className="flex items-center gap-8 flex-1">
        <Button variant="ghost" size="icon" className="lg:hidden">
          <Menu className="h-5 w-5" />
        </Button>

        <div
          className="hidden md:flex items-center gap-3 px-5 py-2.5 bg-slate-50 border border-slate-200 rounded-2xl text-slate-400 text-sm cursor-pointer hover:bg-white hover:border-blue-400 hover:ring-4 hover:ring-blue-50 transition-all group flex-1 max-w-xl shadow-inner shadow-slate-100"
          onClick={() => window.dispatchEvent(new KeyboardEvent('keydown', { key: 'k', ctrlKey: true }))}
        >
          <Search className="h-4.5 w-4.5 group-hover:text-blue-500 transition-colors" />
          <span className="flex-1 font-medium">Search ledger accounts, invoices or try "New Receipt"...</span>
          <div className="flex items-center gap-1 bg-white border border-slate-200 px-2 py-1 rounded-lg shadow-sm">
             <Command className="h-3 w-3 text-slate-500" />
             <span className="text-[10px] font-black text-slate-600">K</span>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="hidden xl:flex flex-col items-end mr-6 pr-6 border-r border-slate-100">
          <div className="flex items-center gap-2">
             <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_#10b981]" />
             <span className="text-xs font-black text-slate-900 tracking-tight">{activeCompany?.name || "Select Organization"}</span>
          </div>
          <span className="text-[10px] text-slate-400 font-bold uppercase tracking-[0.1em] mt-0.5 px-2 py-0.5 bg-slate-50 rounded border border-slate-100">FY {activeFY?.name || "----"}</span>
        </div>

        <div className="flex items-center gap-1.5">
          <Button variant="ghost" size="icon" className="text-slate-400 hover:text-blue-600 hover:bg-blue-50 h-10 w-10 rounded-xl transition-all">
            <HelpCircle className="h-5 w-5" />
          </Button>

          <Link href="/settings/company" className={cn(buttonVariants({ variant: "ghost", size: "icon" }), "text-slate-400 hover:text-blue-600 hover:bg-blue-50 h-10 w-10 rounded-xl transition-all")}>
            <Settings className="h-5 w-5" />
          </Link>

          <div className="relative">
            <Button
              variant="ghost"
              size="icon"
              className={cn("text-slate-400 hover:text-blue-600 hover:bg-blue-50 h-10 w-10 rounded-xl transition-all", showDropdown && "text-blue-600 bg-blue-50")}
              onClick={() => setShowDropdown(!showDropdown)}
            >
              <Bell className="h-5 w-5" />
              {unreadCount > 0 && (
                <span className="absolute top-2.5 right-2.5 w-2 h-2 bg-rose-500 rounded-full ring-2 ring-white animate-pulse shadow-[0_0_8px_#ef4444]" />
              )}
            </Button>

            {showDropdown && (
              <div className="absolute right-0 mt-4 w-96 bg-white border border-slate-200 rounded-3xl shadow-2xl z-50 overflow-hidden ring-8 ring-slate-900/5 animate-in slide-in-from-top-4 duration-300">
                <div className="p-6 border-b flex justify-between items-center bg-slate-50/50">
                  <div>
                     <h3 className="font-black text-sm text-slate-900 uppercase tracking-wider">Alert Center</h3>
                     <p className="text-[10px] text-slate-500 font-bold uppercase mt-0.5">{unreadCount} Unread notifications</p>
                  </div>
                  <button className="text-[10px] font-black text-blue-600 hover:text-blue-700 uppercase tracking-[0.1em] px-3 py-1.5 bg-blue-50 rounded-xl" onClick={() => { readAll(); setShowDropdown(false); }}>Clear All</button>
                </div>
                <div className="max-h-[450px] overflow-y-auto">
                  {notifications.length === 0 ? (
                    <div className="p-16 text-center flex flex-col items-center gap-4">
                      <div className="bg-slate-50 p-5 rounded-3xl"><Bell className="h-8 w-8 text-slate-200" /></div>
                      <p className="text-sm text-slate-400 font-medium">All systems green! No pending alerts.</p>
                    </div>
                  ) : (
                    notifications.map(n => (
                      <div
                        key={n.id}
                        className={cn(
                          "p-5 border-b border-slate-50 last:border-0 hover:bg-slate-50/80 cursor-pointer transition-colors group relative",
                          !n.is_read && "bg-blue-50/30"
                        )}
                        onClick={() => { if(!n.is_read) readOne(n.id); setShowDropdown(false); }}
                      >
                        {!n.is_read && <div className="absolute left-0 top-0 bottom-0 w-1 bg-blue-600" />}
                        <div className="flex justify-between items-start gap-4">
                           <p className={cn("text-sm transition-colors tracking-tight", !n.is_read ? "font-black text-slate-900" : "font-medium text-slate-500 group-hover:text-slate-900")}>{n.title}</p>
                           <p className="text-[10px] text-slate-400 font-bold whitespace-nowrap">{formatDistanceToNow(new Date(n.created_at), { addSuffix: false })}</p>
                        </div>
                        <p className="text-xs text-slate-500 mt-2 line-clamp-2 leading-relaxed font-medium">{n.message}</p>
                      </div>
                    ))
                  )}
                </div>
                <div className="p-4 border-t text-center bg-slate-50/30">
                   <button className="text-[10px] font-black text-slate-400 uppercase tracking-widest hover:text-blue-600 transition-colors">See Archive</button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
