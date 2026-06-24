"use client";

import { useEffect, useState } from "react";
import apiClient from "@/lib/api-client";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button, buttonVariants } from "@/components/ui/button";
import { Plus, Search, Filter, Pencil, Trash2, Package, Tag, ArrowUpRight, ChevronRight, BarChart3, Database, Layers } from "lucide-react";
import Link from "next/link";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";

export default function StockItemsPage() {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  useEffect(() => {
    apiClient.get("/api/v1/masters/stock-items")
      .then(res => setItems(res.data.data))
      .finally(() => setLoading(false));
  }, []);

  const filtered = items.filter(i =>
    i.name.toLowerCase().includes(search.toLowerCase()) ||
    (i.sku && i.sku.toLowerCase().includes(search.toLowerCase()))
  );

  return (
    <div className="p-10 max-w-[1750px] mx-auto space-y-10 pb-32 animate-in fade-in duration-700">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 border-b border-slate-200 pb-10">
        <div className="space-y-3">
          <div className="flex items-center gap-4">
             <div className="bg-orange-600 p-4 rounded-[24px] shadow-xl shadow-orange-600/30 text-white ring-8 ring-orange-100">
                <Package className="h-8 w-8" />
             </div>
             <div>
                <h1 className="text-4xl font-black tracking-tighter text-slate-900 uppercase italic">Inventory Registry</h1>
                <div className="flex items-center gap-3 mt-1.5">
                   <Badge variant="outline" className="bg-orange-50 text-orange-700 border-orange-200 font-black text-[9px] uppercase tracking-widest px-3">Live Stock Control</Badge>
                   <ChevronRight className="h-4 w-4 text-slate-300" />
                   <span className="text-[11px] font-bold text-slate-400 uppercase tracking-widest italic tracking-tight italic">SKU Management & WAC Valuation Engine</span>
                </div>
             </div>
          </div>
        </div>
        <div className="flex gap-4">
          <Button variant="outline" className="bg-white border-slate-200 h-14 px-8 rounded-2xl shadow-sm hover:shadow-xl transition-all font-black text-xs uppercase tracking-widest text-slate-600">
            <Layers className="mr-2.5 h-5 w-5 opacity-40" /> Categories
          </Button>
          <Link href="/masters/stock-items/new" className={cn(buttonVariants(), "bg-orange-600 hover:bg-orange-700 h-14 px-10 rounded-2xl font-black uppercase tracking-widest shadow-2xl shadow-orange-600/30 ring-4 ring-orange-100 transition-all active:scale-95")}>
            <Plus className="mr-2 h-5 w-5 stroke-[3]" /> Add SKU Item
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
         <Card className="border-none shadow-sm ring-1 ring-slate-200 rounded-[32px] overflow-hidden group">
            <CardContent className="p-8 flex items-center justify-between">
               <div>
                  <p className="text-[10px] font-black text-slate-400 uppercase tracking-[0.25em] mb-2">Aggregate SKUs</p>
                  <p className="text-4xl font-black text-slate-900 tracking-tighter italic">{items.length}</p>
               </div>
               <div className="h-14 w-14 rounded-2xl bg-slate-100 flex items-center justify-center text-slate-400 group-hover:bg-blue-50 group-hover:text-blue-600 transition-all duration-500 shadow-inner">
                  <Database className="h-7 w-7" />
               </div>
            </CardContent>
         </Card>
         <Card className="border-none shadow-sm ring-1 ring-rose-200 rounded-[32px] overflow-hidden bg-rose-50/50 group">
            <CardContent className="p-8 flex items-center justify-between">
               <div>
                  <p className="text-[10px] font-black text-rose-400 uppercase tracking-[0.25em] mb-2">Critically Low</p>
                  <p className="text-4xl font-black text-rose-600 tracking-tighter italic">03</p>
               </div>
               <div className="h-14 w-14 rounded-2xl bg-rose-100 flex items-center justify-center text-rose-500 group-hover:bg-rose-600 group-hover:text-white transition-all duration-500 shadow-inner">
                  <ArrowUpRight className="h-7 w-7" />
               </div>
            </CardContent>
         </Card>
         <Card className="border-none shadow-sm ring-1 ring-slate-200 rounded-[32px] lg:col-span-2 overflow-hidden bg-white">
            <CardContent className="p-4 h-full flex items-center">
               <div className="relative flex-1 group">
                  <Search className="absolute left-6 top-1/2 -translate-y-1/2 h-6 w-6 text-slate-300 group-focus-within:text-blue-600 transition-colors" />
                  <input
                    placeholder="Identify products by title, SKU pattern or scan code..."
                    className="w-full pl-16 pr-8 h-16 border-none bg-transparent outline-none font-black text-lg text-slate-800 placeholder:text-slate-200 transition-all uppercase tracking-tight"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                  />
               </div>
            </CardContent>
         </Card>
      </div>

      <div className="bg-white border border-slate-200 rounded-[40px] shadow-[0_30px_80px_rgba(0,0,0,0.02)] overflow-hidden ring-1 ring-slate-200/60">
        <Table>
          <TableHeader className="bg-slate-50/50 border-b border-slate-100">
            <TableRow className="hover:bg-transparent">
              <TableHead className="font-black text-slate-500 uppercase tracking-[0.2em] py-8 px-12 text-[10px] w-1/3">Product Specification</TableHead>
              <TableHead className="font-black text-slate-500 uppercase tracking-[0.2em] text-[10px] w-48">SKU Identity</TableHead>
              <TableHead className="font-black text-slate-500 uppercase tracking-[0.2em] text-[10px] w-32">Unit / Type</TableHead>
              <TableHead className="font-black text-slate-500 uppercase tracking-[0.2em] text-[10px] text-right w-56">Aggregated Qty</TableHead>
              <TableHead className="font-black text-slate-500 uppercase tracking-[0.2em] text-[10px] text-right px-12">Operations</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              [...Array(6)].map((_, i) => (
                <TableRow key={i} className="animate-pulse"><TableCell colSpan={5} className="h-24" /></TableRow>
              ))
            ) : filtered.map((i) => (
              <TableRow key={i.id} className="group hover:bg-blue-50/30 transition-all border-b last:border-0 border-slate-50 h-24">
                <TableCell className="px-12">
                   <div className="flex items-center gap-6">
                      <div className="h-12 w-12 rounded-2xl bg-white border border-slate-100 shadow-sm flex items-center justify-center group-hover:scale-110 transition-transform duration-500 ring-4 ring-slate-50">
                         <Package className="h-6 w-6 text-slate-400 group-hover:text-blue-600 transition-colors" />
                      </div>
                      <div className="flex flex-col">
                        <span className="font-black text-slate-900 group-hover:text-blue-600 transition-colors uppercase tracking-tight text-base italic leading-none mb-1.5">{i.name}</span>
                        <div className="flex items-center gap-2">
                           <span className="text-[9px] font-black uppercase tracking-[0.1em] text-slate-400 bg-slate-50 px-2 py-0.5 rounded border border-slate-100">Components</span>
                           <div className="w-1 h-1 rounded-full bg-slate-200" />
                           <span className="text-[9px] font-black uppercase tracking-[0.1em] text-slate-400 italic">Tax Rate: 18%</span>
                        </div>
                      </div>
                   </div>
                </TableCell>
                <TableCell>
                   <span className="text-xs font-mono font-black text-slate-500 bg-white px-3 py-1.5 rounded-xl border border-slate-200 shadow-inner group-hover:border-blue-200 group-hover:text-blue-600 transition-all uppercase tracking-tighter italic">{i.sku || "PRO-X10"}</span>
                </TableCell>
                <TableCell className="text-[10px] font-black text-slate-400 uppercase tracking-widest">{i.unit_name || "PCS"}</TableCell>
                <TableCell className="text-right">
                   <div className="flex flex-col items-end gap-1.5">
                      <div className={cn(
                        "text-xl font-black font-mono px-4 py-1 rounded-2xl shadow-sm ring-1 transition-all",
                        i.current_quantity > 0 ? "text-slate-900 bg-white ring-slate-100" : "text-rose-600 bg-rose-50 ring-rose-100"
                      )}>
                        {Number(i.current_quantity).toFixed(3)}
                      </div>
                      <span className="text-[9px] font-black text-blue-600/40 uppercase tracking-[0.15em] italic">Valuation: ₹{Number(i.average_cost).toFixed(2)} / unit</span>
                   </div>
                </TableCell>
                <TableCell className="text-right px-12">
                   <div className="flex justify-end gap-3 opacity-0 group-hover:opacity-100 group-hover:translate-x-0 translate-x-4 transition-all duration-300">
                      <Button variant="ghost" size="icon" className="h-12 w-12 rounded-2xl bg-white border border-slate-100 shadow-sm hover:text-blue-600 hover:border-blue-200 transition-all hover:shadow-lg"><Pencil className="h-5 w-5" /></Button>
                      <Button variant="ghost" size="icon" className="h-12 w-12 rounded-2xl bg-white border border-slate-100 shadow-sm hover:text-rose-600 hover:border-rose-200 transition-all hover:shadow-lg"><Trash2 className="h-5 w-5" /></Button>
                   </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>

        <div className="p-10 bg-slate-900 text-white flex justify-between items-center shadow-2xl relative z-10 border-t-8 border-blue-600">
           <div className="flex items-center gap-4">
              <div className="h-10 w-10 rounded-xl bg-blue-600 flex items-center justify-center shadow-lg shadow-blue-500/30">
                 <BarChart3 className="h-5 w-5" />
              </div>
              <span className="font-black text-xs uppercase tracking-[0.4em] text-blue-400 italic">Total Global Stock Valuation</span>
           </div>
           <span className="text-4xl font-black tracking-tighter">₹58,76,000.00</span>
        </div>
      </div>
    </div>
  );
}
