"use client";

import { useEffect, useState } from "react";
import { usePartyStore } from "@/stores/party-store";
import { Button } from "@/components/ui/button";
import { Plus, Search, Filter } from "lucide-react";
import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

export default function PartiesPage() {
  const { parties, fetchParties, isLoading } = usePartyStore();
  const [filter, setFilter] = useState("all");
  const [search, setSearch] = useState("");

  useEffect(() => {
    fetchParties(filter);
  }, [fetchParties, filter]);

  const filteredParties = parties.filter(p =>
    p.name.toLowerCase().includes(search.toLowerCase()) ||
    p.mobile?.includes(search) ||
    p.gstin?.includes(search)
  );

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold">Parties</h1>
        <Button asChild>
          <Link href="/parties/new">
            <Plus className="mr-2 h-4 w-4" /> New Party
          </Link>
        </Button>
      </div>

      <div className="flex gap-4 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search by name, mobile, or GSTIN..."
            className="pl-10"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <select
          className="px-4 py-2 border rounded-md"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        >
          <option value="all">All Parties</option>
          <option value="customer">Customers</option>
          <option value="supplier">Suppliers</option>
          <option value="both">Both</option>
        </select>
      </div>

      {isLoading ? (
        <div className="text-center py-12">Loading parties...</div>
      ) : filteredParties.length === 0 ? (
        <Card className="text-center py-12">
          <CardContent>
            <p className="text-gray-500">No parties found</p>
          </CardContent>
        </Card>
      ) : (
        <div className="bg-white border rounded-lg overflow-hidden">
          <table className="w-full text-left">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="px-6 py-3 text-sm font-semibold text-gray-900">Name</th>
                <th className="px-6 py-3 text-sm font-semibold text-gray-900">Mobile</th>
                <th className="px-6 py-3 text-sm font-semibold text-gray-900">GSTIN</th>
                <th className="px-6 py-3 text-sm font-semibold text-gray-900">Type</th>
                <th className="px-6 py-3 text-sm font-semibold text-gray-900">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {filteredParties.map((party) => (
                <tr key={party.id} className="hover:bg-gray-50 cursor-pointer">
                  <td className="px-6 py-4">
                    <div className="font-medium text-gray-900">{party.name}</div>
                    <div className="text-xs text-gray-500">{party.display_name}</div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">{party.mobile || "-"}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{party.gstin || "-"}</td>
                  <td className="px-6 py-4">
                    <div className="flex gap-1">
                      {party.is_customer && <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-[10px] uppercase font-bold">Cust</span>}
                      {party.is_supplier && <span className="px-2 py-0.5 bg-purple-100 text-purple-700 rounded text-[10px] uppercase font-bold">Supp</span>}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded-full text-xs ${party.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                      {party.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
