import { useMutation, useQueries, useQuery, useQueryClient } from "@tanstack/react-query";
import { Archive, Check, Download, FileText, Plus, Send, XCircle } from "lucide-react";
import { useEffect, useMemo, useState, type ChangeEvent, type FormEvent, type ReactNode } from "react";

import { listCalculations } from "../api/calculations";
import { listCustomers } from "../api/customers";
import {
  archiveEstimate,
  archiveEstimateItem,
  changeEstimateStatus,
  createEstimate,
  createEstimateFromCalculation,
  createEstimateItem,
  downloadEstimateDocument,
  generateEstimatePdf,
  listEstimateItems,
  listEstimateRevisions,
  listEstimates,
  updateEstimateItem,
} from "../api/estimates";
import { listMaterials } from "../api/materials";
import { listProjects } from "../api/projects";
import type {
  CalculationRunResponse,
  CustomerResponse,
  EstimateDocumentResponse,
  EstimateItemCreateRequest,
  EstimateItemResponse,
  EstimateItemUpdateRequest,
  EstimateResponse,
  EstimateRevisionResponse,
  MaterialResponse,
  ProjectResponse,
} from "../api/types";

type MessageTone = "neutral" | "error" | "success";

type PageMessage = {
  text: string;
  tone: MessageTone;
};

type EstimateFormState = {
  project_id: string;
  title: string;
  description: string;
};

type CalculationEstimateFormState = {
  calculation_run_id: string;
  title: string;
  description: string;
};

type ItemFormState = {
  item_type: string;
  name: string;
  description: string;
  material_id: string;
  quantity: string;
  unit: string;
  unit_price: string;
};

const emptyEstimateForm: EstimateFormState = {
  project_id: "",
  title: "",
  description: "",
};

const emptyCalculationEstimateForm: CalculationEstimateFormState = {
  calculation_run_id: "",
  title: "",
  description: "",
};

const emptyItemForm: ItemFormState = {
  item_type: "service",
  name: "",
  description: "",
  material_id: "",
  quantity: "1",
  unit: "",
  unit_price: "0",
};

const emptyCustomers: CustomerResponse[] = [];
const emptyProjects: ProjectResponse[] = [];
const emptyMaterials: MaterialResponse[] = [];
const emptyCalculations: CalculationRunResponse[] = [];
const emptyEstimates: EstimateResponse[] = [];

const statusLabels: Record<string, string> = {
  accepted: "Прифатена",
  archived: "Архивирана",
  draft: "Нацрт",
  rejected: "Одбиена",
  sent: "Испратена",
};

const itemTypeLabels: Record<string, string> = {
  adjustment: "Корекција",
  discount: "Попуст",
  labor: "Работа",
  material: "Материјал",
  service: "Услуга",
};

const engineLabels: Record<string, string> = {
  concrete: "Бетон",
  facade: "Фасада",
  flooring: "Подови",
  knauf: "Кнауф",
  painting: "Бојадисување",
  tiles: "Плочки",
};

function toNullable(value: string): string | null {
  const trimmedValue = value.trim();
  return trimmedValue === "" ? null : trimmedValue;
}

function formatNumber(value: number): string {
  return value.toFixed(4).replace(/\.?0+$/, "");
}

function formatMoney(value: number | null | undefined): string {
  if (value === null || value === undefined) {
    return "Не е вратено";
  }

  return `${formatNumber(value)} MKD`;
}

function formatDate(value: string | null | undefined): string {
  if (!value) {
    return "Не е внесено";
  }

  return new Intl.DateTimeFormat("mk-MK", { dateStyle: "medium" }).format(new Date(value));
}

