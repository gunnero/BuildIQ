import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Archive, Plus, RotateCcw } from "lucide-react";
import { useEffect, useMemo, useState, type ChangeEvent, type FormEvent, type ReactNode } from "react";

import { listCustomers } from "../api/customers";
import { listEstimates } from "../api/estimates";
import { archivePayment, createPayment, getPayment, listPayments, reversePayment } from "../api/financial";
import { listProjects } from "../api/projects";
import type {
  CustomerResponse,
  EstimateResponse,
  PaymentCreateRequest,
  PaymentResponse,
  ProjectResponse,
} from "../api/types";
import { formatDate } from "../lib/format";

type MessageTone = "neutral" | "error" | "success";

type PageMessage = {
  text: string;
  tone: MessageTone;
};

type PaymentFormState = {
  customer_id: string;
  project_id: string;
  estimate_id: string;
  amount: string;
  payment_method: string;
  payment_date: string;
  status: string;
  note: string;
};

const emptyPaymentForm: PaymentFormState = {
  customer_id: "",
  project_id: "",
  estimate_id: "",
  amount: "",
  payment_method: "cash",
  payment_date: "",
  status: "received",
  note: "",
};

const paymentMethods = [
  { value: "cash", label: "Кеш" },
  { value: "bank_transfer", label: "Банкарски трансфер" },
  { value: "card", label: "Картичка" },
  { value: "other", label: "Друго" },
];

const paymentStatuses = [
  { value: "received", label: "Примена" },
  { value: "pending", label: "Во чекање" },
  { value: "reversed", label: "Сторнирана" },
  { value: "archived", label: "Архивирана" },
];

const emptyCustomers: CustomerResponse[] = [];
const emptyProjects: ProjectResponse[] = [];
const emptyEstimates: EstimateResponse[] = [];
const emptyPayments: PaymentResponse[] = [];

function toNullable(value: string): string | null {
  const trimmedValue = value.trim();
  return trimmedValue === "" ? null : trimmedValue;
}

function formatNumber(value: number): string {
  return value.toFixed(4).replace(/\.?0+$/, "");
}

function formatMoney(value: number | null | undefined, currency = "MKD"): string {
  if (value === null || value === undefined) {
    return "Не е вратено";
  }

  return `${formatNumber(value)} ${currency}`;
}

function formatMethod(method: string): string {
  return paymentMethods.find((item) => item.value === method)?.label ?? method;
}

function formatPaymentStatus(status: string): string {
  return paymentStatuses.find((item) => item.value === status)?.label ?? status;
}

function localizedErrorMessage(error: unknown, fallback: string): string {
  if (error instanceof Error && /[А-џ]/.test(error.message)) {
    return error.message;
  }

  return fallback;
}

function selectLabel<T extends { id: string }>(
  items: T[],
  id: string | null,
  getLabel: (item: T) => string,
  fallback: string,
): string {
  if (!id) {
    return fallback;
  }

  const selectedItem = items.find((item) => item.id === id);
  return selectedItem ? getLabel(selectedItem) : id;
}

function paymentPayloadFromForm(form: PaymentFormState): PaymentCreateRequest {
  return {
    customer_id: form.customer_id,
    project_id: form.project_id,
    estimate_id: toNullable(form.estimate_id),
    amount: Number(form.amount),
    payment_method: form.payment_method,
    payment_date: form.payment_date,
    status: form.status,
    note: toNullable(form.note),
    allocations: [],
  };
}

function Panel({ children, title }: { children: ReactNode; title: string }) {
  return (
    <section aria-label={title} className="ui-card">
      <h2 className="ui-card-title">{title}</h2>
      <div className="mt-4">{children}</div>
    </section>
  );
}

function FormField({
  label,
  name,
  onChange,
  required = false,
  type = "text",
  value,
}: {
  label: string;
  name: string;
  onChange: (event: ChangeEvent<HTMLInputElement>) => void;
  required?: boolean;
  type?: string;
  value: string;
}) {
  return (
    <label htmlFor={name} className="ui-field-label">
      {label}
      <input
        id={name}
        name={name}
        type={type}
        value={value}
        required={required}
        onChange={onChange}
        className="ui-input"
      />
    </label>
  );
}

