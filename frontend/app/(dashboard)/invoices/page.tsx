"use client";

import { useEffect, useState } from "react";
import apiClient from "@/lib/api-client";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button, buttonVariants } from "@/components/ui/button";
import { Plus, Search, Eye, FileText, Filter, Download, MoreHorizontal, Calendar, ArrowUpDown, ChevronRight, TrendingUp } from "lucide-react";
import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { cn } from "@/lib/utils";

export default function InvoicesPage() {
  const [invoices, setInvoices] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  useEffect(() => {
    apiClient.get("/api/v1/billing/invoices")
      .then(res => setInvoices(res.data.data))
      .finally(() => setLoading(false));
  }, []);

  const getStatusStyle = (status: string) => {
    switch (status) {
      case "POSTED": return "bg-emerald-50 text-emerald-700 border-emerald-200 ring-4 ring-emerald-500/5";
      case "CANCELLED": return "bg-rose-50 text-rose-700 border-rose-200 ring-4 ring-rose-500/5";
      default: return "bg-amber-50 text-amber-700 border-amber-200 ring-4 amber-500/5";
    }
  };

  const filtered = invoices.filter(inv =>
    inv.invoice_number.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="p-10 max-w-[1700px] mx-auto space-y-10 pb-32 animate-in fade-in slide-in-from-bottom-2 duration-700">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 border-b border-slate-200 pb-10">
        <div className="space-y-2">
           <div className="flex items-center gap-3 mb-2">
              <div className="bg-blue-600 p-3 rounded-2xl shadow-xl shadow-blue-500/30 text-white">
                 <FileText className="h-7 w-7" />
              </div>
              <div>
                 <h1 className="text-4xl font-black tracking-tight text-slate-900 uppercase">Billing Ledger</h1>
                 <div className="flex items-center gap-2 mt-1">
                    <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest bg-slate-100 px-2 py-0.5 rounded border border-slate-200">Total Records: {invoices.length}</span>
                    <ChevronRight className="h-3 w-3 text-slate-300" />
                    <span className="text-[10px] font-black text-blue-600 uppercase tracking-widest">Active Statements</span>
                 </div>
              </div>
           </div>
        </div>
        <div className="flex gap-4">
          <Button variant="outline" className="bg-white border-slate-200 h-14 px-6 rounded-2xl shadow-sm hover:shadow transition-all group font-bold">
            <Download className="mr-2 h-5 w-5 text-slate-400 group-hover:text-blue-600" /> Bulk Export
          </Button>
          <Link href="/invoices/new" className={cn(buttonVariants(), "bg-blue-600 hover:bg-blue-700 h-14 px-10 rounded-2xl shadow-2xl shadow-blue-500/40 font-black uppercase tracking-tight")}>
            <Plus className="mr-2 h-5 w-5" /> New Document
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-4 gap-8">
         <Card className="xl:col-span-3 border-none shadow-sm ring-1 ring-slate-200 overflow-hidden rounded-3xl">
            <CardContent className="p-0">
               <div className="p-6 border-b border-slate-100 flex items-center justify-between bg-slate-50/30">
                  <div className="relative flex-1 max-w-xl group">
                     <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-300 group-focus-within:text-blue-500 transition-colors" />
                     <input
                        placeholder="Search document ID, party name or GST number..."
                        className="w-full pl-12 h-14 border-none bg-transparent outline-none font-bold text-slate-700 placeholder:text-slate-300 transition-all"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                     />
                  </div>
                  <div className="flex items-center gap-4 border-l border-slate-100 pl-8 ml-8">
                     <div className="flex items-center gap-2 bg-white border border-slate-200 p-1.5 rounded-2xl shadow-sm">
                        {['all', 'sales', 'purchase'].map(t => (
                           <button key={t} className={cn("px-5 py-2 text-[10px] font-black uppercase tracking-widest rounded-xl transition-all", t === 'all' ? "bg-slate-900 text-white shadow-lg shadow-slate-900/20" : "text-slate-400 hover:text-slate-900")}>
                              {t}
                           </button>
                        ))}
                     </div>
                     <Button variant="ghost" className="h-12 w-12 rounded-2xl border border-slate-100 text-slate-400 hover:text-blue-600 hover:bg-blue-50 transition-all"><Filter className="h-5 w-5" /></Button>
                  </div>
               </div>

               <Table>
                 <TableHeader className="bg-slate-50/50">
                   <TableRow className="hover:bg-transparent border-b border-slate-100">
                     <TableHead className="font-black text-slate-500 uppercase tracking-widest py-6 px-10 text-[10px]">Document Context</TableHead>
                     <TableHead className="font-black text-slate-500 uppercase tracking-widest text-[10px]"><div className="flex items-center gap-2 cursor-pointer hover:text-slate-900">Posting Date <ArrowUpDown className="h-3 w-3" /></div></TableHead>
                     <TableHead className="font-black text-slate-500 uppercase tracking-widest text-[10px]">Trading Party</TableHead>
                     <TableHead className="font-black text-slate-500 uppercase tracking-widest text-[10px] text-right">Net Value</TableHead>
                     <TableHead className="font-black text-slate-500 uppercase tracking-widest text-[10px] text-center w-40">Status</TableHead>
                     <TableHead className="w-20"></TableHead>
                   </TableRow>
                 </TableHeader>
                 <TableBody>
                   {loading ? (
                     [...Array(6)].map((_, i) => (
                       <TableRow key={i} className="animate-pulse"><TableCell colSpan={6} className="h-24 px-10" /></TableRow>
                     ))
                   ) : filtered.map((inv) => (
                     <TableRow key={inv.id} className="group hover:bg-blue-50/30 transition-all border-b last:border-0 border-slate-100 h-24">
                       <TableCell className="px-10">
                          <div className="flex flex-col">
                             <div className="flex items-center gap-2 mb-1.5">
                                <span className={cn(
                                   "text-[9px] font-black uppercase px-2 py-0.5 rounded shadow-sm border",
                                   inv.document_type === 'SALES' ? "bg-blue-600 text-white border-blue-700 shadow-blue-500/20" : "bg-indigo-600 text-white border-indigo-700 shadow-indigo-500/20"
                                )}>{inv.document_type}</span>
                                <Badge variant="outline" className="text-[9px] font-black uppercase tracking-widest border-slate-200 text-slate-400 bg-slate-50">Local</Badge>
                             </div>
                             <span className="font-black text-slate-900 font-mono text-sm tracking-tighter uppercase">{inv.invoice_number}</span>
                          </div>
                       </TableCell>
                       <TableCell>
                          <div className="flex items-center gap-2 text-slate-500 font-bold text-sm">
                             <Calendar className="h-3.5 w-3.5 text-slate-300" />
                             {inv.invoice_date}
                          </div>
                       </TableCell>
                       <TableCell>
                          <div className="flex flex-col">
                             <span className="font-black text-slate-800 text-sm group-hover:text-blue-600 transition-colors uppercase tracking-tight">{inv.party_name || "Nexus Global Solution"}</span>
                             <span className="text-[10px] text-slate-400 font-bold uppercase tracking-tighter mt-0.5">GST: 27AAACN1234A1Z1</span>
                          </div>
                       </TableCell>
                       <TableCell className="text-right">
                          <div className="flex flex-col items-end">
                             <span className="font-black text-slate-900 font-mono text-lg tracking-tight">₹{Number(inv.total_amount).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
                             <span className="text-[9px] text-emerald-500 font-black uppercase tracking-tighter mt-0.5">Inclusive Tax</span>
                          </div>
                       </TableCell>
                       <TableCell className="text-center">
                         <Badge className={cn("text-[10px] font-black tracking-[0.15em] uppercase px-4 py-1.5 rounded-full border-2", getStatusStyle(inv.status))} variant="outline">
                           {inv.status}
                         </Badge>
                       </TableCell>
                       <TableCell className="px-6">
                          <div className="flex justify-end gap-3 opacity-0 group-hover:opacity-100 group-hover:translate-x-0 translate-x-4 transition-all duration-300">
                             <Link href={`/invoices/${inv.id}`} className={cn(buttonVariants({ variant: "ghost", size: "icon" }), "h-11 w-11 rounded-2xl bg-white border border-slate-200 shadow-sm hover:text-blue-600 hover:border-blue-300")}>
                               <Eye className="h-5 w-5" />
                             </Link>
                             <Button variant="ghost" size="icon" className="h-11 w-11 rounded-2xl bg-white border border-slate-200 shadow-sm hover:bg-slate-50"><MoreHorizontal className="h-5 w-5 text-slate-400" /></Button>
                          </div>
                       </TableCell>
                     </TableRow>
                   ))}
                 </TableBody>
               </Table>

               {!loading && filtered.length === 0 && (
                  <div className="py-40 flex flex-col items-center gap-6 text-center opacity-40">
                     <FileText className="h-20 w-16 text-slate-200" />
                     <div>
                        <p className="text-xl font-black uppercase tracking-widest text-slate-400">Empty Register</p>
                        <p className="text-xs font-bold uppercase tracking-tighter mt-1">Adjust filters or record a new transaction</p>
                     </div>
                  </div>
               )}
            </CardContent>
         </Card>

         <div className="space-y-8">
            <Card className="border-none shadow-sm ring-1 ring-slate-200 rounded-3xl overflow-hidden bg-slate-900 text-white">
               <CardHeader className="border-b border-white/5 py-6">
                  <CardTitle className="text-xs font-black uppercase tracking-[0.2em] text-blue-400">Document Insights</CardTitle>
               </CardHeader>
               <CardContent className="py-8 space-y-8">
                  <div className="flex items-center justify-between">
                     <div className="space-y-1">
                        <p className="text-[10px] font-black text-white/40 uppercase tracking-widest">Aggregate Turnover</p>
                        <p className="text-3xl font-black tracking-tighter">₹2.45 Cr</p>
                     </div>
                     <TrendingUp className="h-8 w-8 text-blue-500 opacity-50" />
                  </div>
                  <div className="space-y-6">
                     <div className="space-y-2">
                        <div className="flex justify-between items-end">
                           <span className="text-[10px] font-black text-white/50 uppercase tracking-widest">Sales Velocity</span>
                           <span className="text-xs font-black text-emerald-400">+14%</span>
                        </div>
                        <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                           <div className="h-full w-[78%] bg-blue-600 shadow-[0_0_10px_#2563eb]" />
                        </div>
                     </div>
                     <div className="space-y-2">
                        <div className="flex justify-between items-end">
                           <span className="text-[10px] font-black text-white/50 uppercase tracking-widest">Pending Settlements</span>
                           <span className="text-xs font-black text-rose-400">22 Docs</span>
                        </div>
                        <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                           <div className="h-full w-[42%] bg-rose-600 shadow-[0_0_10px_#ef4444]" />
                        </div>
                     </div>
                  </div>
               </CardContent>
            </Card>

            <Card className="border-none shadow-sm ring-1 ring-slate-200 rounded-3xl overflow-hidden bg-white">
               <CardHeader className="border-b border-slate-50 py-6 px-8">
                  <CardTitle className="text-xs font-black uppercase tracking-[0.2em] text-slate-500">Recently Modified</CardTitle>
               </CardHeader>
               <CardContent className="p-0 divide-y divide-slate-50">
                  {[1, 2, 3].map(i => (
                    <div key={i} className="px-8 py-6 hover:bg-slate-50 transition-all cursor-pointer group">
                       <div className="flex justify-between items-start mb-2">
                          <span className="font-mono text-xs font-black text-slate-900 uppercase">#INV-2024-00{i*4}</span>
                          <span className="text-[9px] font-black text-blue-600 bg-blue-50 px-2 py-0.5 rounded tracking-tighter">Drafted</span>
                       </div>
                       <p className="text-xs font-bold text-slate-500 uppercase tracking-tight truncate">Modification by Admin @ 14:22</p>
                    </div>
                  ))}
               </CardContent>
            </Card>
         </div>
      </div>
    </div>
  );
}
