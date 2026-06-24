"use client";

import { useEffect, useState } from "react";
import { usePartyStore } from "@/stores/party-store";
import { Button, buttonVariants } from "@/components/ui/button";
import { Plus, Search, Filter, Pencil, Trash2, Users, ChevronRight, UserCircle2 } from "lucide-react";
import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { cn } from "@/lib/utils";

export default function PartiesPage() {
  const { parties, fetchParties, isLoading } = usePartyStore();
  const [filter, setFilter] = useState("all");
  const [search, setSearch] = useState("");

  useEffect(() => {
    fetchParties(filter);
  }, [fetchParties, filter]);

  const filteredParties = parties.filter(p =>
    p.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="p-10 max-w-[1500px] mx-auto space-y-10 pb-32">
      <div className="flex justify-between items-center mb-10">
        <div>
           <h1 className="text-3xl font-black tracking-tight text-slate-900 uppercase italic">Parties Registry</h1>
           <p className="text-slate-500 font-medium mt-1 uppercase text-[10px] tracking-widest italic">Directory of active customers and vendor partners</p>
        </div>
        <Link href="/parties/new" className={cn(buttonVariants(), "bg-blue-600 hover:bg-blue-700 h-12 px-10 rounded-2xl font-black uppercase tracking-widest shadow-2xl shadow-blue-500/30 ring-4 ring-blue-100 transition-all active:scale-95")}>
          <Plus className="mr-2 h-5 w-5 stroke-[3]" /> Add New Party
        </Link>
      </div>

      <div className="bg-white border border-slate-200 rounded-[32px] shadow-sm overflow-hidden ring-1 ring-slate-200/60">
        <div className="p-8 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
           <div className="relative flex-1 max-w-xl group">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-300 group-focus-within:text-blue-600 transition-colors" />
              <input
                placeholder="Identify party by name or entity title..."
                className="w-full pl-12 h-14 border-none bg-transparent outline-none font-bold text-slate-700 placeholder:text-slate-200 transition-all uppercase text-xs tracking-widest"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
           </div>
           <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 bg-white border border-slate-200 p-1.5 rounded-2xl shadow-sm">
                {['all', 'customer', 'supplier'].map(t => (
                  <button key={t} onClick={() => setFilter(t)} className={cn("px-5 py-2 text-[10px] font-black uppercase tracking-widest rounded-xl transition-all", filter === t ? "bg-blue-600 text-white shadow-lg shadow-blue-600/20" : "text-slate-400 hover:text-slate-900")}>
                    {t}
                  </button>
                ))}
              </div>
              <Button variant="ghost" size="icon" className="h-12 w-12 rounded-2xl border border-slate-100 text-slate-400 hover:text-blue-600 transition-all"><Filter className="h-5 w-5" /></Button>
           </div>
        </div>

        <Table>
          <TableHeader className="bg-slate-50/30">
            <TableRow className="hover:bg-transparent border-b border-slate-100">
              <TableHead className="font-black text-slate-500 uppercase tracking-widest py-8 px-12 text-[10px] w-1/3">Name</TableHead>
              <TableHead className="font-black text-slate-500 uppercase tracking-widest text-[10px]">Type</TableHead>
              <TableHead className="font-black text-slate-500 uppercase tracking-widest text-[10px]">GSTIN</TableHead>
              <TableHead className="font-black text-slate-500 uppercase tracking-widest text-[10px]">Phone</TableHead>
              <TableHead className="w-24"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
               [...Array(6)].map((_, i) => (
                 <TableRow key={i} className="animate-pulse"><TableCell colSpan={5} className="h-24 px-12" /></TableRow>
               ))
            ) : filteredParties.map((party) => (
              <TableRow key={party.id} className="group hover:bg-blue-50/30 transition-all border-b last:border-0 border-slate-50 h-24">
                <TableCell className="px-12 whitespace-nowrap">
                   <div className="flex items-center gap-6">
                      <div className="h-12 w-12 rounded-2xl bg-white border border-slate-100 shadow-sm flex items-center justify-center group-hover:scale-110 transition-transform duration-500 ring-4 ring-slate-50 overflow-hidden">
                         <img src={`https://i.pravatar.cc/100?u=${party.id}`} className="h-full w-full object-cover grayscale group-hover:grayscale-0 transition-all" alt="avatar" />
                      </div>
                      <div className="flex flex-col">
                        <span className="font-black text-slate-900 group-hover:text-blue-600 transition-colors uppercase tracking-tight text-base italic leading-none">{party.name}</span>
                        <span className="text-[10px] text-slate-400 font-bold uppercase tracking-[0.1em] mt-1.5">{party.legal_name || "Nexus Business Group"}</span>
                      </div>
                   </div>
                </TableCell>
                <TableCell>
                   <div className="flex gap-1.5">
                    {party.is_customer && <Badge variant="secondary" className="bg-blue-600 text-white border-blue-700 font-black text-[9px] uppercase px-3 shadow-blue-500/20 shadow-lg">CUST</Badge>}
                    {party.is_supplier && <Badge variant="secondary" className="bg-indigo-600 text-white border-indigo-700 font-black text-[9px] uppercase px-3 shadow-indigo-500/20 shadow-lg">VEND</Badge>}
                   </div>
                </TableCell>
                <TableCell className="font-mono text-xs font-black text-slate-500 italic tracking-tighter">{party.gst_number || "UNREGISTERED"}</TableCell>
                <TableCell className="font-bold text-slate-600 text-sm tracking-tight">{party.phone || party.mobile || "—"}</TableCell>
                <TableCell className="px-10">
                   <div className="flex justify-end gap-3 opacity-0 group-hover:opacity-100 group-hover:translate-x-0 translate-x-4 transition-all duration-300">
                      <Link href={`/parties/${party.id}`} className={cn(buttonVariants({ variant: "ghost", size: "icon" }), "h-11 w-11 rounded-2xl bg-white border border-slate-200 shadow-sm hover:text-blue-600 hover:border-blue-300 transition-all hover:shadow-lg")}>
                        <ChevronRight className="h-5 w-5" />
                      </Link>
                   </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>

        <div className="p-10 bg-slate-900 text-white flex justify-between items-center shadow-2xl relative z-10 border-t-8 border-blue-600">
           <div className="flex items-center gap-4">
              <div className="h-10 w-10 rounded-xl bg-blue-600 flex items-center justify-center shadow-lg shadow-blue-500/30">
                 <Users className="h-5 w-5" />
              </div>
              <span className="font-black text-xs uppercase tracking-[0.4em] text-blue-400 italic">Total Registered Stakeholders</span>
           </div>
           <span className="text-4xl font-black tracking-tighter">{parties.length < 10 ? `0${parties.length}` : parties.length}</span>
        </div>
      </div>
    </div>
  );
}