function formatDateTime(value: string | null | undefined): string {
  if (!value) {
    return "Не е внесено";
  }

  return new Intl.DateTimeFormat("mk-MK", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

function formatStatus(status: string): string {
  return statusLabels[status] ?? status;
}

function formatItemType(itemType: string): string {
  return itemTypeLabels[itemType] ?? itemType;
}

function formatEngine(engineType: string): string {
  return engineLabels[engineType] ?? engineType;
}

function formatDocumentType(documentType: string): string {
  if (documentType === "estimate_quote_pdf") {
    return "PDF понуда";
  }

  return documentType;
}

function localizedErrorMessage(error: unknown, fallback: string): string {
  if (error instanceof Error && /[А-џ]/.test(error.message)) {
    return error.message;
  }

  return fallback;
}

function latestRevision(revisions: EstimateRevisionResponse[]): EstimateRevisionResponse | null {
  if (revisions.length === 0) {
    return null;
  }

  return [...revisions].sort((left, right) => right.revision_number - left.revision_number)[0];
}

function isRevisionEditable(estimate: EstimateResponse | null, revision: EstimateRevisionResponse | null): boolean {
  if (!estimate || !revision) {
    return false;
  }

  return !["sent", "accepted"].includes(estimate.status) && !["sent", "accepted"].includes(revision.status);
}

function itemPayloadFromForm(form: ItemFormState): EstimateItemCreateRequest {
  return {
    item_type: form.item_type,
    name: form.name.trim(),
    description: toNullable(form.description),
    material_id: toNullable(form.material_id),
    quantity: Number(form.quantity),
    unit: toNullable(form.unit),
    unit_price: Number(form.unit_price),
  };
}

function itemFormFromItem(item: EstimateItemResponse): ItemFormState {
  return {
    item_type: item.item_type,
    name: item.name,
    description: item.description ?? "",
    material_id: item.material_id ?? "",
    quantity: String(item.quantity),
    unit: item.unit ?? "",
    unit_price: String(item.unit_price),
  };
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

function Panel({ children, title }: { children: ReactNode; title: string }) {
  return (
    <section aria-label={title} className="rounded-md border border-line bg-white p-4 shadow-sm">
      <h2 className="text-base font-bold tracking-normal text-ink">{title}</h2>
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
    <label htmlFor={name} className="block text-sm font-semibold text-slate-700">
      {label}
      <input
        id={name}
        name={name}
        type={type}
        value={value}
        required={required}
        onChange={onChange}
        className="mt-2 h-10 w-full rounded-md border border-line px-3 text-sm outline-none transition focus:border-brand focus:ring-2 focus:ring-brand/20"
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
    <label htmlFor={name} className="block text-sm font-semibold text-slate-700">
      {label}
      <textarea
        id={name}
        name={name}
        value={value}
        onChange={onChange}
        rows={3}
        className="mt-2 w-full rounded-md border border-line px-3 py-2 text-sm outline-none transition focus:border-brand focus:ring-2 focus:ring-brand/20"
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
    <label htmlFor={name} className="block text-sm font-semibold text-slate-700">
      {label}
      <select
        id={name}
        name={name}
        value={value}
        required={required}
        onChange={onChange}
        className="mt-2 h-10 w-full rounded-md border border-line bg-white px-3 text-sm outline-none transition focus:border-brand focus:ring-2 focus:ring-brand/20"
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

  return <p className={`rounded-md border px-3 py-2 text-sm ${toneClass}`}>{children}</p>;
}

function EmptyState({ children }: { children: ReactNode }) {
  return <p className="rounded-md border border-dashed border-line bg-slate-50 px-3 py-4 text-sm text-slate-600">{children}</p>;
}

function PrimaryButton({ children, disabled = false }: { children: ReactNode; disabled?: boolean }) {
  return (
    <button
      type="submit"
      disabled={disabled}
      className="inline-flex h-10 items-center justify-center gap-2 rounded-md bg-brand px-3 text-sm font-bold text-white transition hover:bg-teal-800 focus:outline-none focus:ring-2 focus:ring-brand focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-70"
    >
      <Plus aria-hidden="true" className="h-4 w-4" />
      {children}
    </button>
  );
}

function ActionButton({
  children,
  disabled = false,
  icon,
  onClick,
  tone = "neutral",
}: {
  children: ReactNode;
  disabled?: boolean;
  icon: ReactNode;
  onClick: () => void;
  tone?: "neutral" | "success" | "danger";
}) {
  const toneClass =
    tone === "danger"
      ? "border-red-200 text-red-800 hover:border-red-400 hover:bg-red-50"
      : tone === "success"
        ? "border-emerald-200 text-emerald-800 hover:border-emerald-400 hover:bg-emerald-50"
        : "border-line text-slate-700 hover:border-brand hover:text-brand";

  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className={`inline-flex h-10 items-center justify-center gap-2 rounded-md border bg-white px-3 text-sm font-semibold transition focus:outline-none focus:ring-2 focus:ring-brand focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-70 ${toneClass}`}
    >
      {icon}
      {children}
    </button>
  );
}

function StatusBadge({ status }: { status: string }) {
  const statusClass =
    status === "accepted"
      ? "border-emerald-200 bg-emerald-50 text-emerald-800"
      : status === "rejected" || status === "archived"
        ? "border-red-200 bg-red-50 text-red-800"
        : status === "sent"
          ? "border-sky-200 bg-sky-50 text-sky-800"
          : "border-line bg-slate-50 text-slate-700";

  return (
    <span className={`inline-flex items-center rounded-md border px-2 py-1 text-xs font-bold ${statusClass}`}>
      {formatStatus(status)}
    </span>
  );
}

function TotalTile({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-line bg-slate-50 px-3 py-3">
      <p className="text-xs font-semibold uppercase text-slate-500">{label}</p>
      <p className="mt-1 text-lg font-bold tracking-normal text-ink">{value}</p>
    </div>
  );
}

export function EstimatesPage() {
  const queryClient = useQueryClient();
  const [selectedEstimateId, setSelectedEstimateId] = useState<string | null>(null);
  const [selectedRevisionId, setSelectedRevisionId] = useState<string | null>(null);
  const [selectedItemId, setSelectedItemId] = useState<string | null>(null);
  const [estimateForm, setEstimateForm] = useState<EstimateFormState>(emptyEstimateForm);
  const [calculationForm, setCalculationForm] = useState<CalculationEstimateFormState>(emptyCalculationEstimateForm);
  const [itemForm, setItemForm] = useState<ItemFormState>(emptyItemForm);
  const [itemEditForm, setItemEditForm] = useState<ItemFormState>(emptyItemForm);
  const [pageMessage, setPageMessage] = useState<PageMessage | null>(null);
  const [pdfDocumentsByEstimateId, setPdfDocumentsByEstimateId] = useState<Record<string, EstimateDocumentResponse[]>>({});

  const customersQuery = useQuery({ queryKey: ["customers"], queryFn: listCustomers });
  const projectsQuery = useQuery({ queryKey: ["projects"], queryFn: listProjects });
  const materialsQuery = useQuery({ queryKey: ["materials"], queryFn: listMaterials });
  const calculationsQuery = useQuery({ queryKey: ["calculations"], queryFn: listCalculations });
  const estimatesQuery = useQuery({ queryKey: ["estimates"], queryFn: listEstimates });

  const estimates = estimatesQuery.data ?? emptyEstimates;
  const customers = customersQuery.data ?? emptyCustomers;
  const projects = projectsQuery.data ?? emptyProjects;
  const materials = materialsQuery.data ?? emptyMaterials;
  const calculations = calculationsQuery.data ?? emptyCalculations;
  const completedCalculations = useMemo(
    () => calculations.filter((calculation) => calculation.status === "completed"),
    [calculations],
  );

  const revisionQueries = useQueries({
    queries: estimates.map((estimate) => ({
      queryKey: ["estimate-revisions", estimate.id],
      queryFn: () => listEstimateRevisions(estimate.id),
    })),
  });

  const revisionsByEstimateId = useMemo(() => {
    const revisionsMap = new Map<string, EstimateRevisionResponse[]>();
    estimates.forEach((estimate, index) => {
      revisionsMap.set(estimate.id, revisionQueries[index]?.data ?? []);
    });
    return revisionsMap;
  }, [estimates, revisionQueries]);

  const selectedEstimate =
    estimates.find((estimate) => estimate.id === selectedEstimateId) ?? (estimates.length > 0 ? estimates[0] : null);
  const selectedRevisions = selectedEstimate ? (revisionsByEstimateId.get(selectedEstimate.id) ?? []) : [];
  const selectedRevision =
    selectedRevisions.find((revision) => revision.id === selectedRevisionId) ?? latestRevision(selectedRevisions);
  const selectedPdfDocuments = selectedEstimate ? (pdfDocumentsByEstimateId[selectedEstimate.id] ?? []) : [];

  const itemsQuery = useQuery({
    queryKey: ["estimate-items", selectedRevision?.id],
    queryFn: () => listEstimateItems(selectedRevision?.id ?? ""),
    enabled: Boolean(selectedRevision?.id),
  });

  const items = itemsQuery.data ?? [];
  const selectedItem = items.find((item) => item.id === selectedItemId) ?? (items.length > 0 ? items[0] : null);
  const canEditRevision = isRevisionEditable(selectedEstimate, selectedRevision);

  const customerLabel = (customerId: string | null) =>
    selectLabel<CustomerResponse>(customers, customerId, (customer) => customer.name, "Без клиент");
  const projectLabel = (projectId: string | null) =>
    selectLabel<ProjectResponse>(projects, projectId, (project) => project.name, "Без проект");
  const materialLabel = (materialId: string | null) =>
    selectLabel<MaterialResponse>(materials, materialId, (material) => material.name, "Без материјал");
  const calculationLabel = (calculation: CalculationRunResponse) =>
    `${formatEngine(calculation.engine_type)} - ${projectLabel(calculation.project_id)} - ${formatDate(calculation.created_at)}`;

  useEffect(() => {
    if (!selectedEstimateId && estimates.length > 0) {
      setSelectedEstimateId(estimates[0].id);
    }
  }, [estimates, selectedEstimateId]);

  useEffect(() => {
    if (!estimateForm.project_id && projects.length > 0) {
      setEstimateForm((current) => ({ ...current, project_id: projects[0].id }));
    }
  }, [estimateForm.project_id, projects]);

  useEffect(() => {
    if (!calculationForm.calculation_run_id && completedCalculations.length > 0) {
      setCalculationForm((current) => ({ ...current, calculation_run_id: completedCalculations[0].id }));
    }
  }, [calculationForm.calculation_run_id, completedCalculations]);

  useEffect(() => {
    if (selectedRevision && selectedRevision.id !== selectedRevisionId) {
      setSelectedRevisionId(selectedRevision.id);
    }
  }, [selectedRevision, selectedRevisionId]);

  useEffect(() => {
    if (selectedItem && selectedItem.id !== selectedItemId) {
      setSelectedItemId(selectedItem.id);
    }
  }, [selectedItem, selectedItemId]);

  useEffect(() => {
    if (selectedItem) {
      setItemEditForm(itemFormFromItem(selectedItem));
    }
  }, [selectedItem]);

  const refreshSelectedEstimate = (estimateId: string | null, revisionId: string | null) => {
    void queryClient.invalidateQueries({ queryKey: ["estimates"] });
    if (estimateId) {
      void queryClient.invalidateQueries({ queryKey: ["estimate-revisions", estimateId] });
    }
    if (revisionId) {
      void queryClient.invalidateQueries({ queryKey: ["estimate-items", revisionId] });
    }
  };

  const createEstimateMutation = useMutation({
    mutationFn: createEstimate,
    onSuccess: (estimate) => {
      setPageMessage({ text: "Понудата е креирана.", tone: "success" });
      setSelectedEstimateId(estimate.id);
      setEstimateForm((current) => ({ ...emptyEstimateForm, project_id: current.project_id }));
      refreshSelectedEstimate(estimate.id, null);
    },
    onError: (error) => {
      setPageMessage({ text: localizedErrorMessage(error, "Понудата не беше креирана. Проверете ги внесените податоци."), tone: "error" });
    },
  });

  const createFromCalculationMutation = useMutation({
    mutationFn: ({ calculationRunId, title, description }: { calculationRunId: string; title: string | null; description: string | null }) =>
      createEstimateFromCalculation(calculationRunId, { title, description }),
    onSuccess: (estimate) => {
      setPageMessage({ text: "Понудата од пресметка е креирана.", tone: "success" });
      setSelectedEstimateId(estimate.id);
      setCalculationForm((current) => ({ ...emptyCalculationEstimateForm, calculation_run_id: current.calculation_run_id }));
      refreshSelectedEstimate(estimate.id, null);
    },
    onError: (error) => {
      setPageMessage({
        text: localizedErrorMessage(error, "Понудата од пресметка не беше креирана. Проверете ја избраната пресметка."),
        tone: "error",
      });
    },
  });

  const createItemMutation = useMutation({
    mutationFn: ({ revisionId, payload }: { revisionId: string; payload: EstimateItemCreateRequest }) =>
      createEstimateItem(revisionId, payload),
    onSuccess: () => {
      setPageMessage({ text: "Ставката е додадена.", tone: "success" });
      setItemForm(emptyItemForm);
      refreshSelectedEstimate(selectedEstimate?.id ?? null, selectedRevision?.id ?? null);
    },
    onError: (error) => {
      setPageMessage({ text: localizedErrorMessage(error, "Ставката не беше зачувана. Проверете ги внесените податоци."), tone: "error" });
    },
  });

  const updateItemMutation = useMutation({
    mutationFn: ({ itemId, payload }: { itemId: string; payload: EstimateItemUpdateRequest }) => updateEstimateItem(itemId, payload),
    onSuccess: () => {
      setPageMessage({ text: "Ставката е зачувана.", tone: "success" });
      refreshSelectedEstimate(selectedEstimate?.id ?? null, selectedRevision?.id ?? null);
    },
    onError: (error) => {
      setPageMessage({ text: localizedErrorMessage(error, "Ставката не беше зачувана. Проверете ги внесените податоци."), tone: "error" });
    },
  });

  const archiveItemMutation = useMutation({
    mutationFn: archiveEstimateItem,
    onSuccess: () => {
      setPageMessage({ text: "Ставката е архивирана.", tone: "success" });
      refreshSelectedEstimate(selectedEstimate?.id ?? null, selectedRevision?.id ?? null);
    },
    onError: (error) => {
      setPageMessage({ text: localizedErrorMessage(error, "Ставката не беше архивирана."), tone: "error" });
    },
  });

  const statusMutation = useMutation({
    mutationFn: ({ estimateId, status }: { estimateId: string; status: string }) => changeEstimateStatus(estimateId, { status }),
    onSuccess: (estimate) => {
      setPageMessage({ text: "Статусот на понудата е променет.", tone: "success" });
      refreshSelectedEstimate(estimate.id, selectedRevision?.id ?? null);
    },
    onError: (error) => {
      setPageMessage({ text: localizedErrorMessage(error, "Статусот не беше променет."), tone: "error" });
    },
  });

  const archiveEstimateMutation = useMutation({
    mutationFn: archiveEstimate,
    onSuccess: (estimate) => {
      setPageMessage({ text: "Понудата е архивирана.", tone: "success" });
      refreshSelectedEstimate(estimate.id, selectedRevision?.id ?? null);
    },
    onError: (error) => {
      setPageMessage({ text: localizedErrorMessage(error, "Понудата не беше архивирана."), tone: "error" });
    },
  });

  const generatePdfMutation = useMutation({
    mutationFn: ({ estimateId, revisionId }: { estimateId: string; revisionId: string | null }) =>
      generateEstimatePdf(estimateId, { revision_id: revisionId }),
    onSuccess: (document) => {
      setPageMessage({ text: "PDF понудата е генерирана.", tone: "success" });
      setPdfDocumentsByEstimateId((current) => {
        const existingDocuments = current[document.estimate_id] ?? [];
        const withoutDuplicate = existingDocuments.filter((item) => item.id !== document.id);
        return {
          ...current,
          [document.estimate_id]: [document, ...withoutDuplicate],
        };
      });
    },
    onError: (error) => {
      setPageMessage({ text: localizedErrorMessage(error, "PDF понудата не беше генерирана."), tone: "error" });
    },
  });

  const downloadPdfMutation = useMutation({
    mutationFn: async (document: EstimateDocumentResponse) => ({
      blob: await downloadEstimateDocument(document.id),
      document,
    }),
    onSuccess: ({ blob, document }) => {
      const objectUrl = URL.createObjectURL(blob);
      const link = window.document.createElement("a");
      link.href = objectUrl;
      link.download = `ponuda-${document.estimate_id}-${document.revision_id}.pdf`;
      window.document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(objectUrl);
      setPageMessage({ text: "PDF документот е преземен.", tone: "success" });
    },
    onError: (error) => {
      setPageMessage({ text: localizedErrorMessage(error, "PDF документот не може да се преземе."), tone: "error" });
    },
  });

  function handleEstimateFormField(field: keyof EstimateFormState) {
    return (event: ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) =>
      setEstimateForm((current) => ({ ...current, [field]: event.target.value }));
  }

  function handleCalculationFormField(field: keyof CalculationEstimateFormState) {
    return (event: ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) =>
      setCalculationForm((current) => ({ ...current, [field]: event.target.value }));
  }

  function handleItemFormField(field: keyof ItemFormState) {
    return (event: ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
      setItemForm((current) => ({ ...current, [field]: event.target.value }));
  }

  function handleItemEditFormField(field: keyof ItemFormState) {
    return (event: ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
      setItemEditForm((current) => ({ ...current, [field]: event.target.value }));
  }

  function handleCreateEstimate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!estimateForm.project_id) {
      setPageMessage({ text: "Изберете проект за понудата.", tone: "error" });
      return;
    }
    if (!estimateForm.title.trim()) {
      setPageMessage({ text: "Внесете наслов на понудата.", tone: "error" });
      return;
    }

    createEstimateMutation.mutate({
      project_id: estimateForm.project_id,
      customer_id: null,
      property_id: null,
      title: estimateForm.title.trim(),
      description: toNullable(estimateForm.description),
    });
  }

  function handleCreateFromCalculation(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!calculationForm.calculation_run_id) {
      setPageMessage({ text: "Изберете завршена пресметка.", tone: "error" });
      return;
    }

    createFromCalculationMutation.mutate({
      calculationRunId: calculationForm.calculation_run_id,
      title: toNullable(calculationForm.title),
      description: toNullable(calculationForm.description),
    });
  }

  function handleCreateItem(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedRevision) {
      setPageMessage({ text: "Изберете ревизија за ставката.", tone: "error" });
      return;
    }
    const payload = itemPayloadFromForm(itemForm);
    if (!payload.name) {
      setPageMessage({ text: "Внесете име на ставка.", tone: "error" });
      return;
    }
    if (Number.isNaN(payload.quantity) || payload.quantity < 0) {
      setPageMessage({ text: "Количината мора да биде позитивна.", tone: "error" });
      return;
    }
    if (Number.isNaN(payload.unit_price) || payload.unit_price < 0) {
      setPageMessage({ text: "Единечната цена мора да биде позитивна.", tone: "error" });
      return;
    }

    createItemMutation.mutate({ revisionId: selectedRevision.id, payload });
  }

  function handleUpdateItem(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedItem) {
      return;
    }
    const payload = itemPayloadFromForm(itemEditForm);
    updateItemMutation.mutate({ itemId: selectedItem.id, payload });
  }

  function handleEstimateStatus(status: string) {
    if (!selectedEstimate) {
      return;
    }

    statusMutation.mutate({ estimateId: selectedEstimate.id, status });
  }

  function handleArchiveEstimate() {
    if (selectedEstimate) {
      archiveEstimateMutation.mutate(selectedEstimate.id);
    }
  }

  function handleArchiveItem() {
    if (selectedItem) {
      archiveItemMutation.mutate(selectedItem.id);
    }
  }

  function handleGeneratePdf() {
    if (!selectedEstimate) {
      return;
    }

    generatePdfMutation.mutate({
      estimateId: selectedEstimate.id,
      revisionId: selectedRevision?.id ?? null,
    });
  }

  function handleDownloadPdf(documentId: string) {
    const document = selectedPdfDocuments.find((item) => item.id === documentId);
    if (!document) {
      setPageMessage({ text: "PDF документот не е достапен за преземање.", tone: "error" });
      return;
    }

    downloadPdfMutation.mutate(document);
  }

  return (
    <section className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-normal text-ink">Понуди</h1>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
          Креирајте понуди од проект или завршена пресметка и прегледајте ги ревизиите што ги враќа серверот.
        </p>
      </div>

      {pageMessage ? <Message tone={pageMessage.tone}>{pageMessage.text}</Message> : null}

      <div className="grid gap-6 xl:grid-cols-[420px_minmax(0,1fr)]">
        <aside className="space-y-4">
          <Panel title="Нова понуда">
            <form onSubmit={handleCreateEstimate} className="space-y-4">
              <SelectField
                label="Проект за понуда"
                name="estimate-project-id"
                value={estimateForm.project_id}
                required
                onChange={handleEstimateFormField("project_id")}
              >
                <option value="">Изберете проект</option>
                {projects.map((project) => (
                  <option key={project.id} value={project.id}>
                    {project.name}
                  </option>
                ))}
              </SelectField>
              <FormField
                label="Наслов на понуда"
                name="estimate-title"
                value={estimateForm.title}
                required
                onChange={handleEstimateFormField("title")}
              />
              <TextAreaField
                label="Опис на понуда"
                name="estimate-description"
                value={estimateForm.description}
                onChange={handleEstimateFormField("description")}
              />
              <PrimaryButton disabled={createEstimateMutation.isPending}>Креирај понуда</PrimaryButton>
            </form>
          </Panel>

          <Panel title="Понуда од пресметка">
            <form onSubmit={handleCreateFromCalculation} className="space-y-4">
              <SelectField
                label="Пресметка за понуда"
                name="estimate-calculation-id"
                value={calculationForm.calculation_run_id}
                required
                onChange={handleCalculationFormField("calculation_run_id")}
              >
                <option value="">Изберете завршена пресметка</option>
                {completedCalculations.map((calculation) => (
                  <option key={calculation.id} value={calculation.id}>
                    {calculationLabel(calculation)}
                  </option>
                ))}
              </SelectField>
              <FormField
                label="Наслов од пресметка"
                name="estimate-calculation-title"
                value={calculationForm.title}
                onChange={handleCalculationFormField("title")}
              />
              <TextAreaField
                label="Опис од пресметка"
                name="estimate-calculation-description"
                value={calculationForm.description}
                onChange={handleCalculationFormField("description")}
              />
              <PrimaryButton disabled={createFromCalculationMutation.isPending}>Креирај од пресметка</PrimaryButton>
            </form>
          </Panel>
        </aside>

        <div className="space-y-6">
          <Panel title="Листа на понуди">
            {estimatesQuery.isLoading ? <Message>Се вчитуваат понудите.</Message> : null}
            {estimatesQuery.isError ? <Message tone="error">Понудите не може да се вчитаат.</Message> : null}
            {!estimatesQuery.isLoading && estimates.length === 0 ? <EmptyState>Нема креирани понуди.</EmptyState> : null}
            <div className="grid gap-3 lg:grid-cols-2">
              {estimates.map((estimateItem) => {
                const revision = latestRevision(revisionsByEstimateId.get(estimateItem.id) ?? []);
                return (
                  <button
                    key={estimateItem.id}
                    type="button"
                    onClick={() => {
                      setSelectedEstimateId(estimateItem.id);
                      setSelectedRevisionId(null);
                    }}
                    className={[
                      "rounded-md border px-3 py-3 text-left transition",
                      selectedEstimate?.id === estimateItem.id ? "border-brand bg-brand/10" : "border-line bg-white hover:border-brand",
                    ].join(" ")}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="text-sm font-bold text-ink">{estimateItem.title}</p>
                        <p className="mt-1 text-xs text-slate-500">
                          {customerLabel(estimateItem.customer_id)} - {projectLabel(estimateItem.project_id)}
                        </p>
                        <p className="mt-1 text-xs text-slate-500">{formatDate(estimateItem.created_at)}</p>
                        <p className="mt-2 text-sm font-bold text-ink">{formatMoney(revision?.total)}</p>
                      </div>
                      <StatusBadge status={estimateItem.status} />
                    </div>
                  </button>
                );
              })}
            </div>
          </Panel>

          <Panel title="Детали за понуда">
            {selectedEstimate ? (
              <EstimateDetail
                canEditRevision={canEditRevision}
                customerName={customerLabel(selectedEstimate.customer_id)}
                downloadingDocumentId={downloadPdfMutation.isPending ? (downloadPdfMutation.variables?.id ?? null) : null}
                estimate={selectedEstimate}
                itemEditForm={itemEditForm}
                itemForm={itemForm}
                items={items}
                itemsLoading={itemsQuery.isLoading}
                materialLabel={materialLabel}
                materials={materials}
                onArchiveEstimate={handleArchiveEstimate}
                onArchiveItem={handleArchiveItem}
                onCreateItem={handleCreateItem}
                onDownloadPdf={handleDownloadPdf}
                onEditItemField={handleItemEditFormField}
                onGeneratePdf={handleGeneratePdf}
                onItemField={handleItemFormField}
                onRevisionSelect={setSelectedRevisionId}
                onSelectedItemChange={setSelectedItemId}
                onStatusChange={handleEstimateStatus}
                onUpdateItem={handleUpdateItem}
                pdfDocuments={selectedPdfDocuments}
                pdfGenerating={generatePdfMutation.isPending}
                projectName={projectLabel(selectedEstimate.project_id)}
                revisions={selectedRevisions}
                selectedItem={selectedItem}
                selectedRevision={selectedRevision}
              />
            ) : (
              <EmptyState>Изберете понуда за да ги видите деталите.</EmptyState>
            )}
          </Panel>
        </div>
      </div>
    </section>
  );
}

