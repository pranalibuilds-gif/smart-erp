"use client";

import { useEffect, useState } from "react";
import apiClient from "@/lib/api-client";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Card, CardContent } from "@/components/ui/card";
import { Button, buttonVariants } from "@/components/ui/button";
import { Plus, Search, Filter, Pencil, Trash2, Building2 } from "lucide-react";
import Link from "next/link";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";

export default function LedgersPage() {
  const [ledgers, setLedgers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  useEffect(() => {
    apiClient.get("/api/v1/masters/ledgers")
      .then(res => setLedgers(res.data.data))
      .finally(() => setLoading(false));
  }, []);

  const filtered = ledgers.filter(l =>
    l.name.toLowerCase().includes(search.toLowerCase()) ||
    (l.code && l.code.toLowerCase().includes(search.toLowerCase()))
  );

  return (
    <div className="p-8 max-w-[1400px] mx-auto space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">Chart of Accounts</h1>
          <p className="text-slate-500 mt-1 font-medium text-sm">Manage all account ledgers and opening balances</p>
        </div>
        <Link href="/masters/ledgers/new" className={cn(buttonVariants(), "bg-blue-600 hover:bg-blue-700 shadow-lg shadow-blue-600/20")}>
          <Plus className="mr-2 h-4 w-4" /> Add Ledger
        </Link>
      </div>

      <Card className="border-none shadow-sm ring-1 ring-slate-200">
        <CardContent className="p-4 flex flex-col md:flex-row justify-between gap-4">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
            <input
              placeholder="Search by name or account code..."
              className="w-full pl-10 h-10 border border-slate-200 rounded-lg outline-none bg-slate-50/50 focus:bg-white focus:ring-2 focus:ring-blue-500/10 transition-all text-sm"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <Button variant="ghost" className="text-xs font-bold uppercase tracking-widest text-slate-500 hover:text-slate-900">
             <Filter className="mr-2 h-3.5 w-3.5" /> Filter by Group
          </Button>
        </CardContent>
      </Card>

      <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
        <Table>
          <TableHeader className="bg-slate-50/50 border-b">
            <TableRow className="hover:bg-transparent">
              <TableHead className="font-bold text-slate-900 py-4 px-6 w-1/4">Account Name</TableHead>
              <TableHead className="font-bold text-slate-900">Group</TableHead>
              <TableHead className="font-bold text-slate-900">Code</TableHead>
              <TableHead className="font-bold text-slate-900 text-right">Current Balance (₹)</TableHead>
              <TableHead className="font-bold text-slate-900 text-right px-6">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              [...Array(5)].map((_, i) => (
                <TableRow key={i} className="animate-pulse"><TableCell colSpan={5} className="h-16" /></TableRow>
              ))
            ) : filtered.map((l) => (
              <TableRow key={l.id} className="group hover:bg-slate-50/50 transition-colors border-b last:border-0 border-slate-100">
                <TableCell className="px-6 py-4">
                   <span className="font-bold text-slate-700 group-hover:text-blue-600 transition-colors">{l.name}</span>
                </TableCell>
                <TableCell>
                   <Badge variant="outline" className="text-[10px] font-bold text-slate-500 bg-slate-50 border-slate-200 uppercase tracking-widest">{l.group_name || "General"}</Badge>
                </TableCell>
                <TableCell className="font-mono text-xs text-slate-400 font-bold">{l.code || "—"}</TableCell>
                <TableCell className="text-right font-mono font-bold text-slate-900">
                   {Math.abs(l.current_balance).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                   <span className="text-[10px] ml-1 opacity-40 uppercase font-black">{l.current_balance >= 0 ? 'Dr' : 'Cr'}</span>
                </TableCell>
                <TableCell className="text-right px-6">
                   <div className="flex justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <Button variant="ghost" size="icon" className="h-8 w-8 text-slate-400 hover:text-blue-600 hover:bg-blue-50"><Pencil className="h-4 w-4" /></Button>
                      {!l.is_system && <Button variant="ghost" size="icon" className="h-8 w-8 text-slate-400 hover:text-red-600 hover:bg-red-50"><Trash2 className="h-4 w-4" /></Button>}
                   </div>
                </TableCell>
              </TableRow>
            ))}
            {!loading && filtered.length === 0 && (
              <TableRow>
                <TableCell colSpan={5} className="h-40 text-center py-20 text-slate-400">
                   <div className="flex flex-col items-center gap-3">
                      <Building2 className="h-10 w-10 opacity-20" />
                      <p className="font-medium italic">No ledger accounts found matching your search</p>
                   </div>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
