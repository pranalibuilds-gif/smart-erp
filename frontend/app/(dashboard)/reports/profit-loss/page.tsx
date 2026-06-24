"use client";

import { useEffect, useState } from "react";
import apiClient from "@/lib/api-client";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Printer, Download, TrendingUp, TrendingDown, FileText, ChevronRight, BarChart, ArrowUpRight, Scale, AlertCircle, RefreshCw } from "lucide-react";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";

export default function ProfitLossPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiClient.get("/api/v1/reports/profit-loss");
      setData(res.data.data);
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Financial protocol failed to synchronize");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) return (
    <div className="p-10 flex flex-col items-center justify-center h-[70vh] gap-6 text-slate-300 animate-pulse">
       <BarChart className="h-16 w-16 text-slate-200" />
       <p className="font-black uppercase tracking-[0.3em] text-xs">Auditing Operational Performance...</p>
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

  return (
    <div className="p-10 max-w-[1700px] mx-auto space-y-10 pb-32 animate-in fade-in duration-700">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 border-b border-slate-200 pb-10">
        <div className="space-y-3">
          <div className="flex items-center gap-4">
             <div className="bg-slate-900 p-4 rounded-3xl shadow-xl shadow-slate-900/20 text-white ring-8 ring-slate-100">
                <FileText className="h-8 w-8" />
             </div>
             <div>
                <h1 className="text-4xl font-black tracking-tighter text-slate-900 uppercase italic">Profit & Loss Summary</h1>
                <div className="flex items-center gap-3 mt-1.5">
                   <Badge variant="outline" className="bg-indigo-50 text-indigo-700 border-indigo-100 font-black text-[9px] uppercase tracking-widest px-3">Revenue Protocol</Badge>
                   <ChevronRight className="h-4 w-4 text-slate-300" />
                   <span className="text-[11px] font-bold text-slate-400 uppercase tracking-widest italic tracking-tight">Periodical Income vs Operational Expenditure Mapping</span>
                </div>
             </div>
          </div>
        </div>
        <div className="flex gap-4">
          <Button variant="outline" className="bg-white border-slate-200 h-14 px-8 rounded-2xl shadow-sm hover:shadow-xl hover:border-slate-300 transition-all font-black text-xs uppercase tracking-widest text-slate-600">
            <Printer className="mr-2.5 h-5 w-5 opacity-40" /> Archive Print
          </Button>
          <Button variant="outline" className="bg-white border-slate-200 h-14 px-8 rounded-2xl shadow-sm hover:shadow-xl hover:border-slate-300 transition-all font-black text-xs uppercase tracking-widest text-slate-600">
            <Download className="mr-2.5 h-5 w-5 opacity-40" /> Statement PDF
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-10">
        {/* INCOME */}
        <Card className="border-none shadow-[0_20px_50px_rgba(0,0,0,0.04)] ring-1 ring-slate-200 rounded-[32px] overflow-hidden group">
          <CardHeader className="bg-emerald-600 text-white py-8 px-10 border-b border-white/5 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-white/20 rounded-full -mr-10 -mt-10 blur-3xl group-hover:bg-white/40 transition-all duration-700" />
            <div className="flex justify-between items-center relative z-10">
               <div>
                  <CardTitle className="text-xs font-black uppercase tracking-[0.3em] text-emerald-100">Flow A</CardTitle>
                  <p className="text-2xl font-black tracking-tight mt-1 italic uppercase">GROSS REVENUE & INCOME</p>
               </div>
               <TrendingUp className="h-10 w-10 text-emerald-100 opacity-50 group-hover:scale-110 transition-transform duration-500" />
            </div>
          </CardHeader>
          <CardContent className="p-0 bg-white min-h-[500px] flex flex-col">
            <Table>
               <TableBody>
                  {data.income?.map((item: any, i: number) => (
                    <TableRow key={i} className="hover:bg-emerald-50/50 transition-colors border-b border-slate-50 last:border-0 h-20 group/row">
                       <TableCell className="pl-10">
                          <div className="flex items-center gap-4">
                             <div className="w-1.5 h-8 bg-slate-100 rounded-full group-hover/row:bg-emerald-500 transition-all duration-500" />
                             <span className="font-bold text-slate-700 py-4 group-hover/row:text-emerald-700 transition-colors uppercase tracking-tight text-sm">{item.name}</span>
                          </div>
                       </TableCell>
                       <TableCell className="text-right pr-10 font-mono font-black text-slate-900 tracking-tight text-lg">₹{item.amount.toLocaleString()}</TableCell>
                    </TableRow>
                  ))}
               </TableBody>
            </Table>
            <div className="mt-auto bg-emerald-50/50 border-t border-emerald-100 p-10 flex justify-between items-center">
               <span className="font-black text-xs uppercase tracking-[0.4em] text-emerald-700 italic">Total Income Generated</span>
               <span className="text-3xl font-black tracking-tighter text-emerald-900 font-mono">₹{(data.total_income || 0).toLocaleString()}</span>
            </div>
          </CardContent>
        </Card>

        {/* EXPENSES */}
        <Card className="border-none shadow-[0_20px_50px_rgba(0,0,0,0.04)] ring-1 ring-slate-200 rounded-[32px] overflow-hidden group">
          <CardHeader className="bg-rose-600 text-white py-8 px-10 border-b border-white/5 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-white/20 rounded-full -mr-10 -mt-10 blur-3xl group-hover:bg-white/40 transition-all duration-700" />
            <div className="flex justify-between items-center relative z-10">
               <div>
                  <CardTitle className="text-xs font-black uppercase tracking-[0.3em] text-rose-100">Flow B</CardTitle>
                  <p className="text-2xl font-black tracking-tight mt-1 italic uppercase">OPERATIONAL EXPENDITURE</p>
               </div>
               <TrendingDown className="h-10 w-10 text-rose-100 opacity-50 group-hover:scale-110 transition-transform duration-500" />
            </div>
          </CardHeader>
          <CardContent className="p-0 bg-white min-h-[500px] flex flex-col">
            <Table>
               <TableBody>
                  {data.expenses?.map((item: any, i: number) => (
                    <TableRow key={i} className="hover:bg-rose-50/50 transition-colors border-b border-slate-50 last:border-0 h-20 group/row">
                       <TableCell className="pl-10">
                          <div className="flex items-center gap-4">
                             <div className="w-1.5 h-8 bg-slate-100 rounded-full group-hover/row:bg-rose-500 transition-all duration-500" />
                             <span className="font-bold text-slate-700 py-4 group-hover/row:text-rose-700 transition-colors uppercase tracking-tight text-sm">{item.name}</span>
                          </div>
                       </TableCell>
                       <TableCell className="text-right pr-10 font-mono font-black text-slate-900 tracking-tight text-lg">₹{item.amount.toLocaleString()}</TableCell>
                    </TableRow>
                  ))}
               </TableBody>
            </Table>
            <div className="mt-auto bg-rose-50/50 border-t border-rose-100 p-10 flex justify-between items-center">
               <span className="font-black text-xs uppercase tracking-[0.4em] text-rose-700 italic">Total Cost Application</span>
               <span className="text-3xl font-black tracking-tighter text-rose-900 font-mono">₹{(data.total_expenses || 0).toLocaleString()}</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className={cn(
        "border-none shadow-2xl ring-1 overflow-hidden rounded-[40px] p-2 relative group",
        data.net_profit >= 0 ? "ring-emerald-500/20 bg-emerald-600 shadow-emerald-500/20" : "ring-rose-500/20 bg-rose-600 shadow-rose-500/20"
      )}>
         <div className="absolute top-0 right-0 p-10 opacity-10 group-hover:scale-110 transition-transform duration-1000">
            <Scale className="h-40 w-40 text-white" />
         </div>
         <CardContent className="p-12 flex flex-col md:flex-row justify-between items-center gap-10 bg-white/5 backdrop-blur-3xl rounded-[36px] relative z-10">
            <div className="flex items-center gap-8">
               <div className="bg-white/10 h-20 w-20 rounded-[28px] flex items-center justify-center border border-white/20 shadow-inner">
                  {data.net_profit >= 0 ? <TrendingUp className="h-10 w-10 text-white" /> : <AlertCircle className="h-10 w-10 text-white animate-pulse" />}
               </div>
               <div className="space-y-1">
                  <p className="text-xs font-black uppercase tracking-[0.4em] opacity-60 text-white">Finalized Statement Result</p>
                  <h3 className="text-4xl font-black text-white uppercase italic tracking-tighter">{data.net_profit >= 0 ? 'NET TRADING SURPLUS' : 'NET OPERATIONAL DEFICIT'}</h3>
               </div>
            </div>
            <div className="text-right border-l-4 border-white/20 pl-12">
               <span className="text-6xl font-black font-mono text-white tracking-tighter">
                  ₹{Math.abs(data.net_profit || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
               </span>
               <div className="flex items-center justify-end gap-2 mt-2">
                  <ArrowUpRight className="h-4 w-4 text-emerald-300" />
                  <p className="text-[10px] font-black text-white/70 uppercase tracking-[0.2em]">Verified performance data</p>
               </div>
            </div>
         </CardContent>
      </Card>
    </div>
  );
}
