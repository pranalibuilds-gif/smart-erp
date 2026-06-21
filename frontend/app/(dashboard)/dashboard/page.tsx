"use client";

import { useAuthStore } from "@/stores/auth-store";
import { useCompanyStore } from "@/stores/company-store";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { getDashboardMetrics } from "@/features/reports/api/reports-api";
import { ShoppingCart, ShoppingBag, ArrowUpRight, Package } from "lucide-react";
import Link from "next/link";

export default function DashboardPage() {
  const { user, logout } = useAuthStore();
  const { activeCompany, activeFY } = useCompanyStore();
  const router = useRouter();
  const [metrics, setMetrics] = useState<any>(null);

  useEffect(() => {
    if (activeCompany && activeFY) {
      getDashboardMetrics().then(setMetrics).catch(console.error);
    }
  }, [activeCompany, activeFY]);

  const handleSwitchCompany = () => {
    useCompanyStore.setState({ activeCompany: null, activeFY: null });
    router.push("/company/select");
  };

  return (
    <div className="p-8">
      <div className="flex justify-between items-start mb-8">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-gray-500">
            {activeCompany?.name} | <span className="font-semibold">{activeFY?.name}</span>
          </p>
        </div>
        <div className="space-x-2">
          <Button variant="outline" onClick={handleSwitchCompany}>Switch Company</Button>
          <Button variant="destructive" onClick={() => {
            logout();
            useCompanyStore.setState({ activeCompany: null, activeFY: null });
          }}>Logout</Button>
        </div>
      </div>

      {metrics ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-500">Total Sales</CardTitle>
              <ShoppingCart className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold font-mono">₹{metrics.total_sales.toFixed(2)}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-500">Total Purchases</CardTitle>
              <ShoppingBag className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold font-mono">₹{metrics.total_purchases.toFixed(2)}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-500">Total Receivables</CardTitle>
              <ArrowUpRight className="h-4 w-4 text-orange-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold font-mono">₹{metrics.total_receivables.toFixed(2)}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-500">Inventory Value</CardTitle>
              <Package className="h-4 w-4 text-purple-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold font-mono">₹{metrics.inventory_value.toFixed(2)}</div>
            </CardContent>
          </Card>
        </div>
      ) : (
        <div className="py-12 text-center text-gray-400">Loading metrics...</div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <Card>
           <CardHeader><CardTitle>Reports</CardTitle></CardHeader>
           <CardContent className="grid grid-cols-2 gap-2">
              <Button variant="link" className="p-0 h-auto justify-start" asChild><Link href="/reports/trial-balance">Trial Balance →</Link></Button>
              <Button variant="link" className="p-0 h-auto justify-start" asChild><Link href="/reports/profit-loss">Profit & Loss →</Link></Button>
              <Button variant="link" className="p-0 h-auto justify-start" asChild><Link href="/reports/balance-sheet">Balance Sheet →</Link></Button>
              <Button variant="link" className="p-0 h-auto justify-start" asChild><Link href="/reports/stock-summary">Stock Summary →</Link></Button>
              <Button variant="link" className="p-0 h-auto justify-start" asChild><Link href="/reports/stock-by-warehouse">Stock By Warehouse →</Link></Button>
              <Button variant="link" className="p-0 h-auto justify-start" asChild><Link href="/banking">Banking & Payments →</Link></Button>
           </CardContent>
        </Card>
        <Card>
           <CardHeader><CardTitle>Quick Links</CardTitle></CardHeader>
           <CardContent className="space-y-2">
              <Button variant="link" className="p-0 block h-auto justify-start" asChild><Link href="/invoices/new">Create Invoice →</Link></Button>
              <Button variant="link" className="p-0 block h-auto justify-start" asChild><Link href="/vouchers">View Vouchers →</Link></Button>
           </CardContent>
        </Card>
      </div>
    </div>
  );
}
