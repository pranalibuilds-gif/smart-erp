"use client";

import { useEffect, useState } from "react";
import { listInvoices } from "@/features/billing/api/billing-api";
import { Invoice, InvoiceStatus } from "@/features/billing/types";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Plus, Search, Eye, FileText } from "lucide-react";
import Link from "next/link";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";

export default function InvoicesPage() {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  useEffect(() => {
    listInvoices()
      .then(setInvoices)
      .finally(() => setLoading(false));
  }, []);

  const getStatusColor = (status: InvoiceStatus) => {
    switch (status) {
      case InvoiceStatus.POSTED: return "bg-green-100 text-green-700 hover:bg-green-100";
      case InvoiceStatus.CANCELLED: return "bg-red-100 text-red-700 hover:bg-red-100";
      default: return "bg-yellow-100 text-yellow-700 hover:bg-yellow-100";
    }
  };

  const filtered = invoices.filter(i =>
    i.invoice_number.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold">Billing & Documents</h1>
        <Button asChild>
          <Link href="/invoices/new">
            <Plus className="mr-2 h-4 w-4" /> New Document
          </Link>
        </Button>
      </div>

      <div className="mb-6 relative max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
        <Input
          placeholder="Search by number..."
          className="pl-10"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {loading ? (
        <div className="text-center py-12">Loading...</div>
      ) : (
        <div className="bg-white border rounded-lg overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Number</TableHead>
                <TableHead>Date</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Total Amount</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.map((inv) => (
                <TableRow key={inv.id} className="hover:bg-gray-50">
                  <td className="px-4 py-4 font-medium flex items-center">
                    <FileText className="h-4 w-4 mr-2 text-gray-400" />
                    {inv.invoice_number}
                  </td>
                  <td className="px-4 py-4">{inv.invoice_date}</td>
                  <td className="px-4 py-4 text-xs font-bold uppercase">{inv.document_type}</td>
                  <td className="px-4 py-4">
                    <Badge className={getStatusColor(inv.status)} variant="outline">
                      {inv.status}
                    </Badge>
                  </td>
                  <td className="px-4 py-4 text-right font-bold">₹{Number(inv.total_amount).toFixed(2)}</td>
                  <td className="px-4 py-4 text-right">
                    <Button variant="ghost" size="sm" asChild>
                      <Link href={`/invoices/${inv.id}`}>
                        <Eye className="h-4 w-4 mr-2" /> View
                      </Link>
                    </Button>
                  </td>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  );
}
