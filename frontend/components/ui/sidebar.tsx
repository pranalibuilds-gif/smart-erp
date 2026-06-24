"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  FileText,
  Receipt,
  Users,
  BarChart3,
  Package,
  Settings,
  Building2,
  History,
  ArrowUpRight,
  Landmark,
  ShieldCheck,
  ChevronRight,
  PieChart,
  LogOut
} from "lucide-react";
import { useAuthStore } from "@/stores/auth-store";

const menuItems = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Billing", href: "/invoices", icon: FileText },
  { name: "Vouchers", href: "/vouchers", icon: Receipt },
  { name: "Parties", href: "/parties", icon: Users },
  { name: "Banking", href: "/banking", icon: Landmark },
  { name: "Inventory", href: "/reports/stock-summary", icon: Package },
];

const reportItems = [
  { name: "Trial Balance", href: "/reports/trial-balance" },
  { name: "Profit & Loss", href: "/reports/profit-loss" },
  { name: "Balance Sheet", href: "/reports/balance-sheet" },
];

export function Sidebar() {
  const pathname = usePathname();
  const logout = useAuthStore(state => state.logout);
  const user = useAuthStore(state => state.user);

  return (
    <div className="w-64 bg-[#0f172a] text-slate-300 flex flex-col h-screen sticky top-0 border-r border-slate-800 shadow-2xl">
      <div className="p-7 mb-4 flex items-center gap-3 border-b border-slate-800/50">
        <div className="bg-blue-600 p-2 rounded-xl shadow-lg shadow-blue-500/20">
          <Building2 className="h-6 w-6 text-white" />
        </div>
        <span className="font-black text-2xl tracking-tighter text-white">SmartERP</span>
      </div>

      <nav className="flex-1 px-4 space-y-7 overflow-y-auto pb-8 pt-2">
        <div>
           <p className="px-3 mb-4 text-[10px] font-black text-slate-500 uppercase tracking-[0.25em]">CORE ENGINE</p>
           <div className="space-y-1.5">
            {menuItems.map((item) => {
              const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "flex items-center justify-between group px-3 py-2.5 rounded-xl text-sm font-bold transition-all duration-200",
                    isActive
                      ? "bg-blue-600 text-white shadow-lg shadow-blue-600/30 scale-[1.02]"
                      : "hover:bg-slate-800/50 hover:text-white"
                  )}
                >
                  <div className="flex items-center gap-3">
                    <item.icon className={cn("h-4.5 w-4.5", isActive ? "text-white" : "text-slate-500 group-hover:text-blue-400")} />
                    {item.name}
                  </div>
                  {isActive && <div className="w-1.5 h-1.5 rounded-full bg-white shadow-[0_0_8px_white]" />}
                </Link>
              );
            })}
           </div>
        </div>

        <div>
           <p className="px-3 mb-4 text-[10px] font-black text-slate-500 uppercase tracking-[0.25em]">FINANCIAL STATEMENTS</p>
           <div className="space-y-1">
             {reportItems.map(item => (
               <Link
                 key={item.href}
                 href={item.href}
                 className={cn(
                   "flex items-center gap-3 px-3 py-2 text-slate-400 hover:text-white hover:bg-slate-800/50 rounded-lg text-sm font-semibold transition-all",
                   pathname === item.href && "text-blue-400 font-bold"
                 )}
               >
                 <div className={cn("w-1.5 h-1.5 rounded-full", pathname === item.href ? "bg-blue-400 shadow-[0_0_8px_#60a5fa]" : "bg-slate-700")} /> {item.name}
               </Link>
             ))}
           </div>
        </div>

        <div>
           <p className="px-3 mb-4 text-[10px] font-black text-slate-500 uppercase tracking-[0.25em]">ADMINISTRATION</p>
           <div className="space-y-1.5">
             <Link href="/settings/company" className={cn("flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-bold transition-all", pathname === "/settings/company" ? "bg-slate-800 text-white" : "hover:bg-slate-800/50")}>
               <Building2 className="h-4.5 w-4.5 text-slate-500" /> Company Profile
             </Link>
             <Link href="/settings/profile" className={cn("flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-bold transition-all", pathname === "/settings/profile" ? "bg-slate-800 text-white" : "hover:bg-slate-800/50")}>
               <Users className="h-4.5 w-4.5 text-slate-500" /> User Profile
             </Link>
             <Link href="/activity" className={cn("flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-bold transition-all", pathname === "/activity" ? "bg-slate-800 text-white" : "hover:bg-slate-800/50")}>
               <History className="h-4.5 w-4.5 text-slate-500" /> Activity Center
             </Link>
             <Link href="/settings/team" className={cn("flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-bold transition-all", pathname === "/settings/team" ? "bg-slate-800 text-white" : "hover:bg-slate-800/50")}>
               <ShieldCheck className="h-4.5 w-4.5 text-slate-500" /> User Access
             </Link>
             <Link href="/settings/financial-years" className={cn("flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-bold transition-all", pathname === "/settings/financial-years" ? "bg-slate-800 text-white" : "hover:bg-slate-800/50")}>
               <Settings className="h-4.5 w-4.5 text-slate-500" /> FY Closing
             </Link>
           </div>
        </div>
      </nav>

      <div className="p-4 border-t border-slate-800/50 bg-[#0f172a]">
         <div className="flex items-center gap-3 p-3 rounded-2xl bg-slate-800/30 border border-slate-800/50 group cursor-default">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center font-black text-sm text-white shadow-inner">
               {user?.full_name?.substring(0, 2).toUpperCase() || "JD"}
            </div>
            <div className="flex-1 min-w-0">
               <p className="text-sm font-black truncate text-white tracking-tight">{user?.full_name || "Admin User"}</p>
               <p className="text-[10px] text-slate-500 truncate font-bold uppercase tracking-wider">{user?.email?.split('@')[0] || "portal-admin"}</p>
            </div>
            <button
              onClick={logout}
              className="p-1.5 text-slate-500 hover:text-rose-500 transition-colors"
            >
              <LogOut className="h-4 w-4" />
            </button>
         </div>
      </div>
    </div>
  );
}
