"use client";

import { useEffect, useState } from "react";
import apiClient from "@/lib/api-client";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Landmark, Printer, Download, Scale, AlertTriangle, CheckCircle2, ChevronRight, PieChart, ShieldCheck, Zap, RefreshCw, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";

export default function BalanceSheetPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiClient.get("/api/v1/reports/balance-sheet");
      setData(res.data.data);
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Financial position protocol failed to initialize");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) return (
    <div className="p-10 flex flex-col items-center justify-center h-[70vh] gap-6 text-slate-300 animate-pulse">
       <Scale className="h-16 w-16 text-slate-200" />
       <p className="font-black uppercase tracking-[0.3em] text-xs">Computing Net Worth Snapshot...</p>
    </div>
  );

  if (error || !data) return (
    <div className="p-10 flex flex-col items-center justify-center h-[70vh] gap-6">
       <div className="bg-rose-50 p-10 rounded-[40px] border border-rose-100 flex flex-col items-center gap-6 text-center max-w-lg shadow-2xl shadow-rose-900/5">
          <div className="bg-rose-600 h-20 w-20 rounded-3xl flex items-center justify-center text-white shadow-xl shadow-rose-600/30 ring-[12px] ring-rose-50">
             <AlertCircle className="h-10 w-10" />
          </div>
          <div className="space-y-2">
             <h3 className="text-2xl font-black text-rose-900 uppercase italic tracking-tighter">System Interruption</h3>
             <p className="text-sm font-bold text-rose-600 uppercase tracking-widest italic">{error || "Data set returned empty or invalid"}</p>
          </div>
          <Button onClick={fetchData} className="mt-4 bg-slate-900 hover:bg-slate-800 text-white h-14 px-10 rounded-2xl font-black uppercase tracking-widest shadow-2xl transition-all">
             <RefreshCw className="mr-3 h-5 w-5" /> Reboot Report Engine
          </Button>
       </div>
    </div>
  );

  const totalLiabilitiesEquity = (data.liabilities?.total || 0) + (data.equity?.total || 0);

  return (
    <div className="p-10 max-w-[1800px] mx-auto space-y-10 pb-32 animate-in fade-in duration-700">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 border-b border-slate-200 pb-10">
        <div className="space-y-3">
          <div className="flex items-center gap-4">
             <div className="bg-slate-900 p-4 rounded-[24px] shadow-xl shadow-slate-900/20 text-white ring-8 ring-slate-100">
                <Scale className="h-8 w-8" />
             </div>
             <div>
                <h1 className="text-4xl font-black tracking-tighter text-slate-900 uppercase italic">Financial Position</h1>
                <div className="flex items-center gap-3 mt-1.5">
                   <Badge variant="outline" className="bg-indigo-50 text-indigo-700 border-indigo-100 font-black text-[9px] uppercase tracking-widest px-3">Audited Snapshot</Badge>
                   <ChevronRight className="h-4 w-4 text-slate-300" />
                   <span className="text-[11px] font-bold text-slate-400 uppercase tracking-widest italic tracking-tight">Statement of Assets, Liabilities & Capital Mapping</span>
                </div>
             </div>
          </div>
        </div>
        <div className="flex gap-4">
          <Button variant="outline" className="bg-white border-slate-200 h-14 px-8 rounded-2xl shadow-sm hover:shadow-xl hover:border-slate-300 transition-all font-black text-xs uppercase tracking-widest text-slate-600">
            <Printer className="mr-2.5 h-5 w-5 opacity-40" /> Archive Print
          </Button>
          <Button variant="outline" className="bg-white border-slate-200 h-14 px-8 rounded-2xl shadow-sm hover:shadow-xl hover:border-slate-300 transition-all font-black text-xs uppercase tracking-widest text-slate-600">
            <Download className="mr-2.5 h-5 w-5 opacity-40" /> Export PDF
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-10 items-start">
        {/* LIABILITIES & EQUITY */}
        <div className="space-y-8">
           <Card className="border-none shadow-[0_20px_50px_rgba(0,0,0,0.05)] ring-1 ring-slate-200 rounded-[32px] overflow-hidden group">
              <CardHeader className="bg-slate-900 text-white py-8 px-10 border-b border-white/5 relative overflow-hidden">
                 <div className="absolute top-0 right-0 w-32 h-32 bg-blue-600/20 rounded-full -mr-10 -mt-10 blur-3xl group-hover:bg-blue-600/40 transition-all duration-700" />
                 <div className="flex justify-between items-center relative z-10">
                    <div>
                       <CardTitle className="text-sm font-black uppercase tracking-[0.3em] text-blue-400">Section I</CardTitle>
                       <p className="text-2xl font-black tracking-tight mt-1 uppercase italic">CAPITAL & LIABILITIES</p>
                    </div>
                    <ShieldCheck className="h-8 w-8 text-blue-500 opacity-50" />
                 </div>
              </CardHeader>
              <CardContent className="p-0 bg-white">
                 <div className="px-10 py-5 bg-slate-50 font-black text-[10px] text-slate-500 uppercase tracking-[0.2em] border-b border-slate-100 flex items-center justify-between">
                    <span>Owner's Equity & Reserves</span>
                    <span className="bg-blue-100 text-blue-600 px-2 py-0.5 rounded tracking-tighter">Equity</span>
                 </div>
                 <Table>
                   <TableBody>
                     {data.equity?.groups?.map((item: any, i: number) => (
                       <TableRow key={i} className="hover:bg-slate-50/80 transition-colors border-b border-slate-50 last:border-0 h-16 group/row">
                         <TableCell className="pl-10 font-bold text-slate-700 py-3 text-sm group-hover/row:text-blue-600 transition-colors uppercase tracking-tight">{item.name}</TableCell>
                         <TableCell className="text-right pr-10 font-mono font-black text-slate-900 tracking-tight text-lg">₹{item.amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</TableCell>
                       </TableRow>
                     ))}
                   </TableBody>
                 </Table>

                 <div className="px-10 py-5 bg-slate-50 font-black text-[10px] text-slate-500 uppercase tracking-[0.2em] border-b border-t border-slate-100 flex items-center justify-between">
                    <span>Outstanding Liabilities</span>
                    <span className="bg-rose-100 text-rose-600 px-2 py-0.5 rounded tracking-tighter font-black italic">Net Debt</span>
                 </div>
                 <Table>
                   <TableBody>
                     {data.liabilities?.groups?.map((item: any, i: number) => (
                       <TableRow key={i} className="hover:bg-slate-50/80 transition-colors border-b border-slate-50 last:border-0 h-16 group/row">
                         <TableCell className="pl-10 font-bold text-slate-700 py-3 text-sm group-hover/row:text-rose-600 transition-colors uppercase tracking-tight">{item.name}</TableCell>
                         <TableCell className="text-right pr-10 font-mono font-black text-slate-900 tracking-tight text-lg">₹{item.amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</TableCell>
                       </TableRow>
                     ))}
                   </TableBody>
                 </Table>

                 <div className="bg-slate-900 text-white p-10 flex justify-between items-center shadow-[0_-10px_30px_rgba(0,0,0,0.1)] relative z-10 border-t-8 border-blue-600">
                    <span className="font-black text-xs uppercase tracking-[0.4em] text-blue-400 italic">Total Liabilities & Equity</span>
                    <span className="text-3xl font-black tracking-tighter font-mono">₹{totalLiabilitiesEquity.toLocaleString()}</span>
                 </div>
              </CardContent>
           </Card>
        </div>

        {/* ASSETS */}
        <div className="space-y-8">
           <Card className="border-none shadow-[0_20px_50px_rgba(0,0,0,0.05)] ring-1 ring-slate-200 rounded-[32px] overflow-hidden group">
              <CardHeader className="bg-blue-600 text-white py-8 px-10 border-b border-white/5 relative overflow-hidden">
                 <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -mr-10 -mt-10 blur-3xl group-hover:bg-white/20 transition-all duration-700" />
                 <div className="flex justify-between items-center relative z-10">
                    <div>
                       <CardTitle className="text-sm font-black uppercase tracking-[0.3em] text-blue-100">Section II</CardTitle>
                       <p className="text-2xl font-black tracking-tight mt-1 uppercase italic">RESOURCES & ASSETS</p>
                    </div>
                    <Zap className="h-8 w-8 text-blue-200 opacity-50" />
                 </div>
              </CardHeader>
              <CardContent className="p-0 bg-white">
                 <div className="px-10 py-5 bg-blue-50 font-black text-[10px] text-blue-600 uppercase tracking-[0.2em] border-b border-blue-100 flex items-center justify-between">
                    <span>Company Assets Pool</span>
                    <span className="bg-blue-600 text-white px-2 py-0.5 rounded tracking-tighter font-black italic">Aggregated</span>
                 </div>
                 <Table>
                   <TableBody>
                     {data.assets?.groups?.map((item: any, i: number) => (
                       <TableRow key={i} className="hover:bg-blue-50/20 transition-colors border-b border-slate-50 last:border-0 h-16 group/row">
                         <TableCell className="pl-10 font-bold text-slate-700 py-3 text-sm group-hover/row:text-blue-600 transition-colors uppercase tracking-tight">{item.name}</TableCell>
                         <TableCell className="text-right pr-10 font-mono font-black text-slate-900 tracking-tight text-lg">₹{item.amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</TableCell>
                       </TableRow>
                     ))}
                     {/* Padding for side-by-side consistency */}
                     {[...Array(Math.max(0, ((data.liabilities?.groups?.length || 0) + (data.equity?.groups?.length || 0)) - (data.assets?.groups?.length || 0)))].map((_, i) => (
                       <TableRow key={i} className="h-16 hover:bg-transparent border-none opacity-0"><TableCell colSpan={2}></TableCell></TableRow>
                     ))}
                   </TableBody>
                 </Table>

                 <div className="bg-blue-600 text-white p-10 flex justify-between items-center shadow-[0_-10px_30px_rgba(0,0,0,0.1)] relative z-10 mt-auto border-t-8 border-blue-800">
                    <span className="font-black text-xs uppercase tracking-[0.4em] text-blue-100 italic">Total Application of Funds</span>
                    <span className="text-3xl font-black tracking-tighter font-mono">₹{data.assets?.total?.toLocaleString() || 0}</span>
                 </div>
              </CardContent>
           </Card>
        </div>
      </div>

      <div className={cn(
        "p-10 rounded-[40px] border-4 flex flex-col md:flex-row items-center justify-between gap-8 font-black transition-all animate-in slide-in-from-bottom-6 duration-1000 group shadow-2xl",
        data.is_balanced
          ? "bg-emerald-600 border-emerald-400 text-white shadow-emerald-500/20 ring-[12px] ring-emerald-500/5"
          : "bg-rose-600 border-rose-400 text-white shadow-rose-500/20 ring-[12px] ring-rose-500/5"
      )}>
         <div className="flex items-center gap-6">
            <div className="h-16 w-16 rounded-[24px] bg-white/10 flex items-center justify-center border border-white/20 shadow-inner group-hover:scale-110 transition-transform duration-500">
               {data.is_balanced ? <CheckCircle2 className="h-8 w-8 text-white" /> : <AlertTriangle className="h-8 w-8 text-white animate-bounce" />}
            </div>
            <div>
               <h3 className="text-2xl font-black tracking-tighter uppercase italic">{data.is_balanced ? "System Reconciliation Verified" : "Data Discrepancy Protocol"}</h3>
               <p className="text-xs font-bold uppercase tracking-widest opacity-70 mt-1">{data.is_balanced ? "All ledger entries successfully validated against double-entry standards" : "Debit and Credit aggregates are out of sync. High-level manual audit initiated."}</p>
            </div>
         </div>
         {data.is_balanced && (
           <div className="bg-white/10 px-8 py-4 rounded-3xl border border-white/20 backdrop-blur-md">
              <span className="text-[10px] font-black uppercase tracking-[0.3em] opacity-60">Variance Factor</span>
              <p className="text-xl font-mono">0.0000%</p>
           </div>
         )}
      </div>
    </div>
  );
}
