"use client";

import { useEffect, useState } from "react";
import apiClient from "@/lib/api-client";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function BalanceSheetPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient.get("/api/v1/reports/balance-sheet")
      .then(res => setData(res.data.data))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-8">Loading...</div>;

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">Balance Sheet</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-0 border rounded-lg overflow-hidden">
        {/* Liabilities & Equity */}
        <div className="border-r">
          <div className="p-4 bg-gray-50 border-b font-bold uppercase tracking-wider text-sm">Liabilities & Equity</div>

          <div className="p-4 bg-blue-50/30 font-semibold text-blue-800 text-xs uppercase">Equity & Reserves</div>
          <Table>
            <TableBody>
              {data.equity.groups.map((item: any, i: number) => (
                <TableRow key={i}>
                  <TableCell className="pl-6">{item.name}</TableCell>
                  <TableCell className="text-right font-mono">{item.amount.toFixed(2)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>

          <div className="p-4 bg-blue-50/30 font-semibold text-blue-800 text-xs uppercase">Liabilities</div>
          <Table>
            <TableBody>
              {data.liabilities.groups.map((item: any, i: number) => (
                <TableRow key={i}>
                  <TableCell className="pl-6">{item.name}</TableCell>
                  <TableCell className="text-right font-mono">{item.amount.toFixed(2)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
            <TableHeader className="bg-gray-100 font-bold">
               <TableRow>
                 <TableCell>Total Liabilities & Equity</TableCell>
                 <TableCell className="text-right font-mono text-lg">₹{(data.liabilities.total + data.equity.total).toFixed(2)}</TableCell>
               </TableRow>
            </TableHeader>
          </Table>
        </div>

        {/* Assets */}
        <div>
          <div className="p-4 bg-gray-50 border-b font-bold uppercase tracking-wider text-sm">Assets</div>
          <Table>
            <TableBody>
              {data.assets.groups.map((item: any, i: number) => (
                <TableRow key={i}>
                  <TableCell className="pl-6">{item.name}</TableCell>
                  <TableCell className="text-right font-mono">{item.amount.toFixed(2)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
            <TableHeader className="bg-gray-100 font-bold">
               <TableRow>
                 <TableCell>Total Assets</TableCell>
                 <TableCell className="text-right font-mono text-lg">₹{data.assets.total.toFixed(2)}</TableCell>
               </TableRow>
            </TableHeader>
          </Table>
        </div>
      </div>

      {!data.is_balanced && (
        <div className="mt-4 p-4 bg-red-100 text-red-700 rounded-md font-medium text-center">
          ⚠️ Balance Sheet is not balanced. Please check for discrepancies in accounting entries.
        </div>
      )}
    </div>
  );
}
