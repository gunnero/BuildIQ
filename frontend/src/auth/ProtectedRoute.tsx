import { Navigate, Outlet, useLocation } from "react-router";

import { useAuth } from "./useAuth";

export function ProtectedRoute() {
  const { isAuthenticated, isLoadingSession } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  if (isLoadingSession) {
    return (
      <main className="grid min-h-screen place-items-center bg-paper px-4 text-ink">
        <p className="rounded-md border border-line bg-white px-4 py-3 text-sm font-semibold shadow-sm">
          Се вчитува сесијата...
        </p>
      </main>
    );
  }

  return <Outlet />;
}
