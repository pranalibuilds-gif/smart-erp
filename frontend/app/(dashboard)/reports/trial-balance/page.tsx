"use client";

import { useEffect, useState } from "react";
import { getTrialBalance } from "@/features/reports/api/reports-api";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Download, FileSpreadsheet, Printer, ChevronRight, BarChart3, Search, Filter, AlertCircle, CheckCircle2, TrendingUp, RefreshCw, AlertTriangle } from "lucide-react";
import Link from "next/link";
import apiClient from "@/lib/api-client";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";

export default function TrialBalancePage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await getTrialBalance();
      setData(result);
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Failed to generate statement protocol");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) return (
    <div className="p-10 flex flex-col items-center justify-center h-[70vh] gap-6 text-slate-300 animate-pulse">
       <BarChart3 className="h-16 w-16 text-slate-200" />
       <p className="font-black uppercase tracking-[0.3em] text-xs">Generating Ledger Summary...</p>
    </div>
  );

  if (error || !data) return (
    <div className="p-10 flex flex-col items-center justify-center h-[70vh] gap-6">
       <div className="bg-rose-50 p-6 rounded-[32px] border border-rose-100 flex flex-col items-center gap-4 text-center max-w-md shadow-2xl shadow-rose-900/5">
          <div className="bg-rose-600 h-16 w-16 rounded-2xl flex items-center justify-center text-white shadow-lg shadow-rose-600/30 ring-8 ring-rose-50">
             <AlertCircle className="h-8 w-8" />
          </div>
          <div className="space-y-1">
             <h3 className="text-xl font-black text-rose-900 uppercase">Analysis Interrupted</h3>
             <p className="text-sm font-bold text-rose-600 uppercase tracking-tighter italic">{error || "Data set returned empty or invalid"}</p>
          </div>
          <Button onClick={fetchData} className="mt-4 bg-rose-600 hover:bg-rose-700 h-12 px-8 rounded-xl font-black uppercase tracking-widest shadow-xl shadow-rose-600/20">
             <RefreshCw className="mr-2 h-4 w-4" /> Retry Engine
          </Button>
       </div>
    </div>
  );

  return (
    <div className="p-10 max-w-[1500px] mx-auto space-y-8 pb-32 animate-in fade-in duration-1000">
      <div className="flex justify-between items-center mb-10">
        <div className="flex items-center gap-6">
           <div className="bg-slate-900 p-4 rounded-[22px] shadow-2xl shadow-slate-900/20 text-white ring-8 ring-slate-100">
              <BarChart3 className="h-8 w-8" />
           </div>
           <div>
              <h1 className="text-3xl font-black tracking-tight text-slate-900 uppercase italic">Chart of Accounts / Trial Balance</h1>
              <p className="text-slate-500 font-medium mt-1 uppercase text-[10px] tracking-widest flex items-center gap-2">
                 <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                 Operational Position as of {new Date().toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })}
              </p>
           </div>
        </div>
        <div className="flex gap-3">
           <Button variant="ghost" size="icon" className="h-12 w-12 rounded-2xl border border-slate-200 shadow-sm hover:text-blue-600 transition-all"><Search className="h-5 w-5" /></Button>
           <Button variant="ghost" size="icon" className="h-12 w-12 rounded-2xl border border-slate-200 shadow-sm hover:text-blue-600 transition-all"><Filter className="h-5 w-5" /></Button>
           <Button variant="ghost" size="icon" className="h-12 w-12 rounded-2xl border border-slate-200 shadow-sm hover:text-blue-600 transition-all"><Printer className="h-5 w-5" /></Button>
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-[40px] shadow-[0_30px_80px_rgba(0,0,0,0.02)] overflow-hidden ring-1 ring-slate-200/60">
        <Table>
          <TableHeader className="bg-slate-50/50">
            <TableRow className="hover:bg-transparent border-b border-slate-100">
              <TableHead className="font-black text-slate-500 uppercase tracking-widest py-8 px-12 text-[10px] w-1/2 italic">Account / Ledger Context</TableHead>
              <TableHead className="font-black text-slate-500 uppercase tracking-widest text-[10px] text-right px-10">Debit Ledger (₹)</TableHead>
              <TableHead className="font-black text-slate-500 uppercase tracking-widest text-[10px] text-right px-10">Credit Ledger (₹)</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.items.map((item: any) => (
              <TableRow key={item.ledger_id} className="hover:bg-slate-50/80 transition-all border-b border-slate-50 last:border-0 h-20 group">
                <TableCell className="px-12">
                   <div className="flex items-center gap-4">
                      <div className="w-1.5 h-8 bg-slate-100 rounded-full group-hover:bg-blue-500 transition-all duration-500" />
                      <span className="font-black text-slate-700 uppercase tracking-tight text-sm group-hover:text-blue-600 transition-colors">
                        {item.ledger_name}
                      </span>
                   </div>
                </TableCell>
                <TableCell className="text-right px-10 font-mono font-black text-slate-900 tracking-tight text-lg">
                  {item.closing_balance > 0 ? item.closing_balance.toLocaleString('en-IN', { minimumFractionDigits: 2 }) : "—"}
                </TableCell>
                <TableCell className="text-right px-10 font-mono font-black text-slate-900 tracking-tight text-lg">
                  {item.closing_balance < 0 ? Math.abs(item.closing_balance).toLocaleString('en-IN', { minimumFractionDigits: 2 }) : "—"}
                </TableCell>
              </TableRow>
            ))}

            <TableRow className="bg-slate-900 text-white font-black shadow-2xl relative z-10 h-28 border-t-8 border-blue-600">
              <TableCell className="px-12 uppercase tracking-[0.4em] text-[11px] italic text-blue-400">Ledger Distribution Aggregation</TableCell>
              <TableCell className="text-right px-10 font-mono text-3xl tracking-tighter italic">₹{data.total_debit.toLocaleString()}</TableCell>
              <TableCell className="text-right px-10 font-mono text-3xl tracking-tighter italic">₹{data.total_credit.toLocaleString()}</TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </div>

      <div className={cn(
        "mt-10 p-10 rounded-[40px] border-4 flex flex-col md:flex-row items-center justify-between gap-8 font-black transition-all animate-in slide-in-from-bottom-4 duration-1000 group shadow-2xl",
        data.is_balanced
          ? "bg-emerald-600 border-emerald-400 text-white shadow-emerald-500/20 ring-[12px] ring-emerald-500/5"
          : "bg-rose-600 border-rose-400 text-white shadow-rose-500/20 ring-[12px] ring-rose-500/5"
      )}>
         <div className="flex items-center gap-6">
            <div className="h-16 w-16 rounded-[24px] bg-white/10 flex items-center justify-center border border-white/20 shadow-inner group-hover:scale-110 transition-transform duration-500">
               {data.is_balanced ? <CheckCircle2 className="h-8 w-8 text-white" /> : <AlertTriangle className="h-8 w-8 text-white animate-bounce" />}
            </div>
            <div>
               <h3 className="text-2xl font-black tracking-tighter uppercase italic">{data.is_balanced ? "Equation Verified" : "Discrepancy Protocol"}</h3>
               <p className="text-xs font-bold uppercase tracking-widest opacity-70 mt-1">{data.is_balanced ? "All ledger entries successfully validated against double-entry standards" : "Sum of debits does not equal credits. Manual review required."}</p>
            </div>
         </div>
         <div className="flex items-center gap-10 border-l border-white/20 pl-10">
            <div className="text-right">
               <p className="text-[10px] font-black uppercase tracking-widest opacity-50 mb-1">Variance Factor</p>
               <p className="text-2xl font-black font-mono tracking-tighter italic">₹{Math.abs(data.total_debit - data.total_credit).toLocaleString()}</p>
            </div>
            <TrendingUp className="h-8 w-8 opacity-20" />
         </div>
      </div>
    </div>
  );
}

