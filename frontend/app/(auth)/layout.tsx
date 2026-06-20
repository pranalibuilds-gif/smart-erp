import { GuestOnlyRoute } from "@/features/auth/guards/GuestOnlyRoute";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <GuestOnlyRoute>{children}</GuestOnlyRoute>;
}
