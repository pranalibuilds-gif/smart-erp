"use client";

import { useEffect, useState } from "react";
import { getTrialBalance } from "@/features/reports/api/reports-api";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import Link from "next/link";

export default function TrialBalancePage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getTrialBalance()
      .then(setData)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-8">Loading...</div>;

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">Trial Balance</h1>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Ledger Name</TableHead>
                <TableHead className="text-right">Opening</TableHead>
                <TableHead className="text-right">Debit</TableHead>
                <TableHead className="text-right">Credit</TableHead>
                <TableHead className="text-right">Closing</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.items.map((item: any) => (
                <TableRow key={item.ledger_id}>
                  <TableCell>
                    <Link href={`/reports/general-ledger/${item.ledger_id}`} className="text-blue-600 hover:underline">
                      {item.ledger_name}
                    </Link>
                  </TableCell>
                  <TableCell className="text-right font-mono">{item.opening_balance.toFixed(2)}</TableCell>
                  <TableCell className="text-right font-mono text-blue-600">{item.debit_total.toFixed(2)}</TableCell>
                  <TableCell className="text-right font-mono text-purple-600">{item.credit_total.toFixed(2)}</TableCell>
                  <TableCell className="text-right font-mono font-bold">{item.closing_balance.toFixed(2)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
            <TableHeader className="bg-gray-100 font-bold">
               <TableRow>
                 <TableCell>Totals</TableCell>
                 <TableCell></TableCell>
                 <TableCell className="text-right font-mono">₹{data.total_debit.toFixed(2)}</TableCell>
                 <TableCell className="text-right font-mono">₹{data.total_credit.toFixed(2)}</TableCell>
                 <TableCell className="text-right">
                    {data.is_balanced ?
                      <span className="text-green-600">Balanced ✅</span> :
                      <span className="text-red-600">Unbalanced ❌</span>
                    }
                 </TableCell>
               </TableRow>
            </TableHeader>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
