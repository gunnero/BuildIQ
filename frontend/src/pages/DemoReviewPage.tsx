import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link, useParams } from "react-router";

import { ApiError } from "../api/client";
import { approveDemoRequest, getDemoRequest, listDemoRequests } from "../api/demoRequests";
import { useAuth } from "../auth/useAuth";

const base = "/admin/demo-requests";
const pageSize = 25;

function DemoRequestReview({ id }: { id: string }) {
  const cache = useQueryClient();
  const item = useQuery({ queryKey: ["demo-request", id], queryFn: () => getDemoRequest(id) });
  const approve = useMutation({
    mutationFn: () => approveDemoRequest(id),
    onSuccess: (data) => {
      cache.setQueryData(["demo-request", id], data);
      void cache.invalidateQueries({ queryKey: ["demo-requests"] });
    },
  });

  if (item.isError) return <p role="alert">Барањето не може да се вчита.</p>;
  if (!item.data) return <p role="status">Се вчитува…</p>;

  const request = item.data;
  const delivery = request.activated_at ? "Активирано" : request.invitation_sent_at ? "Испратена е е-пошта" : "Се чека испраќање";
  return (
    <section className="ui-card max-w-2xl space-y-4 p-5">
      <Link className="font-semibold text-brand underline" to={base}>Сите демо барања</Link>
      <h1 className="text-xl font-bold">{request.name}</h1>
      <p className="break-words text-sm text-slate-600">{request.company_name} · {request.email}</p>
      {request.message && <p className="whitespace-pre-wrap break-words">{request.message}</p>}
      {request.approved_at ? (
        <p className="ui-message" role="status">Одобрено · {delivery}</p>
      ) : (
        <button type="button" className="ui-button-primary" onClick={() => approve.mutate()} disabled={approve.isPending}>
          {approve.isPending ? "Се одобрува…" : "Одобри и испрати пристап"}
        </button>
      )}
      {approve.isError && (
        <p className="ui-message" role="alert">
          {approve.error instanceof ApiError ? approve.error.message : "Одобрувањето не успеа."}
        </p>
      )}
    </section>
  );
}

function DemoRequestQueue() {
  const [state, setState] = useState<"pending" | "approved">("pending");
  const [page, setPage] = useState(0);
  const list = useQuery({
    queryKey: ["demo-requests", state, page],
    queryFn: () => listDemoRequests(state, page * pageSize, pageSize + 1),
  });

  return (
    <section className="space-y-4">
      <h1 className="text-2xl font-bold">Демо барања</h1>
      <div className="flex flex-wrap gap-2">
        {(["pending", "approved"] as const).map((choice) => (
          <button key={choice} type="button" aria-pressed={choice === state}
            className={choice === state ? "ui-button-primary" : "ui-button-secondary"}
            onClick={() => { setState(choice); setPage(0); }}>
            {choice === "pending" ? "За преглед" : "Одобрени"}
          </button>
        ))}
      </div>
      {list.isPending && <p role="status">Се вчитува…</p>}
      {list.isError && <p role="alert">Барањата не може да се вчитаат.</p>}
      {list.data?.length === 0 && <p>Нема барања.</p>}
      <ul className="grid gap-2">
        {list.data?.slice(0, pageSize).map((request) => (
          <li key={request.id}>
            <Link className="ui-card block break-words p-4 hover:bg-slate-50" to={base + "/" + request.id}>
              <span className="block font-semibold text-brand">{request.name}</span>
              <span className="text-sm text-slate-600">{request.company_name} · {request.email}</span>
            </Link>
          </li>
        ))}
      </ul>
      <div className="flex gap-2">
        {page > 0 && <button type="button" className="ui-button-secondary" onClick={() => setPage(page - 1)}>Претходна</button>}
        {(list.data?.length ?? 0) > pageSize && (
          <button type="button" className="ui-button-secondary" onClick={() => setPage(page + 1)}>Следна</button>
        )}
      </div>
    </section>
  );
}

export function DemoReviewPage() {
  const { currentUser } = useAuth();
  const { requestId } = useParams();
  if (!currentUser?.can_review_demo_requests) return <p role="alert">Немате пристап до демо барањата.</p>;
  return requestId ? <DemoRequestReview key={requestId} id={requestId} /> : <DemoRequestQueue />;
}
