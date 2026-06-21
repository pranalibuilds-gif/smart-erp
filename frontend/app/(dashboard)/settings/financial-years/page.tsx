"use client";

import { useEffect, useState } from "react";
import apiClient from "@/lib/api-client";
import { useCompanyStore } from "@/stores/company-store";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AlertCircle, CheckCircle2 } from "lucide-react";

export default function FinancialYearsPage() {
  const { currentCompany } = useCompanyStore();
  const [years, setYears] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchYears = async () => {
    if (!currentCompany) return;
    setLoading(true);
    try {
      const res = await apiClient.get(`/api/v1/companies/${currentCompany.id}/financial-years`);
      setYears(res.data.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchYears();
  }, [currentCompany]);

  const handleClose = async (id: string) => {
    if (!confirm("Are you sure you want to close this financial year? This will carry forward balances to the next year and lock this period permanently.")) return;

    try {
      await apiClient.post(`/api/v1/companies/${currentCompany?.id}/financial-years/${id}/close`);
      alert("Financial year closed and next year created successfully!");
      fetchYears();
    } catch (err: any) {
      alert(err.response?.data?.detail || "Failed to close year");
    }
  };

  if (!currentCompany) return <div className="p-8">Please select a company first</div>;

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">Financial Years</h1>

      <div className="grid gap-6">
        {years.map((year) => (
          <Card key={year.id} className={year.is_closed ? "opacity-75" : "border-blue-200 shadow-md"}>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-xl">{year.name}</CardTitle>
                <p className="text-sm text-gray-500 mt-1">
                  {year.start_date} to {year.end_date}
                </p>
              </div>
              <Badge variant={year.is_closed ? "secondary" : "default"} className="px-3 py-1">
                {year.is_closed ? "CLOSED" : "ACTIVE"}
              </Badge>
            </CardHeader>
            <CardContent className="flex justify-between items-center border-t pt-4">
              <div className="flex gap-4">
                 <div className="flex items-center gap-2 text-sm">
                    {year.is_closed ? <CheckCircle2 className="h-4 w-4 text-green-500" /> : <AlertCircle className="h-4 w-4 text-blue-500" />}
                    <span>{year.is_closed ? "Transactions locked" : "Transactions open"}</span>
                 </div>
              </div>
              {!year.is_closed && (
                <Button variant="destructive" onClick={() => handleClose(year.id)}>Close Year & Rollover</Button>
              )}
            </CardContent>
          </Card>
        ))}

        {loading && <div>Loading years...</div>}
        {!loading && years.length === 0 && <div>No financial years found</div>}
      </div>
    </div>
  );
}
