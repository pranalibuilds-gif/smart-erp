"use client";

import { useEffect, useState } from "react";
import { listVouchers } from "@/features/vouchers/api/vouchers-api";
import { Voucher, VoucherStatus } from "@/features/vouchers/types";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Plus, Search, Eye, Filter, Download, Receipt, ChevronRight, FileText, Calendar, Wallet } from "lucide-react";
import Link from "next/link";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export default function VouchersPage() {
  const [vouchers, setVouchers] = useState<Voucher[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  useEffect(() => {
    listVouchers()
      .then(setVouchers)
      .finally(() => setLoading(false));
  }, []);

  const getStatusColor = (status: VoucherStatus) => {
    switch (status) {
      case VoucherStatus.POSTED: return "bg-emerald-50 text-emerald-700 border-emerald-200 ring-4 ring-emerald-500/5";
      case VoucherStatus.CANCELLED: return "bg-rose-50 text-rose-700 border-rose-200 ring-4 ring-rose-500/5";
      default: return "bg-amber-50 text-amber-700 border-amber-200 ring-4 ring-amber-500/5";
    }
  };

  const filteredVouchers = vouchers.filter(v =>
    v.voucher_number.toLowerCase().includes(search.toLowerCase()) ||
    v.narration?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="p-10 max-w-[1700px] mx-auto space-y-10 pb-32 animate-in fade-in slide-in-from-bottom-2 duration-700">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 border-b border-slate-200 pb-10">
        <div className="space-y-2">
           <div className="flex items-center gap-4 mb-2">
              <div className="bg-slate-900 p-3 rounded-2xl shadow-xl shadow-slate-900/30 text-white">
                 <Receipt className="h-7 w-7" />
              </div>
              <div>
                 <h1 className="text-4xl font-black tracking-tight text-slate-900 uppercase">Accounting Journal</h1>
                 <div className="flex items-center gap-2 mt-1">
                    <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest bg-slate-100 px-2 py-0.5 rounded border border-slate-200">Total Entries: {vouchers.length}</span>
                    <ChevronRight className="h-3 w-3 text-slate-300" />
                    <span className="text-[10px] font-black text-blue-600 uppercase tracking-widest">Double Entry Records</span>
                 </div>
              </div>
           </div>
        </div>
        <div className="flex gap-4">
          <Button variant="outline" className="bg-white border-slate-200 h-14 px-6 rounded-2xl shadow-sm hover:shadow transition-all group font-bold">
            <Download className="mr-2 h-5 w-5 text-slate-400 group-hover:text-blue-600" /> Export Data
          </Button>
          <Link href="/vouchers/new" className={cn(buttonVariants(), "bg-blue-600 hover:bg-blue-700 h-14 px-10 rounded-2xl shadow-2xl shadow-blue-500/40 font-black uppercase tracking-tight")}>
            <Plus className="mr-2 h-5 w-5" /> New Voucher
          </Link>
        </div>
      </div>

      <Card className="border-none shadow-sm ring-1 ring-slate-200 overflow-hidden rounded-3xl">
        <CardContent className="p-0">
          <div className="p-6 border-b border-slate-100 flex items-center justify-between bg-slate-50/30">
            <div className="relative flex-1 max-w-xl group">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-300 group-focus-within:text-blue-500 transition-colors" />
              <input
                placeholder="Search voucher number, narration or amount..."
                className="w-full pl-12 h-14 border-none bg-transparent outline-none font-bold text-slate-700 placeholder:text-slate-300 transition-all"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <div className="flex items-center gap-4 border-l border-slate-100 pl-8 ml-8">
               <Button variant="ghost" className="h-12 w-12 rounded-2xl border border-slate-100 text-slate-400 hover:text-blue-600 hover:bg-blue-50 transition-all"><Filter className="h-5 w-5" /></Button>
            </div>
          </div>

          <Table>
            <TableHeader className="bg-slate-50/50">
              <TableRow className="hover:bg-transparent border-b border-slate-100">
                <TableHead className="font-black text-slate-500 uppercase tracking-widest py-6 px-10 text-[10px]">Voucher Context</TableHead>
                <TableHead className="font-black text-slate-500 uppercase tracking-widest text-[10px]">Date</TableHead>
                <TableHead className="font-black text-slate-500 uppercase tracking-widest text-[10px]">Type</TableHead>
                <TableHead className="font-black text-slate-500 uppercase tracking-widest text-[10px] text-right">Debit Aggregate</TableHead>
                <TableHead className="font-black text-slate-500 uppercase tracking-widest text-[10px] text-center w-40">Status</TableHead>
                <TableHead className="w-20"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                [...Array(5)].map((_, i) => (
                  <TableRow key={i} className="animate-pulse"><TableCell colSpan={6} className="h-24 px-10" /></TableRow>
                ))
              ) : (
                filteredVouchers.map((v) => {
                  const totalAmount = v.entries?.reduce((sum, e) => sum + (Number(e.debit_amount) || 0), 0) || 0;
                  return (
                    <TableRow key={v.id} className="group hover:bg-blue-50/30 transition-all border-b last:border-0 border-slate-100 h-24">
                      <TableCell className="px-10">
                        <div className="flex flex-col">
                           <span className="font-black text-slate-900 font-mono text-sm tracking-tighter uppercase">{v.voucher_number}</span>
                           <span className="text-[10px] text-slate-400 font-bold uppercase tracking-tight mt-1 line-clamp-1 italic italic">"{v.narration || "No Narration"}"</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2 text-slate-500 font-bold text-sm">
                           <Calendar className="h-3.5 w-3.5 text-slate-300" />
                           {v.voucher_date}
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline" className="text-[10px] font-black uppercase tracking-widest border-slate-200 text-slate-500 bg-slate-50 px-3">{v.voucher_type}</Badge>
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex items-center justify-end gap-2">
                           <span className="font-black text-slate-900 font-mono text-lg tracking-tight">₹{totalAmount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
                           <div className="w-1.5 h-1.5 rounded-full bg-blue-500" />
                        </div>
                      </TableCell>
                      <TableCell className="text-center">
                        <Badge className={cn("text-[10px] font-black tracking-[0.15em] uppercase px-4 py-1.5 rounded-full border-2", getStatusColor(v.status))} variant="outline">
                          {v.status}
                        </Badge>
                      </TableCell>
                      <TableCell className="px-6">
                        <div className="flex justify-end gap-3 opacity-0 group-hover:opacity-100 group-hover:translate-x-0 translate-x-4 transition-all duration-300">
                          <Link href={`/vouchers/${v.id}`} className={cn(buttonVariants({ variant: "ghost", size: "icon" }), "h-11 w-11 rounded-2xl bg-white border border-slate-200 shadow-sm hover:text-blue-600 hover:border-blue-300")}>
                            <Eye className="h-5 w-5" />
                          </Link>
                        </div>
                      </TableCell>
                    </TableRow>
                  );
                })
              )}
            </TableBody>
          </Table>

          {!loading && filteredVouchers.length === 0 && (
             <div className="py-40 flex flex-col items-center gap-6 text-center opacity-40">
                <Receipt className="h-20 w-16 text-slate-200" />
                <div>
                   <p className="text-xl font-black uppercase tracking-widest text-slate-400">Journal Empty</p>
                   <p className="text-xs font-bold uppercase tracking-tighter mt-1">Record your first accounting entry to populate the register</p>
                </div>
             </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
