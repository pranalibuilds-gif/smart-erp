"use client";

import { useEffect, useState } from "react";
import apiClient from "@/lib/api-client";
import { useCompanyStore } from "@/stores/company-store";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Settings, Calendar, Lock, Unlock, ArrowRight, CheckCircle2, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";

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
    <div className="p-8 max-w-5xl mx-auto space-y-8">
      <div className="flex items-center gap-4">
         <div className="bg-slate-900 p-3 rounded-2xl shadow-lg shadow-slate-900/20 text-white">
            <Calendar className="h-6 w-6" />
         </div>
         <div>
            <h1 className="text-3xl font-bold tracking-tight text-slate-900">Financial Periods</h1>
            <p className="text-slate-500 mt-1">Manage reporting cycles and year-end closing for {currentCompany.name}</p>
         </div>
      </div>

      <div className="grid gap-6">
        {years.map((year) => (
          <Card key={year.id} className={cn(
            "border-none shadow-sm ring-1 transition-all",
            year.is_closed ? "ring-slate-200 bg-slate-50/50 opacity-80" : "ring-blue-600 shadow-xl shadow-blue-600/5 bg-white scale-[1.02]"
          )}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-6 border-b">
              <div className="flex items-center gap-4">
                 <div className={cn("p-2.5 rounded-xl", year.is_closed ? "bg-slate-200 text-slate-500" : "bg-blue-600 text-white")}>
                    {year.is_closed ? <Lock className="h-5 w-5" /> : <Unlock className="h-5 w-5" />}
                 </div>
                 <div>
                    <CardTitle className="text-xl font-black">{year.name}</CardTitle>
                    <CardDescription className="font-medium flex items-center gap-2 mt-0.5">
                       {year.start_date} <ArrowRight className="h-3 w-3" /> {year.end_date}
                    </CardDescription>
                 </div>
              </div>
              <Badge variant={year.is_closed ? "secondary" : "default"} className={cn(
                "px-4 py-1 font-bold text-xs tracking-widest uppercase",
                !year.is_closed && "bg-blue-600 hover:bg-blue-600 shadow-md shadow-blue-200"
              )}>
                {year.is_closed ? "Audit Complete / Closed" : "Open for Posting"}
              </Badge>
            </CardHeader>
            <CardContent className="flex flex-col md:flex-row justify-between items-center py-6 gap-6">
              <div className="flex flex-wrap gap-8">
                 <div className="space-y-1">
                    <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Transactions</p>
                    <div className="flex items-center gap-2">
                       {year.is_closed ? <CheckCircle2 className="h-4 w-4 text-emerald-500" /> : <CheckCircle2 className="h-4 w-4 text-blue-500 opacity-20" />}
                       <span className="text-sm font-bold text-slate-700">{year.is_closed ? "Locked & Finalized" : "Entries Permitted"}</span>
                    </div>
                 </div>
                 <div className="space-y-1">
                    <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Reporting</p>
                    <div className="flex items-center gap-2">
                       <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                       <span className="text-sm font-bold text-slate-700">Financials Generated</span>
                    </div>
                 </div>
              </div>

              {!year.is_closed && (
                <Button
                  onClick={() => handleClose(year.id)}
                  className="bg-rose-600 hover:bg-rose-700 shadow-lg shadow-rose-200 h-11 px-6 font-bold"
                >
                  Close FY & Rollover Balances
                </Button>
              )}
              {year.is_closed && (
                 <Button variant="outline" className="bg-white border-slate-200 font-bold h-11 px-6">View Closure Report</Button>
              )}
            </CardContent>
          </Card>
        ))}

        {loading && <div className="text-center py-20 text-slate-400 animate-pulse font-medium uppercase tracking-[0.2em] text-xs">Loading periods...</div>}
        {!loading && years.length === 0 && (
           <div className="py-20 text-center border border-dashed rounded-2xl bg-slate-50 flex flex-col items-center gap-4">
              <Calendar className="h-10 w-10 text-slate-200" />
              <p className="text-slate-400 font-bold uppercase tracking-widest text-[10px]">No historical data found</p>
           </div>
        )}
      </div>
    </div>
  );
}