function TextAreaField({
  label,
  name,
  onChange,
  value,
}: {
  label: string;
  name: string;
  onChange: (event: ChangeEvent<HTMLTextAreaElement>) => void;
  value: string;
}) {
  return (
    <label htmlFor={name} className="ui-field-label">
      {label}
      <textarea
        id={name}
        name={name}
        value={value}
        onChange={onChange}
        rows={3}
        className="ui-textarea"
      />
    </label>
  );
}

function SelectField({
  children,
  label,
  name,
  onChange,
  required = false,
  value,
}: {
  children: ReactNode;
  label: string;
  name: string;
  onChange: (event: ChangeEvent<HTMLSelectElement>) => void;
  required?: boolean;
  value: string;
}) {
  return (
    <label htmlFor={name} className="ui-field-label">
      {label}
      <select
        id={name}
        name={name}
        value={value}
        required={required}
        onChange={onChange}
        className="ui-select"
      >
        {children}
      </select>
    </label>
  );
}

function Message({ children, tone = "neutral" }: { children: ReactNode; tone?: MessageTone }) {
  const toneClass =
    tone === "error"
      ? "border-red-200 bg-red-50 text-red-800"
      : tone === "success"
        ? "border-emerald-200 bg-emerald-50 text-emerald-800"
        : "border-line bg-slate-50 text-slate-700";

  return <p className={`ui-message ${toneClass}`}>{children}</p>;
}

function EmptyState({ children }: { children: ReactNode }) {
  return <p className="ui-empty-inline">{children}</p>;
}

function PrimaryButton({ children, disabled = false }: { children: ReactNode; disabled?: boolean }) {
  return (
    <button
      type="submit"
      disabled={disabled}
      className="ui-button-primary"
    >
      <Plus aria-hidden="true" className="h-4 w-4" />
      {children}
    </button>
  );
}

function ActionButton({
  children,
  icon,
  onClick,
  tone = "neutral",
}: {
  children: ReactNode;
  icon: ReactNode;
  onClick: () => void;
  tone?: "neutral" | "danger";
}) {
  const toneClass =
    tone === "danger"
      ? "border-red-200 text-red-800 hover:border-red-400 hover:bg-red-50"
      : "border-line text-slate-700 hover:border-brand hover:text-brand";

  return (
    <button
      type="button"
      onClick={onClick}
      className={`ui-button-secondary ${toneClass}`}
    >
      {icon}
      {children}
    </button>
  );
}

function StatusBadge({ status }: { status: string }) {
  const statusClass =
    status === "received"
      ? "border-emerald-200 bg-emerald-50 text-emerald-800"
      : status === "pending"
        ? "border-sky-200 bg-sky-50 text-sky-800"
        : "border-red-200 bg-red-50 text-red-800";

  return (
    <span className={`ui-status-badge ${statusClass}`}>
      {formatPaymentStatus(status)}
    </span>
  );
}

function DetailRow({ label, value }: { label: string; value: string | number | null | undefined }) {
  const displayValue = value === null || value === undefined || value === "" ? "Не е внесено" : value;

  return (
    <div>
      <dt className="text-xs font-semibold uppercase text-slate-500">{label}</dt>
      <dd className="mt-1 text-sm text-slate-800">{displayValue}</dd>
    </div>
  );
}