function EstimateDetail({
  canEditRevision,
  customerName,
  downloadingDocumentId,
  estimate,
  itemEditForm,
  itemForm,
  items,
  itemsLoading,
  materialLabel,
  materials,
  onArchiveEstimate,
  onArchiveItem,
  onCreateItem,
  onDownloadPdf,
  onEditItemField,
  onGeneratePdf,
  onItemField,
  onRevisionSelect,
  onSelectedItemChange,
  onStatusChange,
  onUpdateItem,
  pdfDocuments,
  pdfGenerating,
  projectName,
  revisions,
  selectedItem,
  selectedRevision,
}: {
  canEditRevision: boolean;
  customerName: string;
  downloadingDocumentId: string | null;
  estimate: EstimateResponse;
  itemEditForm: ItemFormState;
  itemForm: ItemFormState;
  items: EstimateItemResponse[];
  itemsLoading: boolean;
  materialLabel: (materialId: string | null) => string;
  materials: MaterialResponse[];
  onArchiveEstimate: () => void;
  onArchiveItem: () => void;
  onCreateItem: (event: FormEvent<HTMLFormElement>) => void;
  onDownloadPdf: (documentId: string) => void;
  onEditItemField: (field: keyof ItemFormState) => (event: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => void;
  onGeneratePdf: () => void;
  onItemField: (field: keyof ItemFormState) => (event: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => void;
  onRevisionSelect: (revisionId: string) => void;
  onSelectedItemChange: (itemId: string) => void;
  onStatusChange: (status: string) => void;
  onUpdateItem: (event: FormEvent<HTMLFormElement>) => void;
  pdfDocuments: EstimateDocumentResponse[];
  pdfGenerating: boolean;
  projectName: string;
  revisions: EstimateRevisionResponse[];
  selectedItem: EstimateItemResponse | null;
  selectedRevision: EstimateRevisionResponse | null;
}) {
  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-xl font-bold tracking-normal text-ink">{estimate.title}</p>
          <p className="mt-1 text-sm text-slate-600">
            {customerName} - {projectName}
          </p>
          <p className="mt-1 text-xs text-slate-500">{estimate.estimate_number ?? "Без број на понуда"}</p>
        </div>
        <StatusBadge status={estimate.status} />
      </div>

      <dl className="grid gap-4 rounded-md border border-line bg-slate-50 p-3 sm:grid-cols-2 xl:grid-cols-4">
        <div>
          <dt className="text-xs font-semibold uppercase text-slate-500">Клиент</dt>
          <dd className="mt-1 text-sm text-slate-800">{customerName}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-slate-500">Проект</dt>
          <dd className="mt-1 text-sm text-slate-800">{projectName}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-slate-500">Креирана</dt>
          <dd className="mt-1 text-sm text-slate-800">{formatDate(estimate.created_at)}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-slate-500">Извор</dt>
          <dd className="mt-1 text-sm text-slate-800">
            {estimate.source_calculation_run_id ? "Од пресметка" : "Рачна понуда"}
          </dd>
        </div>
      </dl>

      <div className="flex flex-wrap gap-2">
        <ActionButton icon={<Send aria-hidden="true" className="h-4 w-4" />} onClick={() => onStatusChange("sent")}>
          Означи како испратена
        </ActionButton>
        <ActionButton icon={<Check aria-hidden="true" className="h-4 w-4" />} onClick={() => onStatusChange("accepted")} tone="success">
          Означи како прифатена
        </ActionButton>
        <ActionButton icon={<XCircle aria-hidden="true" className="h-4 w-4" />} onClick={() => onStatusChange("rejected")} tone="danger">
          Означи како одбиена
        </ActionButton>
        <ActionButton icon={<Archive aria-hidden="true" className="h-4 w-4" />} onClick={onArchiveEstimate} tone="danger">
          Архивирај понуда
        </ActionButton>
        <ActionButton
          disabled={pdfGenerating}
          icon={<FileText aria-hidden="true" className="h-4 w-4" />}
          onClick={onGeneratePdf}
          tone="success"
        >
          {pdfGenerating ? "Се генерира PDF" : "Генерирај PDF понуда"}
        </ActionButton>
      </div>

      <div className="rounded-md border border-line bg-slate-50 p-3">
        <h3 className="text-sm font-bold text-ink">Генерирани PDF документи</h3>
        {pdfDocuments.length === 0 ? (
          <p className="mt-2 text-sm text-slate-600">Нема генерирани PDF документи за оваа понуда.</p>
        ) : (
          <div className="mt-3 grid gap-3 lg:grid-cols-2">
            {pdfDocuments.map((document) => (
              <div key={document.id} className="rounded-md border border-line bg-white p-3">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="text-sm font-bold text-ink">{formatDocumentType(document.document_type)}</p>
                    <p className="mt-1 text-xs text-slate-500">{formatDateTime(document.generated_at)}</p>
                  </div>
                  <ActionButton
                    disabled={downloadingDocumentId === document.id}
                    icon={<Download aria-hidden="true" className="h-4 w-4" />}
                    onClick={() => onDownloadPdf(document.id)}
                  >
                    {downloadingDocumentId === document.id ? "Се презема" : "Преземи PDF"}
                  </ActionButton>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div>
        <h3 className="text-sm font-bold text-ink">Ревизии</h3>
        <div className="mt-3 flex flex-wrap gap-2">
          {revisions.map((revision) => (
            <button
              key={revision.id}
              type="button"
              onClick={() => onRevisionSelect(revision.id)}
              className={[
                "rounded-md border px-3 py-2 text-sm font-semibold transition",
                selectedRevision?.id === revision.id ? "border-brand bg-brand/10 text-brand" : "border-line bg-white text-slate-700",
              ].join(" ")}
            >
              Ревизија {revision.revision_number}
            </button>
          ))}
        </div>
      </div>

      {selectedRevision ? (
        <>
          <div>
            <h3 className="text-sm font-bold text-ink">Вкупно за тековна ревизија</h3>
            <div className="mt-3 grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
              <TotalTile label="Меѓузбир" value={formatMoney(selectedRevision.subtotal)} />
              <TotalTile label="Попуст" value={formatMoney(selectedRevision.discount_total)} />
              <TotalTile label="Корекција" value={formatMoney(selectedRevision.adjustment_total)} />
              <TotalTile label="Данок" value={formatMoney(selectedRevision.tax_total)} />
              <TotalTile label="Вкупно" value={formatMoney(selectedRevision.total)} />
            </div>
          </div>

          {canEditRevision ? (
            <form onSubmit={onCreateItem} className="space-y-4 rounded-md border border-line bg-slate-50 p-3">
              <h3 className="text-sm font-bold text-ink">Нова ставка</h3>
              <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
                <SelectField label="Тип на ставка" name="estimate-item-type" value={itemForm.item_type} onChange={onItemField("item_type")}>
                  {Object.entries(itemTypeLabels).map(([value, label]) => (
                    <option key={value} value={value}>
                      {label}
                    </option>
                  ))}
                </SelectField>
                <FormField label="Име на ставка" name="estimate-item-name" value={itemForm.name} required onChange={onItemField("name")} />
                <SelectField
                  label="Материјал за ставка"
                  name="estimate-item-material"
                  value={itemForm.material_id}
                  onChange={onItemField("material_id")}
                >
                  <option value="">Без материјал</option>
                  {materials.map((material) => (
                    <option key={material.id} value={material.id}>
                      {material.name}
                    </option>
                  ))}
                </SelectField>
                <FormField
                  label="Количина на ставка"
                  name="estimate-item-quantity"
                  type="number"
                  value={itemForm.quantity}
                  onChange={onItemField("quantity")}
                />
                <FormField label="Единица на ставка" name="estimate-item-unit" value={itemForm.unit} onChange={onItemField("unit")} />
                <FormField
                  label="Единечна цена"
                  name="estimate-item-unit-price"
                  type="number"
                  value={itemForm.unit_price}
                  onChange={onItemField("unit_price")}
                />
              </div>
              <FormField label="Опис на ставка" name="estimate-item-description" value={itemForm.description} onChange={onItemField("description")} />
              <PrimaryButton>Додај ставка</PrimaryButton>
            </form>
          ) : (
            <Message>Оваа ревизија не може да се менува по испраќање или прифаќање.</Message>
          )}

          <div>
            <h3 className="text-sm font-bold text-ink">Ставки</h3>
            {itemsLoading ? <Message>Се вчитуваат ставките.</Message> : null}
            {!itemsLoading && items.length === 0 ? <EmptyState>Нема ставки во оваа ревизија.</EmptyState> : null}
            {items.length > 0 ? (
              <div className="mt-3 overflow-x-auto rounded-md border border-line">
                <table className="min-w-full divide-y divide-line text-sm">
                  <thead className="bg-slate-50 text-left text-xs uppercase text-slate-500">
                    <tr>
                      <th className="px-3 py-2">Име</th>
                      <th className="px-3 py-2">Тип</th>
                      <th className="px-3 py-2">Материјал</th>
                      <th className="px-3 py-2">Количина</th>
                      <th className="px-3 py-2">Единечна цена</th>
                      <th className="px-3 py-2">Вкупно</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-line bg-white">
                    {items.map((item) => (
                      <tr
                        key={item.id}
                        onClick={() => onSelectedItemChange(item.id)}
                        className={selectedItem?.id === item.id ? "bg-brand/10" : "cursor-pointer"}
                      >
                        <td className="px-3 py-2 font-semibold text-ink">{item.name}</td>
                        <td className="px-3 py-2 text-slate-700">{formatItemType(item.item_type)}</td>
                        <td className="px-3 py-2 text-slate-700">{materialLabel(item.material_id)}</td>
                        <td className="px-3 py-2 text-slate-700">
                          {formatNumber(item.quantity)} {item.unit ?? ""}
                        </td>
                        <td className="px-3 py-2 text-slate-700">{formatMoney(item.unit_price)}</td>
                        <td className="px-3 py-2 text-slate-700">{formatMoney(item.total_price)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : null}
          </div>

          {canEditRevision && selectedItem ? (
            <form onSubmit={onUpdateItem} className="space-y-4 rounded-md border border-line bg-slate-50 p-3">
              <h3 className="text-sm font-bold text-ink">Уреди ставка</h3>
              <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
                <SelectField
                  label="Тип за уредување на ставка"
                  name="estimate-edit-item-type"
                  value={itemEditForm.item_type}
                  onChange={onEditItemField("item_type")}
                >
                  {Object.entries(itemTypeLabels).map(([value, label]) => (
                    <option key={value} value={value}>
                      {label}
                    </option>
                  ))}
                </SelectField>
                <FormField
                  label="Име за уредување на ставка"
                  name="estimate-edit-item-name"
                  value={itemEditForm.name}
                  required
                  onChange={onEditItemField("name")}
                />
                <SelectField
                  label="Материјал за уредување на ставка"
                  name="estimate-edit-item-material"
                  value={itemEditForm.material_id}
                  onChange={onEditItemField("material_id")}
                >
                  <option value="">Без материјал</option>
                  {materials.map((material) => (
                    <option key={material.id} value={material.id}>
                      {material.name}
                    </option>
                  ))}
                </SelectField>
                <FormField
                  label="Количина за уредување на ставка"
                  name="estimate-edit-item-quantity"
                  type="number"
                  value={itemEditForm.quantity}
                  onChange={onEditItemField("quantity")}
                />
                <FormField
                  label="Единица за уредување на ставка"
                  name="estimate-edit-item-unit"
                  value={itemEditForm.unit}
                  onChange={onEditItemField("unit")}
                />
                <FormField
                  label="Единечна цена за уредување"
                  name="estimate-edit-item-unit-price"
                  type="number"
                  value={itemEditForm.unit_price}
                  onChange={onEditItemField("unit_price")}
                />
              </div>
              <FormField
                label="Опис за уредување на ставка"
                name="estimate-edit-item-description"
                value={itemEditForm.description}
                onChange={onEditItemField("description")}
              />
              <div className="flex flex-wrap gap-2">
                <PrimaryButton>Зачувај ставка</PrimaryButton>
                <ActionButton icon={<Archive aria-hidden="true" className="h-4 w-4" />} onClick={onArchiveItem} tone="danger">
                  Архивирај ставка
                </ActionButton>
              </div>
            </form>
          ) : null}
        </>
      ) : (
        <EmptyState>Нема ревизии за оваа понуда.</EmptyState>
      )}
    </div>
  );
}
