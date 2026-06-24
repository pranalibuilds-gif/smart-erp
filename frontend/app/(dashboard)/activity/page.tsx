"use client";

import { useEffect, useState } from "react";
import { getAuditLogs, AuditLog } from "@/features/audit/api/audit-api";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { History, Search, Download, Filter, User, HardDrive, Zap, ChevronRight, Activity, Cpu, ShieldCheck } from "lucide-react";
import { format } from "date-fns";
import { cn } from "@/lib/utils";

export default function ActivityCenterPage() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAuditLogs({ limit: 100 })
      .then(setLogs)
      .finally(() => setLoading(false));
  }, []);

  const getActionStyle = (action: string) => {
    switch (action) {
      case "CREATE": return "text-blue-600 bg-blue-100/50 border-blue-200 ring-4 ring-blue-500/5";
      case "POST": return "text-emerald-600 bg-emerald-100/50 border-emerald-200 ring-4 ring-emerald-500/5";
      case "CANCEL": return "text-rose-600 bg-rose-100/50 border-rose-200 ring-4 ring-rose-500/5";
      case "LOGIN": return "text-violet-600 bg-violet-100/50 border-violet-200 ring-4 ring-violet-500/5";
      default: return "text-slate-600 bg-slate-100 border-slate-200";
    }
  };

  if (loading) return (
    <div className="p-10 flex flex-col items-center justify-center h-[70vh] gap-6 text-slate-300 animate-pulse">
       <Activity className="h-16 w-16" />
       <p className="font-black uppercase tracking-[0.3em] text-xs">Accessing System Chronicles...</p>
    </div>
  );

  return (
    <div className="p-10 max-w-[1700px] mx-auto space-y-10 pb-32 animate-in fade-in duration-700">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 border-b border-slate-200 pb-10">
        <div className="space-y-3">
          <div className="flex items-center gap-4">
             <div className="bg-slate-900 p-4 rounded-[24px] shadow-xl shadow-slate-900/20 text-white ring-8 ring-slate-100">
                <History className="h-8 w-8" />
             </div>
             <div>
                <h1 className="text-4xl font-black tracking-tighter text-slate-900 uppercase italic">Immutable Ledger</h1>
                <div className="flex items-center gap-3 mt-1.5">
                   <Badge variant="outline" className="bg-slate-900 text-white border-slate-900 font-black text-[9px] uppercase tracking-[0.2em] px-3">Live Feed</Badge>
                   <ChevronRight className="h-4 w-4 text-slate-300" />
                   <span className="text-[11px] font-bold text-slate-400 uppercase tracking-widest italic tracking-tight">Full-spectrum audit logging and event tracking</span>
                </div>
             </div>
          </div>
        </div>
        <div className="flex gap-4">
          <Button variant="outline" className="bg-white border-slate-200 h-14 px-8 rounded-2xl shadow-sm hover:shadow-xl hover:border-slate-300 transition-all font-black text-xs uppercase tracking-widest text-slate-600">
            <Download className="mr-2.5 h-5 w-5 opacity-40" /> Historical Export
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-4 gap-8">
         <div className="space-y-8">
            <Card className="border-none shadow-sm ring-1 ring-slate-200 rounded-[28px] overflow-hidden bg-white">
               <CardHeader className="pb-4 px-8 pt-8 border-b border-slate-50"><CardDescription className="font-black uppercase text-[10px] tracking-[0.25em] text-blue-600">Live Status</CardDescription></CardHeader>
               <CardContent className="px-8 py-8">
                  <div className="flex items-center gap-4 text-emerald-600">
                     <div className="h-12 w-12 rounded-2xl bg-emerald-50 border border-emerald-100 flex items-center justify-center">
                        <Zap className="h-6 w-6 animate-pulse" />
                     </div>
                     <div>
                        <span className="font-black text-lg tracking-tight uppercase">Operational</span>
                        <p className="text-[9px] font-bold uppercase tracking-widest opacity-60">Tracing active events</p>
                     </div>
                  </div>
               </CardContent>
            </Card>

            <Card className="border-none shadow-sm ring-1 ring-slate-200 rounded-[28px] overflow-hidden bg-slate-900 text-white group">
               <CardHeader className="pb-4 px-8 pt-8 border-b border-white/5"><CardDescription className="font-black uppercase text-[10px] tracking-[0.25em] text-slate-400">Security Metrics</CardDescription></CardHeader>
               <CardContent className="px-8 py-8 space-y-8">
                  <div className="flex justify-between items-end">
                     <div>
                        <p className="text-[9px] font-black uppercase tracking-widest opacity-50 mb-1">Log Retention</p>
                        <p className="text-2xl font-black tracking-tight italic">365 DAYS</p>
                     </div>
                     <ShieldCheck className="h-8 w-8 text-blue-500 opacity-50 group-hover:scale-110 transition-transform duration-500" />
                  </div>
                  <div className="flex justify-between items-end">
                     <div>
                        <p className="text-[9px] font-black uppercase tracking-widest opacity-50 mb-1">Integrity Check</p>
                        <p className="text-sm font-black tracking-widest text-emerald-400 uppercase italic">SHA-256 Validated</p>
                     </div>
                     <Cpu className="h-5 w-5 text-slate-600" />
                  </div>
               </CardContent>
            </Card>
         </div>

         <Card className="xl:col-span-3 border-none shadow-[0_20px_50px_rgba(0,0,0,0.03)] ring-1 ring-slate-200 rounded-[40px] overflow-hidden bg-white">
            <div className="p-8 border-b border-slate-100 flex items-center justify-between bg-slate-50/50 px-10">
               <div className="relative flex-1 max-w-xl group">
                  <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-300 group-focus-within:text-blue-600 transition-colors" />
                  <input
                    placeholder="Search by trace ID, user identity or modification type..."
                    className="w-full pl-12 h-14 border-none bg-transparent outline-none font-bold text-slate-700 placeholder:text-slate-300 transition-all uppercase text-xs tracking-widest"
                  />
               </div>
               <Button variant="ghost" className="h-14 px-8 rounded-2xl border border-slate-100 text-slate-400 hover:text-blue-600 transition-all font-black text-[10px] uppercase tracking-[0.2em]"><Filter className="mr-3 h-4 w-4" /> Comprehensive Filters</Button>
            </div>

            <Table>
              <TableHeader className="bg-slate-50/30">
                <TableRow className="hover:bg-transparent border-b border-slate-100">
                  <TableHead className="font-black text-slate-500 uppercase tracking-widest py-8 px-12 text-[10px] w-52">Event Timestamp</TableHead>
                  <TableHead className="font-black text-slate-500 uppercase tracking-widest text-[10px] w-64">System Operator</TableHead>
                  <TableHead className="font-black text-slate-500 uppercase tracking-widest text-[10px] w-44">Module Core</TableHead>
                  <TableHead className="font-black text-slate-500 uppercase tracking-widest text-[10px] text-center w-36">Action</TableHead>
                  <TableHead className="font-black text-slate-500 uppercase tracking-widest text-[10px] px-12">Cryptographic Snapshot Detail</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {logs.map((log) => (
                  <TableRow key={log.id} className="group hover:bg-slate-50/80 transition-all border-b last:border-0 border-slate-50 h-24">
                    <TableCell className="px-12 whitespace-nowrap">
                       <div className="flex flex-col">
                          <span className="text-sm font-black text-slate-800 tracking-tight italic">{format(new Date(log.created_at), "MMM dd, yyyy")}</span>
                          <span className="text-[10px] text-slate-400 font-black font-mono tracking-tighter uppercase">{format(new Date(log.created_at), "HH:mm:ss:SSS")}</span>
                       </div>
                    </TableCell>
                    <TableCell>
                       <div className="flex items-center gap-4">
                          <div className="h-10 w-10 rounded-xl bg-white border border-slate-200 flex items-center justify-center text-xs font-black text-slate-400 shadow-sm ring-1 ring-slate-100 group-hover:border-blue-200 group-hover:text-blue-600 transition-all">
                             {log.user_full_name?.substring(0, 1) || "S"}
                          </div>
                          <div className="flex flex-col">
                             <span className="text-xs font-black text-slate-900 group-hover:text-blue-600 transition-colors uppercase tracking-tight">{log.user_full_name || "System Core"}</span>
                             <span className="text-[9px] text-slate-400 font-bold uppercase tracking-widest">ID: {log.user_id?.split('-')[0] || "AUTO"}</span>
                          </div>
                       </div>
                    </TableCell>
                    <TableCell>
                       <span className="text-[10px] font-black text-slate-500 uppercase tracking-[0.15em] bg-slate-100/50 px-3 py-1.5 rounded-lg border border-slate-200/60 flex items-center gap-2 w-fit">
                          <HardDrive className="h-3 w-3 opacity-50" /> {log.entity_type}
                       </span>
                    </TableCell>
                    <TableCell className="text-center">
                      <Badge className={cn("text-[9px] font-black tracking-[0.2em] px-3 py-1 rounded-full border shadow-sm", getActionStyle(log.action))} variant="outline">
                        {log.action}
                      </Badge>
                    </TableCell>
                    <TableCell className="px-12">
                       {log.new_values && (
                          <div className="bg-slate-900 rounded-2xl p-4 border border-white/5 relative group/code overflow-hidden shadow-2xl">
                             <div className="absolute top-0 left-0 w-1 h-full bg-blue-600/50 group-hover/code:bg-blue-500 transition-colors" />
                             <p className="text-[10px] font-mono text-blue-200/70 break-all line-clamp-2 leading-relaxed">
                               {JSON.stringify(log.new_values).replace(/["{}]/g, '').replace(/:/g, ': ').replace(/,/g, ' | ')}
                             </p>
                          </div>
                       )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
         </Card>
      </div>
    </div>
  );
}
