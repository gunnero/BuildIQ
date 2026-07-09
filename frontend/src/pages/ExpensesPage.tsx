import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Archive, Plus, RotateCcw, Save } from "lucide-react";
import { useEffect, useState, type ChangeEvent, type FormEvent, type ReactNode } from "react";

import {
  archiveExpense,
  archiveExpenseCategory,
  createExpense,
  createExpenseCategory,
  getExpense,
  listExpenseCategories,
  listExpenses,
  reverseExpense,
  updateExpenseCategory,
} from "../api/financial";
import { listMaterials } from "../api/materials";
import { listProjects } from "../api/projects";
import type {
  ExpenseCategoryCreateRequest,
  ExpenseCategoryResponse,
  ExpenseCategoryUpdateRequest,
  ExpenseCreateRequest,
  ExpenseResponse,
  MaterialResponse,
  ProjectResponse,
} from "../api/types";
import { formatDate } from "../lib/format";

type MessageTone = "neutral" | "error" | "success";

type PageMessage = {
  text: string;
  tone: MessageTone;
};

type CategoryFormState = {
  name: string;
  description: string;
};

type ExpenseFormState = {
  project_id: string;
  category_id: string;
  material_id: string;
  description: string;
  amount: string;
  expense_date: string;
  payment_method: string;
  status: string;
  note: string;
};

const emptyCategoryForm: CategoryFormState = {
  name: "",
  description: "",
};

const emptyExpenseForm: ExpenseFormState = {
  project_id: "",
  category_id: "",
  material_id: "",
  description: "",
  amount: "",
  expense_date: "",
  payment_method: "cash",
  status: "recorded",
  note: "",
};

const paymentMethods = [
  { value: "cash", label: "Кеш" },
  { value: "bank_transfer", label: "Банкарски трансфер" },
  { value: "card", label: "Картичка" },
  { value: "other", label: "Друго" },
];

const expenseStatuses = [
  { value: "recorded", label: "Евидентиран" },
  { value: "reimbursed", label: "Надоместен" },
  { value: "reversed", label: "Сторниран" },
  { value: "archived", label: "Архивиран" },
];

const emptyProjects: ProjectResponse[] = [];
const emptyMaterials: MaterialResponse[] = [];
const emptyCategories: ExpenseCategoryResponse[] = [];
const emptyExpenses: ExpenseResponse[] = [];

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