export function PaymentsPage() {
  const queryClient = useQueryClient();
  const [selectedPaymentId, setSelectedPaymentId] = useState<string | null>(null);
  const [paymentForm, setPaymentForm] = useState<PaymentFormState>(emptyPaymentForm);
  const [reverseReason, setReverseReason] = useState("");
  const [pageMessage, setPageMessage] = useState<PageMessage | null>(null);

  const customersQuery = useQuery({ queryKey: ["customers"], queryFn: listCustomers });
  const projectsQuery = useQuery({ queryKey: ["projects"], queryFn: listProjects });
  const estimatesQuery = useQuery({ queryKey: ["estimates"], queryFn: listEstimates });
  const paymentsQuery = useQuery({ queryKey: ["payments"], queryFn: listPayments });

  const customers = customersQuery.data ?? emptyCustomers;
  const projects = projectsQuery.data ?? emptyProjects;
  const estimates = estimatesQuery.data ?? emptyEstimates;
  const payments = paymentsQuery.data ?? emptyPayments;

  const selectedPaymentListItem = payments.find((paymentItem) => paymentItem.id === selectedPaymentId) ?? null;
  const selectedPaymentQuery = useQuery({
    queryKey: ["payments", selectedPaymentId],
    queryFn: () => getPayment(selectedPaymentId ?? ""),
    enabled: Boolean(selectedPaymentId),
  });
  const selectedPayment = selectedPaymentQuery.data ?? selectedPaymentListItem ?? payments[0] ?? null;

  const customerLabel = (customerId: string | null) =>
    selectLabel<CustomerResponse>(customers, customerId, (customer) => customer.name, "Без клиент");
  const projectLabel = (projectId: string | null) =>
    selectLabel<ProjectResponse>(projects, projectId, (project) => project.name, "Без проект");
  const estimateLabel = (estimateId: string | null) =>
    selectLabel<EstimateResponse>(estimates, estimateId, (estimate) => estimate.title, "Без понуда");

  const estimatesForSelectedProject = useMemo(() => {
    return estimates.filter((estimate) => !paymentForm.project_id || estimate.project_id === paymentForm.project_id);
  }, [estimates, paymentForm.project_id]);

  useEffect(() => {
    if (!selectedPaymentId && payments.length > 0) {
      setSelectedPaymentId(payments[0].id);
    }
  }, [payments, selectedPaymentId]);

  useEffect(() => {
    if (!paymentForm.customer_id && customers.length > 0) {
      setPaymentForm((current) => ({ ...current, customer_id: customers[0].id }));
    }
  }, [customers, paymentForm.customer_id]);

  useEffect(() => {
    if (!paymentForm.project_id && projects.length > 0) {
      const firstProject = projects[0];
      setPaymentForm((current) => ({
        ...current,
        customer_id: current.customer_id || firstProject.customer_id,
        project_id: firstProject.id,
      }));
    }
  }, [paymentForm.project_id, projects]);

  const createPaymentMutation = useMutation({
    mutationFn: createPayment,
    onSuccess: (paymentItem) => {
      setPageMessage({ text: "Уплатата е додадена.", tone: "success" });
      setSelectedPaymentId(paymentItem.id);
      setPaymentForm((current) => ({
        ...emptyPaymentForm,
        customer_id: current.customer_id,
        project_id: current.project_id,
      }));
      void queryClient.invalidateQueries({ queryKey: ["payments"] });
    },
    onError: (error) => {
      setPageMessage({ text: localizedErrorMessage(error, "Уплатата не беше додадена. Проверете ги податоците."), tone: "error" });
    },
  });

  const reversePaymentMutation = useMutation({
    mutationFn: ({ paymentId, reason }: { paymentId: string; reason: string }) => reversePayment(paymentId, { reason }),
    onSuccess: (paymentItem) => {
      setPageMessage({ text: "Уплатата е сторнирана.", tone: "success" });
      setReverseReason("");
      void queryClient.invalidateQueries({ queryKey: ["payments"] });
      void queryClient.invalidateQueries({ queryKey: ["payments", paymentItem.id] });
    },
    onError: (error) => {
      setPageMessage({ text: localizedErrorMessage(error, "Уплатата не беше сторнирана."), tone: "error" });
    },
  });

  const archivePaymentMutation = useMutation({
    mutationFn: archivePayment,
    onSuccess: (paymentItem) => {
      setPageMessage({ text: "Уплатата е архивирана.", tone: "success" });
      void queryClient.invalidateQueries({ queryKey: ["payments"] });
      void queryClient.invalidateQueries({ queryKey: ["payments", paymentItem.id] });
    },
    onError: (error) => {
      setPageMessage({ text: localizedErrorMessage(error, "Уплатата не беше архивирана."), tone: "error" });
    },
  });

  function handlePaymentField(field: keyof PaymentFormState) {
    return (event: ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
      const value = event.target.value;
      setPaymentForm((current) => {
        if (field === "project_id") {
          const selectedProject = projects.find((project) => project.id === value);
          return {
            ...current,
            project_id: value,
            customer_id: selectedProject?.customer_id ?? current.customer_id,
            estimate_id: current.estimate_id && estimates.some((estimate) => estimate.id === current.estimate_id && estimate.project_id === value)
              ? current.estimate_id
              : "",
          };
        }

        return { ...current, [field]: value };
      });
    };
  }

  function handleCreatePayment(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const payload = paymentPayloadFromForm(paymentForm);

    if (!payload.customer_id) {
      setPageMessage({ text: "Изберете клиент за уплатата.", tone: "error" });
      return;
    }
    if (!payload.project_id) {
      setPageMessage({ text: "Изберете проект за уплатата.", tone: "error" });
      return;
    }
    if (!payload.payment_date) {
      setPageMessage({ text: "Внесете датум на уплата.", tone: "error" });
      return;
    }
    if (Number.isNaN(payload.amount) || payload.amount <= 0) {
      setPageMessage({ text: "Износот мора да биде поголем од нула.", tone: "error" });
      return;
    }

    createPaymentMutation.mutate(payload);
  }

  function handleReversePayment() {
    if (!selectedPayment) {
      return;
    }
    const reason = reverseReason.trim();
    if (!reason) {
      setPageMessage({ text: "Внесете причина за сторно.", tone: "error" });
      return;
    }
    if (!window.confirm("Дали сте сигурни дека сакате да ја сторнирате уплатата?")) {
      return;
    }

    reversePaymentMutation.mutate({ paymentId: selectedPayment.id, reason });
  }

  function handleArchivePayment() {
    if (!selectedPayment) {
      return;
    }
    if (!window.confirm("Дали сте сигурни дека сакате да ја архивирате уплатата?")) {
      return;
    }

    archivePaymentMutation.mutate(selectedPayment.id);
  }

  return (
    <section className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-normal text-ink">Уплати</h1>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
          Следете примени, очекувани и сторнирани уплати преку податоците од серверот.
        </p>
      </div>

      {pageMessage ? <Message tone={pageMessage.tone}>{pageMessage.text}</Message> : null}

      <div className="grid gap-6 xl:grid-cols-[420px_minmax(0,1fr)]">
        <aside className="space-y-4">
          <Panel title="Нова уплата">
            <form onSubmit={handleCreatePayment} className="space-y-4">
              <SelectField
                label="Клиент за уплата"
                name="payment-customer-id"
                value={paymentForm.customer_id}
                required
                onChange={handlePaymentField("customer_id")}
              >
                <option value="">Изберете клиент</option>
                {customers.map((customer) => (
                  <option key={customer.id} value={customer.id}>
                    {customer.name}
                  </option>
                ))}
              </SelectField>
              <SelectField
                label="Проект за уплата"
                name="payment-project-id"
                value={paymentForm.project_id}
                required
                onChange={handlePaymentField("project_id")}
              >
                <option value="">Изберете проект</option>
                {projects.map((project) => (
                  <option key={project.id} value={project.id}>
                    {project.name}
                  </option>
                ))}
              </SelectField>
              <SelectField
                label="Понуда за уплата"
                name="payment-estimate-id"
                value={paymentForm.estimate_id}
                onChange={handlePaymentField("estimate_id")}
              >
                <option value="">Без понуда</option>
                {estimatesForSelectedProject.map((estimate) => (
                  <option key={estimate.id} value={estimate.id}>
                    {estimate.title}
                  </option>
                ))}
              </SelectField>
              <FormField
                label="Износ на уплата"
                name="payment-amount"
                type="number"
                value={paymentForm.amount}
                required
                onChange={handlePaymentField("amount")}
              />
              <SelectField
                label="Начин на плаќање"
                name="payment-method"
                value={paymentForm.payment_method}
                onChange={handlePaymentField("payment_method")}
              >
                {paymentMethods.map((method) => (
                  <option key={method.value} value={method.value}>
                    {method.label}
                  </option>
                ))}
              </SelectField>
              <FormField
                label="Датум на уплата"
                name="payment-date"
                type="date"
                value={paymentForm.payment_date}
                required
                onChange={handlePaymentField("payment_date")}
              />
              <SelectField
                label="Статус на уплата"
                name="payment-status"
                value={paymentForm.status}
                onChange={handlePaymentField("status")}
              >
                {paymentStatuses
                  .filter((status) => ["received", "pending"].includes(status.value))
                  .map((status) => (
                    <option key={status.value} value={status.value}>
                      {status.label}
                    </option>
                  ))}
              </SelectField>
              <TextAreaField
                label="Белешка за уплата"
                name="payment-note"
                value={paymentForm.note}
                onChange={handlePaymentField("note")}
              />
              <PrimaryButton disabled={createPaymentMutation.isPending}>Додај уплата</PrimaryButton>
            </form>
          </Panel>
        </aside>

        <div className="space-y-6">
          <Panel title="Листа на уплати">
            {paymentsQuery.isLoading ? <Message>Се вчитуваат уплатите.</Message> : null}
            {paymentsQuery.isError ? <Message tone="error">Уплатите не може да се вчитаат.</Message> : null}
            {!paymentsQuery.isLoading && payments.length === 0 ? <EmptyState>Нема евидентирани уплати.</EmptyState> : null}
            <div className="grid gap-3 lg:grid-cols-2">
              {payments.map((paymentItem) => (
                <button
                  key={paymentItem.id}
                  type="button"
                  onClick={() => setSelectedPaymentId(paymentItem.id)}
                  className={[
                    "rounded-md border px-3 py-3 text-left transition",
                    selectedPayment?.id === paymentItem.id ? "border-brand bg-brand/10" : "border-line bg-white hover:border-brand",
                  ].join(" ")}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-sm font-bold text-ink">{formatMoney(paymentItem.amount, paymentItem.currency)}</p>
                      <p className="mt-1 text-xs text-slate-500">
                        {customerLabel(paymentItem.customer_id)} - {projectLabel(paymentItem.project_id)}
                      </p>
                      <p className="mt-1 text-xs text-slate-500">{formatMethod(paymentItem.payment_method)}</p>
                    </div>
                    <StatusBadge status={paymentItem.status} />
                  </div>
                </button>
              ))}
            </div>
          </Panel>

          <Panel title="Детали за уплата">
            {selectedPayment ? (
              <div className="space-y-5">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <p className="text-xl font-bold tracking-normal text-ink">
                      {formatMoney(selectedPayment.amount, selectedPayment.currency)}
                    </p>
                    <p className="mt-1 text-sm text-slate-600">
                      {customerLabel(selectedPayment.customer_id)} - {projectLabel(selectedPayment.project_id)}
                    </p>
                  </div>
                  <StatusBadge status={selectedPayment.status} />
                </div>

                <dl className="grid gap-4 rounded-md border border-line bg-slate-50 p-3 sm:grid-cols-2 xl:grid-cols-4">
                  <DetailRow label="Понуда" value={estimateLabel(selectedPayment.estimate_id)} />
                  <DetailRow label="Начин" value={formatMethod(selectedPayment.payment_method)} />
                  <DetailRow label="Датум" value={formatDate(selectedPayment.payment_date)} />
                  <DetailRow label="Белешка" value={selectedPayment.note} />
                  <DetailRow label="Сторно причина" value={selectedPayment.reversal_reason} />
                  <DetailRow label="Сторнирано" value={selectedPayment.reversed_at ? formatDate(selectedPayment.reversed_at) : null} />
                  <DetailRow label="Архивирано" value={selectedPayment.archived_at ? formatDate(selectedPayment.archived_at) : null} />
                  <DetailRow label="Креирано" value={formatDate(selectedPayment.created_at)} />
                </dl>

                {selectedPayment.allocations.length > 0 ? (
                  <div>
                    <h3 className="text-sm font-bold text-ink">Алокации</h3>
                    <div className="mt-3 grid gap-2">
                      {selectedPayment.allocations.map((allocation) => (
                        <div key={allocation.id} className="rounded-md border border-line bg-white px-3 py-2 text-sm text-slate-700">
                          {projectLabel(allocation.project_id)} - {estimateLabel(allocation.estimate_id)} -{" "}
                          {formatMoney(allocation.amount, selectedPayment.currency)}
                        </div>
                      ))}
                    </div>
                  </div>
                ) : null}

                <label htmlFor="payment-reverse-reason" className="block text-sm font-semibold text-slate-700">
                  Причина за сторно уплата
                  <textarea
                    id="payment-reverse-reason"
                    value={reverseReason}
                    onChange={(event) => setReverseReason(event.target.value)}
                    rows={3}
                    className="ui-textarea"
                  />
                </label>

                <div className="flex flex-wrap gap-2">
                  <ActionButton
                    icon={<RotateCcw aria-hidden="true" className="h-4 w-4" />}
                    onClick={handleReversePayment}
                    tone="danger"
                  >
                    Сторнирај уплата
                  </ActionButton>
                  <ActionButton
                    icon={<Archive aria-hidden="true" className="h-4 w-4" />}
                    onClick={handleArchivePayment}
                    tone="danger"
                  >
                    Архивирај уплата
                  </ActionButton>
                </div>
              </div>
            ) : (
              <EmptyState>Изберете уплата за да ги видите деталите.</EmptyState>
            )}
          </Panel>
        </div>
      </div>
    </section>
  );
}
