import { EmptyState } from "../components/EmptyState";

export function DashboardPage() {
  return (
    <section className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-normal text-ink">Контролна табла</h1>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
          Овде ќе се прикажуваат прегледи добиени од серверот кога backend ќе обезбеди
          податоци за активни проекти, уплати, трошоци и понуди.
        </p>
      </div>
      <EmptyState
        title="Нема податоци за приказ."
        description="Фронтендот не пресметува суми, статуси или количини. Овој екран ќе прикаже само вредности добиени од серверот."
      />
    </section>
  );
}
