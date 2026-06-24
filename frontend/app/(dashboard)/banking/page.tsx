"use client";

import { useEffect, useState } from "react";
import { listBankAccounts, BankAccount } from "@/features/banking/api/banking-api";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { Plus, Landmark, History, CheckCircle2, CreditCard, ArrowRightLeft, Globe } from "lucide-react";
import Link from "next/link";
import { Badge } from "@/components/ui/badge";

export default function BankingDashboardPage() {
  const [accounts, setAccounts] = useState<BankAccount[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listBankAccounts()
      .then(setAccounts)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 pb-20">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div className="flex items-center gap-4">
           <div className="bg-slate-900 p-3 rounded-2xl shadow-lg shadow-slate-900/20 text-white">
              <Landmark className="h-6 w-6" />
           </div>
           <div>
              <h1 className="text-3xl font-bold tracking-tight text-slate-900">Banking & Liquidity</h1>
              <p className="text-slate-500 mt-1">Manage corporate bank accounts and inter-account reconciliations</p>
           </div>
        </div>
        <div className="flex gap-3">
          <Link href="/banking/reconciliation" className={cn(buttonVariants({ variant: "outline" }), "bg-white border-slate-200")}>
            <CheckCircle2 className="mr-2 h-4 w-4" /> Reconciliation
          </Link>
          <Link href="/banking/receipts/new" className={cn(buttonVariants(), "bg-blue-600 hover:bg-blue-700 shadow-lg shadow-blue-600/20 px-6 font-bold")}>
            <Plus className="mr-2 h-4 w-4" /> New Receipt
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {loading ? (
          [1, 2, 3].map(i => <Card key={i} className="h-48 animate-pulse bg-slate-50 border-none" />)
        ) : accounts.map((acc) => (
          <Card key={acc.id} className="group border-none shadow-sm ring-1 ring-slate-200 hover:ring-blue-500 hover:shadow-xl transition-all duration-300 overflow-hidden">
            <CardHeader className="bg-slate-50/50 border-b flex flex-row items-center justify-between py-4">
               <Badge variant="outline" className="bg-white text-slate-500 border-slate-200 font-bold text-[10px] tracking-widest">{acc.account_type}</Badge>
               <Landmark className="h-4 w-4 text-slate-300 group-hover:text-blue-500 transition-colors" />
            </CardHeader>
            <CardContent className="pt-6">
               <div className="flex justify-between items-start">
                  <div>
                    <h3 className="text-xl font-black text-slate-900">{acc.account_name}</h3>
                    <p className="text-xs font-mono text-slate-400 mt-1 uppercase tracking-tighter">No: •••• {acc.account_number.slice(-4)}</p>
                  </div>
                  <div className="text-right">
                     <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1">Available Balance</p>
                     <p className="text-xl font-bold text-slate-900 font-mono">₹{acc.current_balance.toLocaleString()}</p>
                  </div>
               </div>

               <div className="mt-8 flex gap-2">
                  <Link href={`/banking/reconciliation?account_id=${acc.id}`} className={cn(buttonVariants({variant: 'ghost', size: 'sm'}), "flex-1 text-[10px] font-bold uppercase tracking-widest border border-slate-100 hover:bg-blue-50 hover:text-blue-600 transition-all")}>
                    Statements
                  </Link>
                  <Link href={`/banking/payments/new?account_id=${acc.id}`} className={cn(buttonVariants({variant: 'ghost', size: 'sm'}), "flex-1 text-[10px] font-bold uppercase tracking-widest border border-slate-100 hover:bg-blue-50 hover:text-blue-600 transition-all")}>
                    Post Payment
                  </Link>
               </div>
            </CardContent>
          </Card>
        ))}

        <Link href="/banking/new" className="group flex flex-col items-center justify-center h-full min-h-[220px] rounded-2xl border-2 border-dashed border-slate-200 bg-slate-50/50 hover:bg-white hover:border-blue-500 hover:shadow-lg transition-all duration-300">
           <div className="bg-white p-4 rounded-full shadow-sm group-hover:bg-blue-600 group-hover:text-white transition-all">
              <Plus className="h-6 w-6 text-slate-400 group-hover:text-white" />
           </div>
           <p className="mt-4 text-sm font-bold text-slate-500 group-hover:text-blue-600">Connect New Account</p>
        </Link>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
         <Card className="border-none shadow-sm ring-1 ring-slate-200 overflow-hidden">
            <CardHeader className="bg-slate-50/50 border-b flex flex-row items-center justify-between">
               <CardTitle className="text-sm font-bold uppercase tracking-widest flex items-center gap-2 text-slate-600">
                  <ArrowRightLeft className="h-4 w-4 text-blue-600" /> Recent Transfers
               </CardTitle>
               <Link href="/banking/transfers" className="text-[10px] font-bold text-blue-600 uppercase hover:underline">View History</Link>
            </CardHeader>
            <CardContent className="p-0">
               <div className="p-8 text-center flex flex-col items-center gap-3 opacity-20">
                  <Globe className="h-10 w-10" />
                  <p className="text-xs font-bold uppercase tracking-widest">No Recent Internal Movements</p>
               </div>
            </CardContent>
         </Card>

         <Card className="border-none shadow-sm ring-1 ring-slate-200 overflow-hidden">
            <CardHeader className="bg-slate-50/50 border-b flex flex-row items-center justify-between">
               <CardTitle className="text-sm font-bold uppercase tracking-widest flex items-center gap-2 text-slate-600">
                  <CreditCard className="h-4 w-4 text-orange-600" /> Payment Queues
               </CardTitle>
               <span className="bg-orange-100 text-orange-700 text-[10px] font-black px-2 py-0.5 rounded-full">3 PENDING</span>
            </CardHeader>
            <CardContent className="p-0 divide-y divide-slate-100">
               {[1, 2].map(i => (
                 <div key={i} className="p-4 flex items-center justify-between hover:bg-slate-50 transition-colors">
                    <div className="flex items-center gap-3">
                       <div className="h-10 w-10 rounded-lg bg-blue-50 flex items-center justify-center text-blue-600 font-black text-xs">TX</div>
                       <div>
                          <p className="text-sm font-bold text-slate-900">Vendor Payment #00{i}</p>
                          <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest">Target: Apex Solutions</p>
                       </div>
                    </div>
                    <p className="text-sm font-black font-mono text-slate-700">₹{ (i*5000).toLocaleString() }</p>
                 </div>
               ))}
            </CardContent>
         </Card>
      </div>
    </div>
  );
}
