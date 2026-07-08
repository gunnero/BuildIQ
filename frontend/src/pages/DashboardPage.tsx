import { EmptyState } from "../components/EmptyState";
import { useAuth } from "../auth/useAuth";
import { formatCompanyStatus, formatSubscriptionStatus } from "../utils/statusLabels";

export function DashboardPage() {
  const { company, currentUser, subscription } = useAuth();
  const companyStatus = formatCompanyStatus(company?.status);
  const subscriptionStatus = formatSubscriptionStatus(subscription?.status);

  return (
    <section className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-normal text-ink">Контролна табла</h1>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
          Добредојдовте во BuildIQ. Подолу се прикажани само податоци добиени од backend API.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <section className="rounded-md border border-line bg-white p-4 shadow-sm">
          <p className="text-xs font-semibold uppercase text-slate-500">Корисник</p>
          <h2 className="mt-2 text-lg font-bold tracking-normal text-ink">{currentUser?.name ?? "Непознат корисник"}</h2>
          <p className="mt-1 break-all text-sm text-slate-600">{currentUser?.email ?? "Нема е-пошта"}</p>
        </section>

        <section className="rounded-md border border-line bg-white p-4 shadow-sm">
          <p className="text-xs font-semibold uppercase text-slate-500">Компанија</p>
          <h2 className="mt-2 text-lg font-bold tracking-normal text-ink">{company?.name ?? "Нема компанија"}</h2>
          <p className="mt-1 text-sm text-slate-600">Статус: {companyStatus}</p>
        </section>

        <section className="rounded-md border border-line bg-white p-4 shadow-sm">
          <p className="text-xs font-semibold uppercase text-slate-500">Претплата</p>
          <h2 className="mt-2 text-lg font-bold tracking-normal text-ink">{subscription?.plan.name ?? "Нема план"}</h2>
          <p className="mt-1 text-sm text-slate-600">Статус: {subscriptionStatus}</p>
        </section>
      </div>

      <EmptyState
        title="Започнете со додавање клиент."
        description="Потоа креирајте проект и простории. Потоа направете пресметка и понуда."
      />
    </section>
  );
}
