"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { Command } from "cmdk";
import {
  Search,
  FileText,
  Plus,
  Users,
  Receipt,
  BarChart3,
  Package,
  Settings,
  Building2
} from "lucide-react";
import { searchGlobal, SearchResult } from "@/features/search/api/search-api";
import { cn } from "@/lib/utils";

export function CommandPalette() {
  const [open, setOpen] = React.useState(false);
  const [query, setQuery] = React.useState("");
  const [results, setResults] = React.useState<SearchResult[]>([]);
  const [loading, setLoading] = React.useState(false);
  const router = useRouter();

  React.useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen((open) => !open);
      }
    };

    document.addEventListener("keydown", down);
    return () => document.removeEventListener("keydown", down);
  }, []);

  React.useEffect(() => {
    if (!query) {
      setResults([]);
      return;
    }

    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        const data = await searchGlobal(query);
        setResults(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [query]);

  const runCommand = React.useCallback((command: () => void) => {
    setOpen(false);
    command();
  }, []);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-24 sm:pt-40 px-4 bg-slate-900/50 backdrop-blur-sm" onClick={() => setOpen(false)}>
      <Command
        className="w-full max-w-2xl bg-white rounded-xl shadow-2xl border overflow-hidden"
        onClick={(e) => e.stopPropagation()}
        loop
      >
        <div className="flex items-center px-4 border-b">
          <Search className="h-5 w-5 text-slate-400" />
          <Command.Input
            autoFocus
            placeholder="Search anything or type a command... (Ctrl+K)"
            className="flex-1 h-12 bg-transparent border-none outline-none text-sm px-4"
            value={query}
            onValueChange={setQuery}
          />
        </div>

        <Command.List className="max-h-[300px] overflow-y-auto p-2 scroll-py-2">
          {loading && <div className="p-4 text-center text-sm text-slate-500">Searching...</div>}

          <Command.Empty className="p-4 text-center text-sm text-slate-500">
            No results found.
          </Command.Empty>

          {results.length > 0 && (
            <Command.Group heading="Global Search" className="px-2 py-1 text-xs font-bold text-slate-500 uppercase tracking-wider">
              {results.map((res) => (
                <Command.Item
                  key={res.id}
                  className="flex items-center gap-3 p-3 rounded-lg hover:bg-slate-100 cursor-pointer select-none"
                  onSelect={() => runCommand(() => router.push(res.url))}
                >
                  <div className="bg-slate-100 p-2 rounded text-slate-600">
                    {res.entity_type === 'INVOICE' && <FileText className="h-4 w-4" />}
                    {res.entity_type === 'PARTY' && <Users className="h-4 w-4" />}
                    {res.entity_type === 'STOCK_ITEM' && <Package className="h-4 w-4" />}
                    {res.entity_type === 'VOUCHER' && <Receipt className="h-4 w-4" />}
                    {res.entity_type === 'LEDGER' && <Building2 className="h-4 w-4" />}
                  </div>
                  <div>
                    <p className="text-sm font-medium">{res.title}</p>
                    <p className="text-xs text-slate-500">{res.subtitle}</p>
                  </div>
                </Command.Item>
              ))}
            </Command.Group>
          )}

          {!query && (
            <>
              <Command.Group heading="Navigation" className="px-2 py-1 mt-2 text-xs font-bold text-slate-500 uppercase tracking-wider">
                <Command.Item className="flex items-center gap-3 p-3 rounded-lg hover:bg-slate-100 cursor-pointer select-none" onSelect={() => runCommand(() => router.push("/dashboard"))}>
                  <Building2 className="h-4 w-4 text-slate-400" />
                  <span className="text-sm">Go to Dashboard</span>
                </Command.Item>
                <Command.Item className="flex items-center gap-3 p-3 rounded-lg hover:bg-slate-100 cursor-pointer select-none" onSelect={() => runCommand(() => router.push("/reports/trial-balance"))}>
                  <BarChart3 className="h-4 w-4 text-slate-400" />
                  <span className="text-sm">Open Trial Balance</span>
                </Command.Item>
              </Command.Group>

              <Command.Group heading="Actions" className="px-2 py-1 mt-2 text-xs font-bold text-slate-500 uppercase tracking-wider">
                <Command.Item className="flex items-center gap-3 p-3 rounded-lg hover:bg-slate-100 cursor-pointer select-none" onSelect={() => runCommand(() => router.push("/invoices/new"))}>
                  <Plus className="h-4 w-4 text-green-500" />
                  <span className="text-sm">Create New Invoice</span>
                </Command.Item>
                <Command.Item className="flex items-center gap-3 p-3 rounded-lg hover:bg-slate-100 cursor-pointer select-none" onSelect={() => runCommand(() => router.push("/vouchers/new"))}>
                  <Plus className="h-4 w-4 text-blue-500" />
                  <span className="text-sm">Create New Voucher</span>
                </Command.Item>
              </Command.Group>
            </>
          )}
        </Command.List>
      </Command>
    </div>
  );
}
