"use client";

import { useEffect, useState } from "react";
import apiClient from "@/lib/api-client";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button, buttonVariants } from "@/components/ui/button";
import { Plus, Warehouse, MapPin, Package, ArrowUpRight, BarChart3, Settings } from "lucide-react";
import Link from "next/link";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";

export default function WarehousesPage() {
  const [warehouses, setWarehouses] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient.get("/api/v1/masters/warehouses")
      .then(res => setWarehouses(res.data.data))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 pb-20">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div className="flex items-center gap-4">
           <div className="bg-blue-600 p-3 rounded-2xl shadow-lg shadow-blue-600/20 text-white">
              <Warehouse className="h-6 w-6" />
           </div>
           <div>
              <h1 className="text-3xl font-bold tracking-tight text-slate-900">Physical Warehouses</h1>
              <p className="text-slate-500 mt-1">Manage physical storage locations and intra-warehouse movement</p>
           </div>
        </div>
        <Link href="/inventory/warehouses/new" className={cn(buttonVariants(), "bg-blue-600 hover:bg-blue-700 shadow-lg shadow-blue-600/20 px-6 font-bold")}>
          <Plus className="mr-2 h-4 w-4" /> Add Warehouse
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {loading ? (
          [1, 2].map(i => <Card key={i} className="h-48 animate-pulse bg-slate-50 border-none" />)
        ) : warehouses.map((wh) => (
          <Card key={wh.id} className="group border-none shadow-sm ring-1 ring-slate-200 hover:ring-blue-500 hover:shadow-xl transition-all duration-300 overflow-hidden">
            <CardHeader className="bg-slate-50/50 border-b flex flex-row items-start justify-between py-5 px-6">
               <div className="space-y-1">
                  <CardTitle className="text-xl font-black text-slate-900">{wh.name}</CardTitle>
                  <CardDescription className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-widest text-slate-400">
                     <MapPin className="h-3 w-3" /> {wh.location || "Central Zone"}
                  </CardDescription>
               </div>
               <Badge variant="outline" className="bg-white text-blue-600 border-blue-100 font-black text-[10px]">ACTIVE</Badge>
            </CardHeader>
            <CardContent className="pt-6 px-6 pb-6">
               <div className="flex justify-between items-end">
                  <div className="space-y-4">
                     <div>
                        <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1">Stock Handling</p>
                        <div className="flex items-center gap-2">
                           <Package className="h-4 w-4 text-slate-300" />
                           <span className="text-sm font-bold text-slate-700">Multi-SKU Optimized</span>
                        </div>
                     </div>
                     <div className="flex gap-2">
                        <Link href={`/reports/stock-by-warehouse?warehouse_id=${wh.id}`} className={cn(buttonVariants({variant: 'ghost', size: 'sm'}), "text-[10px] font-black uppercase tracking-widest bg-slate-50 hover:bg-blue-600 hover:text-white border border-slate-100 transition-all px-3")}>
                           <BarChart3 className="h-3 w-3 mr-1.5" /> Analytics
                        </Link>
                        <Link href={`/inventory/transfers/new?from=${wh.id}`} className={cn(buttonVariants({variant: 'ghost', size: 'sm'}), "text-[10px] font-black uppercase tracking-widest bg-slate-50 hover:bg-blue-600 hover:text-white border border-slate-100 transition-all px-3")}>
                           <ArrowUpRight className="h-3 w-3 mr-1.5" /> Transfer
                        </Link>
                     </div>
                  </div>
                  <Button variant="ghost" size="icon" className="h-10 w-10 text-slate-300 hover:text-blue-600 hover:bg-blue-50 rounded-xl"><Settings className="h-5 w-5" /></Button>
               </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {!loading && warehouses.length === 0 && (
         <div className="py-24 flex flex-col items-center gap-6 text-center border-2 border-dashed rounded-3xl bg-slate-50/50">
            <div className="bg-white p-6 rounded-full shadow-sm">
               <Warehouse className="h-12 w-12 text-slate-200" />
            </div>
            <div>
               <p className="text-xl font-bold text-slate-900">No Warehouses Configured</p>
               <p className="text-slate-500 max-w-xs mx-auto mt-1">Add storage locations to begin tracking inventory across different physical zones.</p>
            </div>
            <Link href="/inventory/warehouses/new" className={cn(buttonVariants(), "bg-blue-600 hover:bg-blue-700 h-11 px-8 font-bold")}>Setup Primary Warehouse</Link>
         </div>
      )}
    </div>
  );
}
