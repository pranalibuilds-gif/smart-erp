"use client";

import { useEffect } from "react";
import { useCompanyStore, Company } from "@/stores/company-store";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Plus, Building2 } from "lucide-react";
import Link from "next/link";

export default function CompanySelectPage() {
  const { companies, fetchCompanies, setActiveCompany, isLoading } = useCompanyStore();
  const router = useRouter();

  useEffect(() => {
    fetchCompanies();
  }, [fetchCompanies]);

  const handleSelect = async (company: Company) => {
    setActiveCompany(company);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/companies/${company.id}/financial-years`, {
         headers: {
            'Authorization': `Bearer ${localStorage.getItem('auth-storage') ? JSON.parse(localStorage.getItem('auth-storage')!).state.accessToken : ''}`
         }
      });
      const data = await response.json();
      if (data.success && data.data.length > 0) {
        // Find latest open FY
        const openFys = data.data.filter((f: any) => !f.is_closed);
        if (openFys.length > 0) {
           useCompanyStore.getState().setActiveFY(openFys[0]);
        }
      }
    } catch (e) {
      console.error("Failed to fetch FY", e);
    }

    router.push("/dashboard");
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4 bg-gray-50">
      <div className="w-full max-w-2xl">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold">Select Company</h1>
          <Button asChild>
            <Link href="/company/create">
              <Plus className="mr-2 h-4 w-4" /> New Company
            </Link>
          </Button>
        </div>

        {isLoading ? (
          <div className="text-center py-12">Loading companies...</div>
        ) : companies.length === 0 ? (
          <Card className="text-center py-12">
            <CardContent>
              <Building2 className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <p className="text-xl font-medium text-gray-900">No companies found</p>
              <p className="text-gray-500 mb-6">Create your first company to get started</p>
              <Button asChild>
                <Link href="/company/create">Create Company</Link>
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {companies.map((company) => (
              <Card
                key={company.id}
                className="cursor-pointer hover:border-blue-500 transition-colors"
                onClick={() => handleSelect(company)}
              >
                <CardHeader className="flex flex-row items-center space-x-4 pb-2">
                  <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
                    <Building2 className="h-6 w-6 text-blue-600" />
                  </div>
                  <div>
                    <CardTitle className="text-lg">{company.name}</CardTitle>
                    <CardDescription>{company.legal_name}</CardDescription>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-500">{company.state}, {company.country}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
