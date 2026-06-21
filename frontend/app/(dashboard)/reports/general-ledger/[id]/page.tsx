"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { getGeneralLedger } from "@/features/reports/api/reports-api";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function GeneralLedgerPage() {
  const { id } = useParams();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getGeneralLedger(id as string)
      .then(setData)
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="p-8">Loading...</div>;

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-2">{data.ledger_name}</h1>
      <p className="text-gray-500 mb-8">General Ledger Statement</p>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Date</TableHead>
                <TableHead>Voucher No</TableHead>
                <TableHead>Narration</TableHead>
                <TableHead className="text-right">Debit</TableHead>
                <TableHead className="text-right">Credit</TableHead>
                <TableHead className="text-right">Balance</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow className="bg-gray-50 font-medium italic">
                 <TableCell colSpan={5}>Opening Balance</TableCell>
                 <TableCell className="text-right font-mono">{data.opening_balance.toFixed(2)}</TableCell>
              </TableRow>
              {data.entries.map((entry: any, i: number) => (
                <TableRow key={i}>
                  <TableCell>{entry.date}</TableCell>
                  <TableCell className="font-medium">{entry.voucher_number}</TableCell>
                  <TableCell className="text-gray-500 text-sm">{entry.narration}</TableCell>
                  <TableCell className="text-right font-mono text-blue-600">{entry.debit > 0 ? entry.debit.toFixed(2) : "-"}</TableCell>
                  <TableCell className="text-right font-mono text-purple-600">{entry.credit > 0 ? entry.credit.toFixed(2) : "-"}</TableCell>
                  <TableCell className="text-right font-mono font-bold">{entry.running_balance.toFixed(2)}</TableCell>
                </TableRow>
              ))}
              {data.entries.length === 0 && (
                <TableRow>
                   <TableCell colSpan={6} className="text-center py-8 text-gray-400">No transactions found in this period</TableCell>
                </TableRow>
              )}
            </TableBody>
            <TableHeader className="bg-gray-100 font-bold">
               <TableRow>
                 <TableCell colSpan={5} className="text-right">Closing Balance</TableCell>
                 <TableCell className="text-right font-mono text-lg text-blue-700">₹{data.closing_balance.toFixed(2)}</TableCell>
               </TableRow>
            </TableHeader>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
