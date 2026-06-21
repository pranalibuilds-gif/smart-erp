"use client";

import { useEffect, useState } from "react";
import { useMasterStore } from "@/stores/master-store";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { CheckCircle2, Upload } from "lucide-react";

export default function ReconciliationPage() {
  const { ledgers, fetchMasters } = useMasterStore();
  const [selectedBank, setSelectedBank] = useState("");

  useEffect(() => {
    fetchMasters();
  }, [fetchMasters]);

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Bank Reconciliation</h1>
        <Button variant="outline"><Upload className="mr-2 h-4 w-4" /> Import Statement</Button>
      </div>

      <div className="max-w-xs mb-8">
        <select
          className="w-full h-9 rounded-md border border-input bg-transparent px-3 py-1 text-sm mt-2"
          value={selectedBank}
          onChange={(e) => setSelectedBank(e.target.value)}
        >
          <option value="">Select Bank Ledger</option>
          {ledgers.map(l => <option key={l.id} value={l.id}>{l.name}</option>)}
        </select>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
         <Card>
           <CardHeader><CardTitle>Unreconciled Vouchers</CardTitle></CardHeader>
           <CardContent className="p-0">
             <Table>
               <TableHeader>
                 <TableRow>
                   <TableHead>Date</TableHead>
                   <TableHead>Ref</TableHead>
                   <TableHead className="text-right">Amount</TableHead>
                 </TableRow>
               </TableHeader>
               <TableBody>
                 <TableRow>
                   <TableCell colSpan={3} className="text-center py-8 text-gray-400">Select a bank to view vouchers</TableCell>
                 </TableRow>
               </TableBody>
             </Table>
           </CardContent>
         </Card>

         <Card>
           <CardHeader><CardTitle>Bank Statement Lines</CardTitle></CardHeader>
           <CardContent className="p-0">
             <Table>
               <TableHeader>
                 <TableRow>
                   <TableHead>Date</TableHead>
                   <TableHead>Desc</TableHead>
                   <TableHead className="text-right">Amount</TableHead>
                 </TableRow>
               </TableHeader>
               <TableBody>
                 <TableRow>
                   <TableCell colSpan={3} className="text-center py-8 text-gray-400">Import a statement to begin</TableCell>
                 </TableRow>
               </TableBody>
             </Table>
           </CardContent>
         </Card>
      </div>
    </div>
  );
}
