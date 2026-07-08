import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { AuthProvider } from "./auth/AuthContext";
import { ProtectedRoute } from "./auth/ProtectedRoute";
import { AppShell } from "./components/AppShell";
import { CalculationsPage } from "./pages/CalculationsPage";
import { CustomersPage } from "./pages/CustomersPage";
import { DashboardPage } from "./pages/DashboardPage";
import { LoginPage } from "./pages/LoginPage";
import { ProjectsPage } from "./pages/ProjectsPage";
import { SectionPage } from "./pages/SectionPage";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
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
                <Route
                  path="/estimates"
                  element={<SectionPage title="Понуди" description="Овде ќе се прикажуваат понудите и нивните ревизии." />}
                />
                <Route
                  path="/payments"
                  element={<SectionPage title="Уплати" description="Овде ќе се прикажуваат уплатите добиени од серверот." />}
                />
                <Route
                  path="/expenses"
                  element={<SectionPage title="Трошоци" description="Овде ќе се прикажуваат трошоците добиени од серверот." />}
                />
                <Route
                  path="/settings"
                  element={<SectionPage title="Поставки" description="Овде ќе се прикажуваат поставките за компанијата и профилот." />}
                />
              </Route>
            </Route>
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
}
