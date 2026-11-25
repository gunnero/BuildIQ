import { useMutation } from "@tanstack/react-query";
import { useEffect, useState, type FormEvent, type ReactNode } from "react";
import { Link } from "react-router";

import { ApiError } from "../api/client";
import { activateDemo, submitDemoRequest } from "../api/demoRequests";

function DemoCard({ title, children }: { title: string; children: ReactNode }) {
  return (
    <main className="grid min-h-screen place-items-center bg-paper p-4 text-ink">
      <section className="ui-card w-full max-w-md space-y-5 p-6">
        <p className="text-sm font-semibold text-brand">BuildIQ</p>
        <h1 className="text-2xl font-bold">{title}</h1>
        {children}
        <Link className="text-sm font-semibold text-brand underline" to="/login">Назад кон најава</Link>
      </section>
    </main>
  );
}

const errorText = (error: unknown) =>
  error instanceof ApiError ? error.message : "Обидете се повторно.";

export function DemoRequestPage() {
  const submit = useMutation({ mutationFn: submitDemoRequest });

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    submit.mutate({
      name: String(data.get("name")).trim(),
      email: String(data.get("email")).trim(),
      company_name: String(data.get("company")).trim(),
      message: String(data.get("message")).trim(),
    });
  }

  return (
    <DemoCard title="Побарајте демо">
      {submit.isSuccess ? (
        <p className="ui-message" role="status">
          Барањето е примено. Ако биде одобрено, ќе добиете инструкции за пристап по е-пошта.
        </p>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4">
          <p className="text-sm text-slate-600">
            Побарајте пристап до свој демо работен простор за тестирање на BuildIQ.
          </p>
          <label className="ui-field-label">
            Име и презиме
            <input className="ui-input mt-1" name="name" autoComplete="name" required maxLength={120} />
          </label>
          <label className="ui-field-label">
            Е-пошта
            <input className="ui-input mt-1" name="email" type="email" autoComplete="email" required maxLength={254} />
          </label>
          <label className="ui-field-label">
            Компанија
            <input className="ui-input mt-1" name="company" autoComplete="organization" required maxLength={120} />
          </label>
          <label className="ui-field-label">
            Што сакате да тестирате? (изборно)
            <textarea className="ui-input mt-1" name="message" rows={3} maxLength={1000} />
          </label>
          <p className="text-sm text-slate-600">Ќе ја користиме е-поштата за да ви одговориме на ова барање.</p>
          {submit.isError && <p className="ui-message" role="alert">{errorText(submit.error)}</p>}
          <button type="submit" className="ui-button-primary w-full" disabled={submit.isPending}>
            {submit.isPending ? "Се испраќа…" : "Испратете барање"}
          </button>
        </form>
      )}
    </DemoCard>
  );
}

export function DemoActivationPage() {
  const [token] = useState(() => window.location.hash.slice(1));
  const [passwordMismatch, setPasswordMismatch] = useState(false);
  const activate = useMutation({ mutationFn: activateDemo });

  useEffect(() => {
    if (window.location.hash) {
      window.history.replaceState(window.history.state, "", window.location.pathname);
    }
  }, []);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const password = String(data.get("password"));
    if (password !== data.get("confirmation")) {
      setPasswordMismatch(true);
      return;
    }
    setPasswordMismatch(false);
    activate.mutate({ token, password });
  }

  return (
    <DemoCard title="Активирајте го демото">
      {activate.isSuccess ? (
        <p className="ui-message" role="status">
          Демото е активно 14 дена. Најавете се со {activate.data.email} и лозинката што ја поставивте.
        </p>
      ) : !token ? (
        <p role="alert">Отворете ја врската за активација од е-поштата за одобрување.</p>
      ) : (
        <form className="space-y-4" onSubmit={handleSubmit}>
          <label className="ui-field-label">
            Нова лозинка (најмалку 12 знаци)
            <input className="ui-input mt-1" name="password" type="password" autoComplete="new-password" minLength={12} maxLength={128} required />
          </label>
          <label className="ui-field-label">
            Потврдете ја лозинката
            <input className="ui-input mt-1" name="confirmation" type="password" autoComplete="new-password" minLength={12} maxLength={128} required />
          </label>
          {passwordMismatch && <p role="alert">Лозинките не се совпаѓаат.</p>}
          {activate.isError && <p className="ui-message" role="alert">{errorText(activate.error)}</p>}
          <button className="ui-button-primary w-full" type="submit" disabled={activate.isPending}>
            {activate.isPending ? "Се активира…" : "Активирајте демо пристап"}
          </button>
        </form>
      )}
    </DemoCard>
  );
}
