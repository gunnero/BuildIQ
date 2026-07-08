import {
  Boxes,
  Calculator,
  ClipboardList,
  CreditCard,
  LayoutDashboard,
  LogOut,
  ReceiptText,
  Settings,
  Users,
  WalletCards,
  Warehouse,
} from "lucide-react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";

import { useAuth } from "../auth/useAuth";
import { formatSubscriptionStatus } from "../utils/statusLabels";

const navigationItems = [
  { to: "/dashboard", label: "Контролна табла", icon: LayoutDashboard },
  { to: "/customers", label: "Клиенти", icon: Users },
  { to: "/projects", label: "Проекти", icon: ClipboardList },
  { to: "/materials", label: "Материјали", icon: Boxes },
  { to: "/suppliers", label: "Добавувачи", icon: Warehouse },
  { to: "/calculations", label: "Пресметки", icon: Calculator },
  { to: "/estimates", label: "Понуди", icon: ReceiptText },
  { to: "/payments", label: "Уплати", icon: CreditCard },
  { to: "/expenses", label: "Трошоци", icon: WalletCards },
  { to: "/settings", label: "Поставки", icon: Settings },
];

export function AppShell() {
  const { company, currentUser, logout, subscription } = useAuth();
  const navigate = useNavigate();
  const companyName = company?.name ?? "BuildIQ";
  const subscriptionLabel = formatSubscriptionStatus(subscription?.status);

  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  return (
    <div className="min-h-screen bg-paper text-ink">
      <div className="grid min-h-screen lg:grid-cols-[280px_1fr]">
        <aside className="border-b border-line bg-white lg:border-b-0 lg:border-r">
          <div className="flex min-h-16 items-center justify-between gap-4 border-b border-line px-5">
            <div>
              <p className="text-lg font-bold tracking-normal">{companyName}</p>
              <p className="text-xs text-slate-500">BuildIQ</p>
            </div>
          </div>
          <nav aria-label="Главна навигација" className="grid gap-1 p-3">
            {navigationItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) =>
                    [
                      "flex h-11 items-center gap-3 rounded-md px-3 text-sm font-medium transition",
                      isActive
                        ? "bg-brand text-white shadow-sm"
                        : "text-slate-700 hover:bg-slate-100 hover:text-ink",
                    ].join(" ")
                  }
                >
                  <Icon aria-hidden="true" className="h-4 w-4 shrink-0" />
                  <span>{item.label}</span>
                </NavLink>
              );
            })}
          </nav>
        </aside>

        <div className="flex min-w-0 flex-col">
          <header className="flex min-h-16 items-center justify-between gap-4 border-b border-line bg-white px-5">
            <div>
              <p className="text-sm font-semibold text-slate-700">{currentUser?.name ?? "Корисник"}</p>
              <p className="text-xs text-slate-500">
                {companyName} - Претплата: {subscriptionLabel}
              </p>
            </div>
            <button
              type="button"
              onClick={handleLogout}
              className="inline-flex h-10 items-center gap-2 rounded-md border border-line bg-white px-3 text-sm font-semibold text-slate-700 transition hover:border-brand hover:text-brand focus:outline-none focus:ring-2 focus:ring-brand focus:ring-offset-2"
            >
              <LogOut aria-hidden="true" className="h-4 w-4" />
              Одјава
            </button>
          </header>
          <main className="min-w-0 flex-1 p-5 lg:p-8">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  );
}
