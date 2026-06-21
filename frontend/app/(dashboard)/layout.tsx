import { Sidebar } from "@/components/ui/sidebar";
import { ProtectedRoute } from "@/features/auth/guards/ProtectedRoute";

export default function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ProtectedRoute>
      <div className="flex min-h-screen">
        <Sidebar />
        <main className="flex-1 bg-gray-50">
          {children}
        </main>
      </div>
    </ProtectedRoute>
  );
}
