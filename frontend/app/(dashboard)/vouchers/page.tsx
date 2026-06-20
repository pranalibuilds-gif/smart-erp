"use client";

import { useEffect, useState } from "react";
import { listVouchers } from "@/features/vouchers/api/vouchers-api";
import { Voucher, VoucherStatus } from "@/features/vouchers/types";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Plus, Search, Eye } from "lucide-react";
import Link from "next/link";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";

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
      case VoucherStatus.POSTED: return "bg-green-100 text-green-700 hover:bg-green-100";
      case VoucherStatus.CANCELLED: return "bg-red-100 text-red-700 hover:bg-red-100";
      default: return "bg-yellow-100 text-yellow-700 hover:bg-yellow-100";
    }
  };

  const filteredVouchers = vouchers.filter(v =>
    v.voucher_number.toLowerCase().includes(search.toLowerCase()) ||
    v.narration?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold">Vouchers</h1>
        <Button asChild>
          <Link href="/vouchers/new">
            <Plus className="mr-2 h-4 w-4" /> New Voucher
          </Link>
        </Button>
      </div>

      <div className="mb-6 relative max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
        <Input
          placeholder="Search voucher number or narration..."
          className="pl-10"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {loading ? (
        <div className="text-center py-12">Loading vouchers...</div>
      ) : (
        <div className="bg-white border rounded-lg overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Number</TableHead>
                <TableHead>Date</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Narration</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredVouchers.map((v) => (
                <TableRow key={v.id} className="hover:bg-gray-50">
                  <td className="px-4 py-4 font-medium">{v.voucher_number}</td>
                  <td className="px-4 py-4">{v.voucher_date}</td>
                  <td className="px-4 py-4 text-xs font-bold uppercase">{v.voucher_type}</td>
                  <td className="px-4 py-4">
                    <Badge className={getStatusColor(v.status)} variant="outline">
                      {v.status}
                    </Badge>
                  </td>
                  <td className="px-4 py-4 text-gray-500 max-w-xs truncate">{v.narration}</td>
                  <td className="px-4 py-4 text-right">
                    <Button variant="ghost" size="sm" asChild>
                      <Link href={`/vouchers/${v.id}`}>
                        <Eye className="h-4 w-4 mr-2" /> View
                      </Link>
                    </Button>
                  </td>
                </TableRow>
              ))}
              {filteredVouchers.length === 0 && (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-12 text-gray-500">
                    No vouchers found
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  );
}
