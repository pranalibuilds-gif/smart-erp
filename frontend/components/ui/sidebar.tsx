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
  Building2
  History,
} from "lucide-react";

const menuItems = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Invoices", href: "/invoices", icon: FileText },
  { name: "Vouchers", href: "/vouchers", icon: Receipt },
  { name: "Parties", href: "/parties", icon: Users },
  { name: "Stock Adjust", href: "/inventory/adjustments", icon: Settings },
  { name: "Stock Transfer", href: "/inventory/transfers", icon: ArrowUpRight },
  { name: "Activity", href: "/activity", icon: History },
  { name: "Stock Summary", href: "/reports/stock-summary", icon: Package },
  { name: "Trial Balance", href: "/reports/trial-balance", icon: BarChart3 },
  { name: "Settings", href: "/settings/financial-years", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="w-64 bg-slate-900 text-white flex flex-col min-h-screen">
      <div className="p-6 border-b border-slate-800 flex items-center gap-3">
        <Building2 className="text-blue-400" />
        <span className="font-bold text-xl tracking-tight">SmartERP</span>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        {menuItems.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
                isActive
                  ? "bg-blue-600 text-white"
                  : "text-slate-300 hover:bg-slate-800 hover:text-white"
              )}
            >
              <item.icon className="h-4 w-4" />
              {item.name}
            </Link>
          );
        })}

        <div className="pt-4 mt-4 border-t border-slate-800">
           <p className="px-3 mb-2 text-xs font-semibold text-slate-500 uppercase tracking-wider">Financials</p>
           <Link href="/reports/profit-loss" className="flex items-center gap-3 px-3 py-2 text-slate-300 hover:bg-slate-800 hover:text-white rounded-md text-sm font-medium">Profit & Loss</Link>
           <Link href="/reports/balance-sheet" className="flex items-center gap-3 px-3 py-2 text-slate-300 hover:bg-slate-800 hover:text-white rounded-md text-sm font-medium">Balance Sheet</Link>
        </div>
      </nav>
    </div>
  );
}
