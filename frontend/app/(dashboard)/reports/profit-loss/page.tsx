"use client";

import { useEffect, useState } from "react";
import apiClient from "@/lib/api-client";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function ProfitLossPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient.get("/api/v1/reports/profit-loss")
      .then(res => setData(res.data.data))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-8">Loading...</div>;

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">Profit & Loss Statement</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
        <Card>
          <CardHeader className="bg-green-50"><CardTitle className="text-green-700">Income</CardTitle></CardHeader>
          <CardContent className="p-0">
            <Table>
               <TableBody>
                  {data.income.map((item: any, i: number) => (
                    <TableRow key={i}>
                       <TableCell>{item.name}</TableCell>
                       <TableCell className="text-right font-mono">{item.amount.toFixed(2)}</TableCell>
                    </TableRow>
                  ))}
               </TableBody>
               <TableHeader className="bg-gray-50 font-bold">
                  <TableRow>
                    <TableCell>Total Income</TableCell>
                    <TableCell className="text-right font-mono">₹{data.total_income.toFixed(2)}</TableCell>
                  </TableRow>
               </TableHeader>
            </Table>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="bg-red-50"><CardTitle className="text-red-700">Expenses</CardTitle></CardHeader>
          <CardContent className="p-0">
            <Table>
               <TableBody>
                  {data.expenses.map((item: any, i: number) => (
                    <TableRow key={i}>
                       <TableCell>{item.name}</TableCell>
                       <TableCell className="text-right font-mono">{item.amount.toFixed(2)}</TableCell>
                    </TableRow>
                  ))}
               </TableBody>
               <TableHeader className="bg-gray-50 font-bold">
                  <TableRow>
                    <TableCell>Total Expenses</TableCell>
                    <TableCell className="text-right font-mono">₹{data.total_expenses.toFixed(2)}</TableCell>
                  </TableRow>
               </TableHeader>
            </Table>
          </CardContent>
        </Card>
      </div>

      <Card className={`border-2 ${data.net_profit >= 0 ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}`}>
         <CardContent className="p-6 flex justify-between items-center">
            <span className="text-xl font-bold">{data.net_profit >= 0 ? 'Net Profit' : 'Net Loss'}</span>
            <span className={`text-3xl font-bold font-mono ${data.net_profit >= 0 ? 'text-green-700' : 'text-red-700'}`}>
               ₹{Math.abs(data.net_profit).toFixed(2)}
            </span>
         </CardContent>
      </Card>
    </div>
  );
}