function formatExpenseStatus(status: string): string {
  return expenseStatuses.find((item) => item.value === status)?.label ?? status;
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

function categoryPayloadFromForm(form: CategoryFormState): ExpenseCategoryCreateRequest {
  return {
    name: form.name.trim(),
    description: toNullable(form.description),
  };
}

function categoryFormFromEntity(category: ExpenseCategoryResponse): CategoryFormState {
  return {
    name: category.name,
    description: category.description ?? "",
  };
}

function expensePayloadFromForm(form: ExpenseFormState): ExpenseCreateRequest {
  return {
    project_id: toNullable(form.project_id),
    category_id: toNullable(form.category_id),
    supplier_id: null,
    material_id: toNullable(form.material_id),
    description: form.description.trim(),
    amount: Number(form.amount),
    expense_date: form.expense_date,
    payment_method: form.payment_method,
    status: form.status,
    note: toNullable(form.note),
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
  value,
}: {
  children: ReactNode;
  label: string;
  name: string;
  onChange: (event: ChangeEvent<HTMLSelectElement>) => void;
  value: string;
}) {
  return (
    <label htmlFor={name} className="ui-field-label">
      {label}
      <select
        id={name}
        name={name}
        value={value}
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
    status === "recorded" || status === "reimbursed"
      ? "border-emerald-200 bg-emerald-50 text-emerald-800"
      : "border-red-200 bg-red-50 text-red-800";

  return (
    <span className={`ui-status-badge ${statusClass}`}>
      {formatExpenseStatus(status)}
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

export function ExpensesPage() {
  const queryClient = useQueryClient();
  const [selectedCategoryId, setSelectedCategoryId] = useState<string | null>(null);
  const [selectedExpenseId, setSelectedExpenseId] = useState<string | null>(null);
  const [categoryForm, setCategoryForm] = useState<CategoryFormState>(emptyCategoryForm);
  const [categoryEditForm, setCategoryEditForm] = useState<CategoryFormState>(emptyCategoryForm);
  const [expenseForm, setExpenseForm] = useState<ExpenseFormState>(emptyExpenseForm);
  const [reverseReason, setReverseReason] = useState("");
  const [pageMessage, setPageMessage] = useState<PageMessage | null>(null);

  const projectsQuery = useQuery({ queryKey: ["projects"], queryFn: listProjects });
  const materialsQuery = useQuery({ queryKey: ["materials"], queryFn: listMaterials });
  const categoriesQuery = useQuery({ queryKey: ["expense-categories"], queryFn: listExpenseCategories });
  const expensesQuery = useQuery({ queryKey: ["expenses"], queryFn: listExpenses });

  const projects = projectsQuery.data ?? emptyProjects;
  const materials = materialsQuery.data ?? emptyMaterials;
  const categories = categoriesQuery.data ?? emptyCategories;
  const expenses = expensesQuery.data ?? emptyExpenses;

  const selectedCategory = categories.find((category) => category.id === selectedCategoryId) ?? categories[0] ?? null;
  const selectedExpenseListItem = expenses.find((expenseItem) => expenseItem.id === selectedExpenseId) ?? null;
  const selectedExpenseQuery = useQuery({
    queryKey: ["expenses", selectedExpenseId],
    queryFn: () => getExpense(selectedExpenseId ?? ""),
    enabled: Boolean(selectedExpenseId),
  });
  const selectedExpense = selectedExpenseQuery.data ?? selectedExpenseListItem ?? expenses[0] ?? null;

  const projectLabel = (projectId: string | null) =>
    selectLabel<ProjectResponse>(projects, projectId, (project) => project.name, "Без проект");
  const categoryLabel = (categoryId: string | null) =>
    selectLabel<ExpenseCategoryResponse>(categories, categoryId, (category) => category.name, "Без категорија");
  const materialLabel = (materialId: string | null) =>
    selectLabel<MaterialResponse>(materials, materialId, (material) => material.name, "Без материјал");

  useEffect(() => {
    if (!selectedCategoryId && categories.length > 0) {
      setSelectedCategoryId(categories[0].id);
    }
  }, [categories, selectedCategoryId]);

  useEffect(() => {
    if (selectedCategory) {
      setCategoryEditForm(categoryFormFromEntity(selectedCategory));
    }
  }, [selectedCategory]);

  useEffect(() => {
    if (!selectedExpenseId && expenses.length > 0) {
      setSelectedExpenseId(expenses[0].id);
    }
  }, [expenses, selectedExpenseId]);

  const createCategoryMutation = useMutation({
    mutationFn: createExpenseCategory,
    onSuccess: (category) => {
      setPageMessage({ text: "Категоријата е додадена.", tone: "success" });
      setSelectedCategoryId(category.id);
      setCategoryForm(emptyCategoryForm);
      void queryClient.invalidateQueries({ queryKey: ["expense-categories"] });
    },
    onError: (error) => {
      setPageMessage({ text: localizedErrorMessage(error, "Категоријата не беше додадена."), tone: "error" });
    },
  });

  const updateCategoryMutation = useMutation({
    mutationFn: ({ categoryId, payload }: { categoryId: string; payload: ExpenseCategoryUpdateRequest }) =>
      updateExpenseCategory(categoryId, payload),
    onSuccess: () => {
      setPageMessage({ text: "Категоријата е зачувана.", tone: "success" });
      void queryClient.invalidateQueries({ queryKey: ["expense-categories"] });
    },
    onError: (error) => {
      setPageMessage({ text: localizedErrorMessage(error, "Категоријата не беше зачувана."), tone: "error" });
    },
  });

  const archiveCategoryMutation = useMutation({
    mutationFn: archiveExpenseCategory,
    onSuccess: () => {
      setPageMessage({ text: "Категоријата е архивирана.", tone: "success" });
      void queryClient.invalidateQueries({ queryKey: ["expense-categories"] });
    },
    onError: (error) => {
      setPageMessage({ text: localizedErrorMessage(error, "Категоријата не беше архивирана."), tone: "error" });
    },
  });

  const createExpenseMutation = useMutation({
    mutationFn: createExpense,
    onSuccess: (expenseItem) => {
      setPageMessage({ text: "Трошокот е додаден.", tone: "success" });
      setSelectedExpenseId(expenseItem.id);
      setExpenseForm((current) => ({
        ...emptyExpenseForm,
        project_id: current.project_id,
        category_id: current.category_id,
      }));
      void queryClient.invalidateQueries({ queryKey: ["expenses"] });
    },
    onError: (error) => {
      setPageMessage({ text: localizedErrorMessage(error, "Трошокот не беше додаден. Проверете ги податоците."), tone: "error" });
    },
  });

  const reverseExpenseMutation = useMutation({
    mutationFn: ({ expenseId, reason }: { expenseId: string; reason: string }) => reverseExpense(expenseId, { reason }),
    onSuccess: (expenseItem) => {
      setPageMessage({ text: "Трошокот е сторниран.", tone: "success" });
      setReverseReason("");
      void queryClient.invalidateQueries({ queryKey: ["expenses"] });
      void queryClient.invalidateQueries({ queryKey: ["expenses", expenseItem.id] });
    },
    onError: (error) => {
      setPageMessage({ text: localizedErrorMessage(error, "Трошокот не беше сторниран."), tone: "error" });
    },
  });

  const archiveExpenseMutation = useMutation({
    mutationFn: archiveExpense,
    onSuccess: (expenseItem) => {
      setPageMessage({ text: "Трошокот е архивиран.", tone: "success" });
      void queryClient.invalidateQueries({ queryKey: ["expenses"] });
      void queryClient.invalidateQueries({ queryKey: ["expenses", expenseItem.id] });
    },
    onError: (error) => {
      setPageMessage({ text: localizedErrorMessage(error, "Трошокот не беше архивиран."), tone: "error" });
    },
  });

  function handleCategoryField(field: keyof CategoryFormState) {
    return (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
      setCategoryForm((current) => ({ ...current, [field]: event.target.value }));
  }

  function handleCategoryEditField(field: keyof CategoryFormState) {
    return (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
      setCategoryEditForm((current) => ({ ...current, [field]: event.target.value }));
  }

  function handleExpenseField(field: keyof ExpenseFormState) {
    return (event: ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) =>
      setExpenseForm((current) => ({ ...current, [field]: event.target.value }));
  }

  function handleCreateCategory(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const payload = categoryPayloadFromForm(categoryForm);
    if (!payload.name) {
      setPageMessage({ text: "Внесете име на категорија.", tone: "error" });
      return;
    }

    createCategoryMutation.mutate(payload);
  }

  function handleUpdateCategory(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedCategory) {
      return;
    }

    const payload = categoryPayloadFromForm(categoryEditForm);
    if (!payload.name) {
      setPageMessage({ text: "Внесете име на категорија.", tone: "error" });
      return;
    }

    updateCategoryMutation.mutate({ categoryId: selectedCategory.id, payload });
  }

  function handleArchiveCategory() {
    if (!selectedCategory) {
      return;
    }
    if (!window.confirm("Дали сте сигурни дека сакате да ја архивирате категоријата?")) {
      return;
    }

    archiveCategoryMutation.mutate(selectedCategory.id);
  }

  function handleCreateExpense(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const payload = expensePayloadFromForm(expenseForm);
    if (!payload.description) {
      setPageMessage({ text: "Внесете опис на трошок.", tone: "error" });
      return;
    }
    if (!payload.expense_date) {
      setPageMessage({ text: "Внесете датум на трошок.", tone: "error" });
      return;
    }
    if (Number.isNaN(payload.amount) || payload.amount <= 0) {
      setPageMessage({ text: "Износот мора да биде поголем од нула.", tone: "error" });
      return;
    }

    createExpenseMutation.mutate(payload);
  }

  function handleReverseExpense() {
    if (!selectedExpense) {
      return;
    }
    const reason = reverseReason.trim();
    if (!reason) {
      setPageMessage({ text: "Внесете причина за сторно.", tone: "error" });
      return;
    }
    if (!window.confirm("Дали сте сигурни дека сакате да го сторнирате трошокот?")) {
      return;
    }

    reverseExpenseMutation.mutate({ expenseId: selectedExpense.id, reason });
  }

  function handleArchiveExpense() {
    if (!selectedExpense) {
      return;
    }
    if (!window.confirm("Дали сте сигурни дека сакате да го архивирате трошокот?")) {
      return;
    }

    archiveExpenseMutation.mutate(selectedExpense.id);
  }

  return (
    <section className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-normal text-ink">Трошоци</h1>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
          Евидентирајте категории и проектни трошоци преку податоците од серверот.
        </p>
      </div>

      {pageMessage ? <Message tone={pageMessage.tone}>{pageMessage.text}</Message> : null}

      <div className="grid gap-6 xl:grid-cols-[420px_minmax(0,1fr)]">
        <aside className="space-y-4">
          <Panel title="Категории на трошоци">
            <form onSubmit={handleCreateCategory} className="space-y-4">
              <FormField
                label="Име на категорија"
                name="expense-category-name"
                value={categoryForm.name}
                required
                onChange={handleCategoryField("name")}
              />
              <TextAreaField
                label="Опис на категорија"
                name="expense-category-description"
                value={categoryForm.description}
                onChange={handleCategoryField("description")}
              />
              <PrimaryButton disabled={createCategoryMutation.isPending}>Додај категорија</PrimaryButton>
            </form>

            <div className="mt-5 space-y-2">
              {categoriesQuery.isLoading ? <Message>Се вчитуваат категориите.</Message> : null}
              {categoriesQuery.isError ? <Message tone="error">Категориите не може да се вчитаат.</Message> : null}
              {!categoriesQuery.isLoading && categories.length === 0 ? <EmptyState>Нема категории на трошоци.</EmptyState> : null}
              {categories.map((category) => (
                <button
                  key={category.id}
                  type="button"
                  onClick={() => setSelectedCategoryId(category.id)}
                  className={[
                    "w-full rounded-md border px-3 py-2 text-left text-sm transition",
                    selectedCategory?.id === category.id
                      ? "border-brand bg-brand/10 text-brand"
                      : "border-line bg-white text-slate-700 hover:border-brand",
                  ].join(" ")}
                >
                  <span className="block font-bold">{category.name}</span>
                  <span className="mt-1 block text-xs text-slate-500">{category.description ?? "Без опис"}</span>
                </button>
              ))}
            </div>

            {selectedCategory ? (
              <form onSubmit={handleUpdateCategory} className="mt-5 space-y-4 rounded-md border border-line bg-slate-50 p-3">
                <h3 className="text-sm font-bold text-ink">Уреди категорија</h3>
                <FormField
                  label="Име за уредување на категорија"
                  name="expense-category-edit-name"
                  value={categoryEditForm.name}
                  required
                  onChange={handleCategoryEditField("name")}
                />
                <TextAreaField
                  label="Опис за уредување на категорија"
                  name="expense-category-edit-description"
                  value={categoryEditForm.description}
                  onChange={handleCategoryEditField("description")}
                />
                <div className="flex flex-wrap gap-2">
                  <button
                    type="submit"
                    className="ui-button-secondary"
                  >
                    <Save aria-hidden="true" className="h-4 w-4" />
                    Зачувај категорија
                  </button>
                  <ActionButton
                    icon={<Archive aria-hidden="true" className="h-4 w-4" />}
                    onClick={handleArchiveCategory}
                    tone="danger"
                  >
                    Архивирај категорија
                  </ActionButton>
                </div>
              </form>
            ) : null}
          </Panel>

          <Panel title="Нов трошок">
            <form onSubmit={handleCreateExpense} className="space-y-4">
              <SelectField
                label="Проект за трошок"
                name="expense-project-id"
                value={expenseForm.project_id}
                onChange={handleExpenseField("project_id")}
              >
                <option value="">Без проект</option>
                {projects.map((project) => (
                  <option key={project.id} value={project.id}>
                    {project.name}
                  </option>
                ))}
              </SelectField>
              <SelectField
                label="Категорија за трошок"
                name="expense-category-id"
                value={expenseForm.category_id}
                onChange={handleExpenseField("category_id")}
              >
                <option value="">Без категорија</option>
                {categories.map((category) => (
                  <option key={category.id} value={category.id}>
                    {category.name}
                  </option>
                ))}
              </SelectField>
              <SelectField
                label="Материјал за трошок"
                name="expense-material-id"
                value={expenseForm.material_id}
                onChange={handleExpenseField("material_id")}
              >
                <option value="">Без материјал</option>
                {materials.map((material) => (
                  <option key={material.id} value={material.id}>
                    {material.name}
                  </option>
                ))}
              </SelectField>
              <FormField
                label="Опис на трошок"
                name="expense-description"
                value={expenseForm.description}
                required
                onChange={handleExpenseField("description")}
              />
              <FormField
                label="Износ на трошок"
                name="expense-amount"
                type="number"
                value={expenseForm.amount}
                required
                onChange={handleExpenseField("amount")}
              />
              <FormField
                label="Датум на трошок"
                name="expense-date"
                type="date"
                value={expenseForm.expense_date}
                required
                onChange={handleExpenseField("expense_date")}
              />
              <SelectField
                label="Начин на плаќање за трошок"
                name="expense-payment-method"
                value={expenseForm.payment_method}
                onChange={handleExpenseField("payment_method")}
              >
                {paymentMethods.map((method) => (
                  <option key={method.value} value={method.value}>
                    {method.label}
                  </option>
                ))}
              </SelectField>
              <SelectField
                label="Статус на трошок"
                name="expense-status"
                value={expenseForm.status}
                onChange={handleExpenseField("status")}
              >
                {expenseStatuses
                  .filter((status) => ["recorded", "reimbursed"].includes(status.value))
                  .map((status) => (
                    <option key={status.value} value={status.value}>
                      {status.label}
                    </option>
                  ))}
              </SelectField>
              <TextAreaField
                label="Белешка за трошок"
                name="expense-note"
                value={expenseForm.note}
                onChange={handleExpenseField("note")}
              />
              <PrimaryButton disabled={createExpenseMutation.isPending}>Додај трошок</PrimaryButton>
            </form>
          </Panel>
        </aside>

        <div className="space-y-6">
          <Panel title="Листа на трошоци">
            {expensesQuery.isLoading ? <Message>Се вчитуваат трошоците.</Message> : null}
            {expensesQuery.isError ? <Message tone="error">Трошоците не може да се вчитаат.</Message> : null}
            {!expensesQuery.isLoading && expenses.length === 0 ? <EmptyState>Нема евидентирани трошоци.</EmptyState> : null}
            <div className="grid gap-3 lg:grid-cols-2">
              {expenses.map((expenseItem) => (
                <button
                  key={expenseItem.id}
                  type="button"
                  onClick={() => setSelectedExpenseId(expenseItem.id)}
                  className={[
                    "rounded-md border px-3 py-3 text-left transition",
                    selectedExpense?.id === expenseItem.id ? "border-brand bg-brand/10" : "border-line bg-white hover:border-brand",
                  ].join(" ")}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-sm font-bold text-ink">{expenseItem.description}</p>
                      <p className="mt-1 text-xs text-slate-500">
                        {categoryLabel(expenseItem.category_id)} - {projectLabel(expenseItem.project_id)}
                      </p>
                      <p className="mt-1 text-sm font-bold text-ink">{formatMoney(expenseItem.amount, expenseItem.currency)}</p>
                      <p className="mt-1 text-xs text-slate-500">{formatMethod(expenseItem.payment_method)}</p>
                    </div>
                    <StatusBadge status={expenseItem.status} />
                  </div>
                </button>
              ))}
            </div>
          </Panel>

          <Panel title="Детали за трошок">
            {selectedExpense ? (
              <div className="space-y-5">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <p className="text-xl font-bold tracking-normal text-ink">{selectedExpense.description}</p>
                    <p className="mt-1 text-sm text-slate-600">
                      {categoryLabel(selectedExpense.category_id)} - {projectLabel(selectedExpense.project_id)}
                    </p>
                  </div>
                  <StatusBadge status={selectedExpense.status} />
                </div>

                <dl className="grid gap-4 rounded-md border border-line bg-slate-50 p-3 sm:grid-cols-2 xl:grid-cols-4">
                  <DetailRow label="Износ" value={formatMoney(selectedExpense.amount, selectedExpense.currency)} />
                  <DetailRow label="Материјал" value={materialLabel(selectedExpense.material_id)} />
                  <DetailRow label="Начин" value={formatMethod(selectedExpense.payment_method)} />
                  <DetailRow label="Датум" value={formatDate(selectedExpense.expense_date)} />
                  <DetailRow label="Белешка" value={selectedExpense.note} />
                  <DetailRow label="Сторно причина" value={selectedExpense.reversal_reason} />
                  <DetailRow label="Сторнирано" value={selectedExpense.reversed_at ? formatDate(selectedExpense.reversed_at) : null} />
                  <DetailRow label="Архивирано" value={selectedExpense.archived_at ? formatDate(selectedExpense.archived_at) : null} />
                </dl>

                <label htmlFor="expense-reverse-reason" className="block text-sm font-semibold text-slate-700">
                  Причина за сторно трошок
                  <textarea
                    id="expense-reverse-reason"
                    value={reverseReason}
                    onChange={(event) => setReverseReason(event.target.value)}
                    rows={3}
                    className="ui-textarea"
                  />
                </label>

                <div className="flex flex-wrap gap-2">
                  <ActionButton
                    icon={<RotateCcw aria-hidden="true" className="h-4 w-4" />}
                    onClick={handleReverseExpense}
                    tone="danger"
                  >
                    Сторнирај трошок
                  </ActionButton>
                  <ActionButton
                    icon={<Archive aria-hidden="true" className="h-4 w-4" />}
                    onClick={handleArchiveExpense}
                    tone="danger"
                  >
                    Архивирај трошок
                  </ActionButton>
                </div>
              </div>
            ) : (
              <EmptyState>Изберете трошок за да ги видите деталите.</EmptyState>
            )}
          </Panel>
        </div>
      </div>
    </section>
  );
}
