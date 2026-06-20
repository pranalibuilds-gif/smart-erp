"use client";

import { useAuthStore } from "@/stores/auth-store";
import { useCompanyStore } from "@/stores/company-store";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useRouter } from "next/navigation";

export default function DashboardPage() {
  const { user, logout } = useAuthStore();
  const { activeCompany, setActiveCompany } = useCompanyStore();
  const router = useRouter();

  const handleSwitchCompany = () => {
    // Clear active company and redirect to select
    // (Note: setActiveCompany with null would need type adjustment or just a reset function)
    useCompanyStore.setState({ activeCompany: null });
    router.push("/company/select");
  };

  return (
    <div className="p-8">
      <div className="flex justify-between items-start mb-8">
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="text-gray-600">Company: <span className="font-semibold text-blue-600">{activeCompany?.name}</span></p>
        </div>
        <div className="space-x-2">
          <Button variant="outline" onClick={handleSwitchCompany}>Switch Company</Button>
          <Button variant="destructive" onClick={() => {
            logout();
            useCompanyStore.setState({ activeCompany: null, activeFY: null });
          }}>Logout</Button>
        </div>
      </div>

      <Card className="p-6">
        <h2 className="text-xl font-semibold mb-4">Welcome, {user?.full_name}!</h2>
        <p>You are now managing <strong>{activeCompany?.legal_name}</strong>.</p>
      </Card>
    </div>
  );
}
