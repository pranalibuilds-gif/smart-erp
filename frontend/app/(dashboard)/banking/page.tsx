"use client";

import { useEffect, useState } from "react";
import { listBankAccounts, BankAccount } from "@/features/banking/api/banking-api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Plus, Landmark, History, CheckCircle2 } from "lucide-react";
import Link from "next/link";

export default function BankingDashboardPage() {
  const [accounts, setAccounts] = useState<BankAccount[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listBankAccounts().then(setAccounts).finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Banking & Payments</h1>
        <div className="space-x-4">
          <Button asChild variant="outline"><Link href="/banking/reconciliation"><CheckCircle2 className="mr-2 h-4 w-4" /> Reconciliation</Link></Button>
          <Button asChild><Link href="/banking/receipts/new"><Plus className="mr-2 h-4 w-4" /> New Receipt</Link></Button>
          <Button asChild><Link href="/banking/payments/new"><Plus className="mr-2 h-4 w-4" /> New Payment</Link></Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        {accounts.map(acc => (
          <Card key={acc.id}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{acc.bank_name}</CardTitle>
              <Landmark className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{acc.account_name}</div>
              <p className="text-xs text-muted-foreground">{acc.account_number}</p>
            </CardContent>
          </Card>
        ))}
        {accounts.length === 0 && !loading && (
           <Card className="border-dashed flex items-center justify-center h-32 text-gray-400">
              No bank accounts linked yet
           </Card>
        )}
      </div>

      <h2 className="text-xl font-bold mb-6">Recent Activity</h2>
      <Card>
        <CardContent className="p-12 text-center text-gray-400 flex flex-col items-center gap-4">
           <History className="h-12 w-12" />
           <p>Integrate recent payment/receipt vouchers here</p>
        </CardContent>
      </Card>
    </div>
  );
}
