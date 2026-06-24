"use client";

import { useEffect, useState } from "react";
import { getStockSummary } from "@/features/reports/api/reports-api";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Package, Download, Printer, Filter, ArrowUpRight, ArrowDownRight, Warehouse } from "lucide-react";
import Link from "next/link";
import { cn } from "@/lib/utils";
import { buttonVariants } from "@/components/ui/button";

export default function StockSummaryPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getStockSummary()
      .then(setData)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-8 flex justify-center items-center h-96 text-slate-400">Loading Inventory Report...</div>;

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div className="flex items-center gap-4">
           <div className="bg-orange-500 p-3 rounded-2xl shadow-lg shadow-orange-500/20 text-white">
              <Package className="h-6 w-6" />
           </div>
           <div>
              <h1 className="text-3xl font-bold tracking-tight text-slate-900">Stock Summary</h1>
              <p className="text-slate-500 mt-1">Real-time inventory valuation and movement across all warehouses</p>
           </div>
        </div>
        <div className="flex gap-3">
          <Link href="/reports/stock-by-warehouse" className={cn(buttonVariants({ variant: "outline" }), "bg-white")}>
            <Warehouse className="mr-2 h-4 w-4" /> Warehouse View
          </Link>
          <Button variant="outline" className="bg-white"><Printer className="mr-2 h-4 w-4" /> Print</Button>
          <Button className="bg-blue-600 hover:bg-blue-700 shadow-lg shadow-blue-200"><Download className="mr-2 h-4 w-4" /> Export CSV</Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
         <Card className="border-none shadow-sm ring-1 ring-slate-200">
            <CardHeader className="pb-2"><CardDescription className="font-bold uppercase text-[10px] tracking-widest text-slate-500">Total Items</CardDescription></CardHeader>
            <CardContent><p className="text-2xl font-bold text-slate-900">{data.items.length}</p></CardContent>
         </Card>
         <Card className="border-none shadow-sm ring-1 ring-slate-200 lg:col-span-3 bg-slate-900 text-white">
            <CardHeader className="pb-2 text-white/50"><CardDescription className="font-bold uppercase text-[10px] tracking-widest text-white/50">Total Inventory Valuation</CardDescription></CardHeader>
            <CardContent className="flex justify-between items-center">
               <p className="text-3xl font-black">₹{data.total_value.toLocaleString()}</p>
               <div className="bg-white/10 px-3 py-1 rounded-full text-xs font-bold border border-white/10">WAC BASIS</div>
            </CardContent>
         </Card>
      </div>

      <Card className="border-none shadow-sm ring-1 ring-slate-200 overflow-hidden">
        <CardHeader className="bg-slate-50/50 border-b flex flex-row items-center justify-between py-4">
           <CardTitle className="text-sm font-bold uppercase tracking-wider text-slate-700">Product Inventory Details</CardTitle>
           <Button variant="ghost" size="sm" className="text-slate-500 font-bold uppercase text-[10px] tracking-widest">
              <Filter className="mr-2 h-3 w-3" /> Advanced Filter
           </Button>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader className="bg-white border-b">
              <TableRow className="hover:bg-transparent">
                <TableHead className="font-bold text-slate-900 py-4 px-6">Product / SKU</TableHead>
                <TableHead className="text-right font-bold text-slate-900">Opening</TableHead>
                <TableHead className="text-right font-bold text-slate-900">Inward</TableHead>
                <TableHead className="text-right font-bold text-slate-900">Outward</TableHead>
                <TableHead className="text-right font-bold text-slate-900">Closing Balance</TableHead>
                <TableHead className="text-right font-bold text-slate-900">Avg Cost</TableHead>
                <TableHead className="text-right font-bold text-slate-900 px-6">Stock Value</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.items.map((item: any) => (
                <TableRow key={item.item_id} className="group hover:bg-slate-50/50 transition-colors">
                  <TableCell className="px-6 py-4">
                    <div className="flex flex-col">
                       <span className="font-bold text-slate-700 group-hover:text-blue-600 transition-colors">{item.item_name}</span>
                       <span className="text-[10px] text-slate-400 font-mono tracking-tighter uppercase">{item.item_id.split('-')[0]}</span>
                    </div>
                  </TableCell>
                  <TableCell className="text-right text-slate-500 text-xs font-mono">{item.opening_qty.toFixed(2)}</TableCell>
                  <TableCell className="text-right text-emerald-600 font-bold text-xs"><div className="flex items-center justify-end"><ArrowUpRight className="h-2.5 w-2.5 mr-1 opacity-50" /> {item.inward_qty.toFixed(2)}</div></TableCell>
                  <TableCell className="text-right text-rose-600 font-bold text-xs"><div className="flex items-center justify-end"><ArrowDownRight className="h-2.5 w-2.5 mr-1 opacity-50" /> {item.outward_qty.toFixed(2)}</div></TableCell>
                  <TableCell className="text-right">
                    <span className={cn(
                      "font-bold font-mono px-3 py-1 rounded-md text-sm",
                      item.closing_qty > 10 ? "text-slate-700 bg-slate-100" : "text-orange-700 bg-orange-50 border border-orange-100"
                    )}>
                      {item.closing_qty.toFixed(3)}
                    </span>
                  </TableCell>
                  <TableCell className="text-right font-mono text-slate-500 text-xs">₹{item.average_cost.toLocaleString()}</TableCell>
                  <TableCell className="text-right font-mono font-bold text-slate-900 px-6">₹{item.stock_value.toLocaleString()}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
