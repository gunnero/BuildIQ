import { QueryClientProvider } from "@tanstack/react-query";
import { lazy, Suspense } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router";

import { AuthProvider } from "./auth/AuthContext";
import { ProtectedRoute } from "./auth/ProtectedRoute";
import { AppShell } from "./components/AppShell";
import { LoginPage } from "./pages/LoginPage";
import { SectionPage } from "./pages/SectionPage";
import { queryClient } from "./queryClient";

const CalculationsPage = lazy(() => import("./pages/CalculationsPage").then(({ CalculationsPage }) => ({ default: CalculationsPage })));
const CustomersPage = lazy(() => import("./pages/CustomersPage").then(({ CustomersPage }) => ({ default: CustomersPage })));
const DashboardPage = lazy(() => import("./pages/DashboardPage").then(({ DashboardPage }) => ({ default: DashboardPage })));
const EstimatesPage = lazy(() => import("./pages/EstimatesPage").then(({ EstimatesPage }) => ({ default: EstimatesPage })));
const ExpensesPage = lazy(() => import("./pages/ExpensesPage").then(({ ExpensesPage }) => ({ default: ExpensesPage })));
const PaymentsPage = lazy(() => import("./pages/PaymentsPage").then(({ PaymentsPage }) => ({ default: PaymentsPage })));
const ProjectsPage = lazy(() => import("./pages/ProjectsPage").then(({ ProjectsPage }) => ({ default: ProjectsPage })));

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <Suspense fallback={<main className="p-6" aria-live="polite">Се вчитува…</main>}>
            <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route element={<ProtectedRoute />}>
              <Route element={<AppShell />}>
                <Route index element={<Navigate to="/dashboard" replace />} />
                <Route path="/dashboard" element={<DashboardPage />} />
                <Route path="/customers" element={<CustomersPage />} />
                <Route path="/projects" element={<ProjectsPage />} />
                <Route
                  path="/materials"
                  element={<SectionPage title="Материјали" description="Овде ќе се прикажува каталогот на материјали од серверот." />}
                />
                <Route
                  path="/suppliers"
                  element={<SectionPage title="Добавувачи" description="Овде ќе се прикажуваат добавувачите и продавниците." />}
                />
                <Route path="/calculations" element={<CalculationsPage />} />
                <Route path="/estimates" element={<EstimatesPage />} />
                <Route path="/payments" element={<PaymentsPage />} />
                <Route path="/expenses" element={<ExpensesPage />} />
                <Route
                  path="/settings"
                  element={<SectionPage title="Поставки" description="Овде ќе се прикажуваат поставките за компанијата и профилот." />}
                />
              </Route>
            </Route>
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </Suspense>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
}
