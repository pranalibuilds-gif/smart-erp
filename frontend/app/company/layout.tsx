import { ProtectedRoute } from "@/features/auth/guards/ProtectedRoute";

export default function CompanySetupLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        {children}
      </div>
    </ProtectedRoute>
  );
}
