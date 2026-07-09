import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { FileText, Play } from "lucide-react";
import { useEffect, useMemo, useState, type ChangeEvent, type FormEvent, type ReactNode } from "react";

import { getCalculation, listCalculationEngines, listCalculations, runCalculation } from "../api/calculations";
import { createEstimateFromCalculation } from "../api/estimates";
import { listMaterials } from "../api/materials";
import { listMeasurementSets } from "../api/measurements";
import { listProjectTasks, listProjects } from "../api/projects";
import { listProjectRooms } from "../api/rooms";
import type {
  CalculationRunCreateRequest,
  CalculationRunResponse,
  MaterialResponse,
  MeasurementSetResponse,
  ProjectResponse,
  ProjectTaskResponse,
  RoomResponse,
} from "../api/types";
import { formatDate, formatUnit } from "../lib/format";

type PaintingFormState = {
  project_id: string;
  project_task_id: string;
  room_id: string;
  measurement_set_id: string;
  include_walls: boolean;
  include_ceiling: boolean;
  coats: string;
  primer_coats: string;
  paint_material_id: string;
  primer_material_id: string;
  waste_percentage: string;
  labor_rate_per_m2: string;
  notes: string;
};

type MessageTone = "neutral" | "error" | "success";

type PageMessage = {
  text: string;
  tone: MessageTone;
};

const emptyPaintingForm: PaintingFormState = {
  project_id: "",
  project_task_id: "",
  room_id: "",
  measurement_set_id: "",
  include_walls: true,
  include_ceiling: true,
  coats: "2",
  primer_coats: "0",
  paint_material_id: "",
  primer_material_id: "",
  waste_percentage: "",
  labor_rate_per_m2: "",
  notes: "",
};

const engineLabels: Record<string, string> = {
  concrete: "Бетон",
  facade: "Фасада",
  flooring: "Подови",
  knauf: "Кнауф",
  painting: "Бојадисување",
  tiles: "Плочки",
};

const calculationStatusLabels: Record<string, string> = {
  archived: "Архивирана",
  completed: "Завршена",
  draft: "Нацрт",
  failed: "Неуспешна",
};

const outputLabels: Array<{ key: string; label: string; unit?: "liter" | "money" | "percent" | "m2" }> = [
  { key: "selected_area_m2", label: "Избрана површина", unit: "m2" },
  { key: "wall_area_net_m2", label: "Ѕидна површина", unit: "m2" },
  { key: "ceiling_area_m2", label: "Таванска површина", unit: "m2" },
  { key: "total_paintable_area_m2", label: "Вкупна површина за бојадисување", unit: "m2" },
  { key: "coats", label: "Слоеви боја" },
  { key: "primer_coats", label: "Прајмер слоеви" },
  { key: "waste_percentage", label: "Отпад", unit: "percent" },
  { key: "paint_required_liters", label: "Потребна боја", unit: "liter" },
  { key: "primer_required_liters", label: "Потребен прајмер", unit: "liter" },
  { key: "paint_material_cost", label: "Трошок за боја", unit: "money" },
  { key: "primer_material_cost", label: "Трошок за прајмер", unit: "money" },
  { key: "labor_cost", label: "Трошок за работа", unit: "money" },
  { key: "total_cost", label: "Вкупен трошок", unit: "money" },
];

function toNullable(value: string): string | null {
  const trimmedValue = value.trim();
  return trimmedValue === "" ? null : trimmedValue;
}

function toOptionalNumber(value: string): number | null {
  const trimmedValue = value.trim();
  return trimmedValue === "" ? null : Number(trimmedValue);
}

function formatNumber(value: number): string {
  return value.toFixed(4).replace(/\.?0+$/, "");
}

function formatQuantity(value: number | null, unit: string | null): string {
  if (value === null) {
    return "Не е вратено";
  }

  return [formatNumber(value), formatUnit(unit)].filter(Boolean).join(" ");
}

function formatEngine(engineType: string): string {
  return engineLabels[engineType] ?? engineType;
}

function formatCalculationStatus(status: string): string {
  return calculationStatusLabels[status] ?? status;
}

function formatOutputValue(value: unknown, unit?: "liter" | "money" | "percent" | "m2"): string {
  if (value === null || value === undefined || value === "") {
    return "Не е вратено";
  }

  if (typeof value === "number") {
    const formatted = formatNumber(value);

    if (unit === "m2") {
      return `${formatted} m²`;
    }

    if (unit === "liter") {
      return `${formatted} l`;
    }

    if (unit === "money") {
      return `${formatted} MKD`;
    }

    if (unit === "percent") {
      return `${formatted}%`;
    }

    return formatted;
  }

  if (typeof value === "boolean") {
    return value ? "Да" : "Не";
  }

  return String(value);
}

function localizedErrorMessage(error: unknown, fallback: string): string {
  if (error instanceof Error && /[А-џ]/.test(error.message)) {
    return error.message;
  }

  return fallback;
}

function materialName(materials: MaterialResponse[], materialId: unknown): string {
  if (typeof materialId !== "string") {
    return "Не е избран";
  }

  return materials.find((material) => material.id === materialId)?.name ?? materialId;
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

function paintingPayloadFromForm(form: PaintingFormState): CalculationRunCreateRequest {
  return {
    engine_type: "painting",
    project_id: toNullable(form.project_id),
    project_task_id: toNullable(form.project_task_id),
    room_id: toNullable(form.room_id),
    measurement_set_id: toNullable(form.measurement_set_id),
    input_payload: {
      include_walls: form.include_walls,
      include_ceiling: form.include_ceiling,
      coats: Number(form.coats),
      primer_coats: Number(form.primer_coats),
      paint_material_id: toNullable(form.paint_material_id),
      primer_material_id: toNullable(form.primer_material_id),
      waste_percentage: toOptionalNumber(form.waste_percentage),
      labor_rate_per_m2: toOptionalNumber(form.labor_rate_per_m2),
      notes: toNullable(form.notes),
    },
  };
}

function Panel({ children, title }: { children: ReactNode; title: string }) {
  return (
    <section className="ui-card">
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

function CheckboxField({
  checked,
  label,
  name,
  onChange,
}: {
  checked: boolean;
  label: string;
  name: string;
  onChange: (event: ChangeEvent<HTMLInputElement>) => void;
}) {
  return (
    <label htmlFor={name} className="flex min-h-10 items-center gap-2 text-sm font-semibold text-slate-700">
      <input
        id={name}
        name={name}
        type="checkbox"
        checked={checked}
        onChange={onChange}
        className="h-4 w-4 rounded border-line text-brand focus:ring-brand"
      />
      {label}
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

function Message({ children, tone = "neutral" }: { children: ReactNode; tone?: MessageTone }) {
  const toneClass =
    tone === "error"
      ? "border-red-200 bg-red-50 text-red-800"
      : tone === "success"
        ? "border-emerald-200 bg-emerald-50 text-emerald-800"
        : "border-line bg-slate-50 text-slate-700";

  return <p className={`ui-message ${toneClass}`}>{children}</p>;
}

function PrimaryButton({ children, disabled = false }: { children: ReactNode; disabled?: boolean }) {
  return (
    <button
      type="submit"
      disabled={disabled}
      className="ui-button-primary"
    >
      <Play aria-hidden="true" className="h-4 w-4" />
      {children}
    </button>
  );
}

function EmptyState({ children }: { children: ReactNode }) {
  return <p className="ui-empty-inline">{children}</p>;
}

function StatusBadge({ status }: { status: string }) {
  const statusClass =
    status === "failed"
      ? "border-red-200 bg-red-50 text-red-800"
      : status === "completed"
        ? "border-emerald-200 bg-emerald-50 text-emerald-800"
        : "border-line bg-slate-50 text-slate-700";

  return (
    <span className={`ui-status-badge ${statusClass}`}>
      {formatCalculationStatus(status)}
    </span>
  );
}

function OutputTile({ label, value }: { label: string; value: string }) {
  return (
    <div className="ui-data-tile">
      <p className="text-xs font-semibold uppercase text-slate-500">{label}</p>
      <p className="mt-1 text-lg font-bold tracking-normal text-ink">{value}</p>
    </div>
  );
}

function ListSection({ children, title }: { children: ReactNode; title: string }) {
  return (
    <div>
      <h3 className="text-sm font-bold text-ink">{title}</h3>
      <div className="mt-3">{children}</div>
    </div>
  );
}

export function CalculationsPage() {
  const queryClient = useQueryClient();
  const [selectedCalculationId, setSelectedCalculationId] = useState<string | null>(null);
  const [paintingForm, setPaintingForm] = useState<PaintingFormState>(emptyPaintingForm);
  const [pageMessage, setPageMessage] = useState<PageMessage | null>(null);

  const projectsQuery = useQuery({
    queryKey: ["projects"],
    queryFn: listProjects,
  });

  const materialsQuery = useQuery({
    queryKey: ["materials"],
    queryFn: listMaterials,
  });

  const enginesQuery = useQuery({
    queryKey: ["calculation-engines"],
    queryFn: listCalculationEngines,
  });

  const calculationsQuery = useQuery({
    queryKey: ["calculations"],
    queryFn: listCalculations,
  });

  const tasksQuery = useQuery({
    queryKey: ["project-tasks", paintingForm.project_id],
    queryFn: () => listProjectTasks(paintingForm.project_id),
    enabled: Boolean(paintingForm.project_id),
  });

  const roomsQuery = useQuery({
    queryKey: ["project-rooms", paintingForm.project_id],
    queryFn: () => listProjectRooms(paintingForm.project_id),
    enabled: Boolean(paintingForm.project_id),
  });

  const measurementSetsQuery = useQuery({
    queryKey: ["measurement-sets", paintingForm.project_id],
    queryFn: () => listMeasurementSets(paintingForm.project_id),
    enabled: Boolean(paintingForm.project_id),
  });

  const selectedCalculationListItem = useMemo(() => {
    return (calculationsQuery.data ?? []).find((calculation) => calculation.id === selectedCalculationId) ?? null;
  }, [calculationsQuery.data, selectedCalculationId]);

  const selectedCalculationQuery = useQuery({
    queryKey: ["calculations", selectedCalculationId],
    queryFn: () => getCalculation(selectedCalculationId ?? ""),
    enabled: Boolean(selectedCalculationId),
  });

  const selectedCalculation = selectedCalculationQuery.data ?? selectedCalculationListItem;
  const projects = projectsQuery.data ?? [];
  const tasks = tasksQuery.data ?? [];
  const rooms = roomsQuery.data ?? [];
  const measurementSets = measurementSetsQuery.data ?? [];
  const materials = materialsQuery.data ?? [];

  useEffect(() => {
    if (!selectedCalculationId && calculationsQuery.data && calculationsQuery.data.length > 0) {
      setSelectedCalculationId(calculationsQuery.data[0].id);
    }
  }, [calculationsQuery.data, selectedCalculationId]);

  useEffect(() => {
    if (!paintingForm.project_id && projectsQuery.data && projectsQuery.data.length > 0) {
      setPaintingForm((current) => ({ ...current, project_id: projectsQuery.data[0].id }));
    }
  }, [paintingForm.project_id, projectsQuery.data]);

  const runPaintingMutation = useMutation({
    mutationFn: runCalculation,
    onSuccess: (calculation) => {
      setPageMessage({ text: "Пресметката е стартувана.", tone: "success" });
      setSelectedCalculationId(calculation.id);
      void queryClient.invalidateQueries({ queryKey: ["calculations"] });
      queryClient.setQueryData(["calculations", calculation.id], calculation);
    },
    onError: (error) => {
      const message = localizedErrorMessage(error, "Пресметката не беше стартувана. Проверете ги внесените податоци.");
      setPageMessage({ text: message, tone: "error" });
    },
  });

  const createEstimateMutation = useMutation({
    mutationFn: (calculationRunId: string) =>
      createEstimateFromCalculation(calculationRunId, {
        title: null,
        description: null,
      }),
    onSuccess: () => {
      setPageMessage({ text: "Понудата е креирана.", tone: "success" });
      void queryClient.invalidateQueries({ queryKey: ["estimates"] });
    },
    onError: (error) => {
      const message = localizedErrorMessage(error, "Понудата не беше креирана од пресметката.");
      setPageMessage({ text: message, tone: "error" });
    },
  });

  function handleFormField(field: keyof PaintingFormState) {
    return (event: ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
      const value = event.target.value;
      setPaintingForm((current) => {
        const next = { ...current, [field]: value };

        if (field === "project_id") {
          next.project_task_id = "";
          next.room_id = "";
          next.measurement_set_id = "";
        }

        return next;
      });
    };
  }

  function handleCheckboxField(field: "include_ceiling" | "include_walls") {
    return (event: ChangeEvent<HTMLInputElement>) =>
      setPaintingForm((current) => ({ ...current, [field]: event.target.checked }));
  }

  function handleRunPainting(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const payload = paintingPayloadFromForm(paintingForm);

    if (!payload.project_id) {
      setPageMessage({ text: "Изберете проект за пресметката.", tone: "error" });
      return;
    }

    if (!paintingForm.include_walls && !paintingForm.include_ceiling) {
      setPageMessage({ text: "Изберете ѕидови или таван за пресметката.", tone: "error" });
      return;
    }

    if (Number(paintingForm.coats) < 1 || Number.isNaN(Number(paintingForm.coats))) {
      setPageMessage({ text: "Слоевите боја мора да бидат најмалку 1.", tone: "error" });
      return;
    }

    if (Number(paintingForm.primer_coats) < 0 || Number.isNaN(Number(paintingForm.primer_coats))) {
      setPageMessage({ text: "Прајмер слоевите не може да бидат негативни.", tone: "error" });
      return;
    }

    runPaintingMutation.mutate(payload);
  }

  const projectLabel = (projectId: string | null) =>
    selectLabel<ProjectResponse>(projects, projectId, (project) => project.name, "Без проект");
  const taskLabel = (taskId: string | null) =>
    selectLabel<ProjectTaskResponse>(tasks, taskId, (task) => task.title, "Без задача");
  const roomLabel = (roomId: string | null) => selectLabel<RoomResponse>(rooms, roomId, (room) => room.name, "Без просторија");
  const measurementSetLabel = (measurementSetId: string | null) =>
    selectLabel<MeasurementSetResponse>(measurementSets, measurementSetId, (measurementSet) => measurementSet.name, "Без сет");

  return (
    <section className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-normal text-ink">Пресметки</h1>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
          Стартувајте пресметка за бојадисување преку серверот и прегледајте ги зачуваните резултати.
        </p>
      </div>

      {pageMessage ? <Message tone={pageMessage.tone}>{pageMessage.text}</Message> : null}

      <div className="grid gap-6 xl:grid-cols-[380px_minmax(0,1fr)]">
        <aside className="space-y-4">
          <Panel title="Бојадисување">
            <form onSubmit={handleRunPainting} className="space-y-4">
              <SelectField
                label="Проект за пресметка"
                name="calculation-project-id"
                value={paintingForm.project_id}
                required
                onChange={handleFormField("project_id")}
              >
                <option value="">Изберете проект</option>
                {projects.map((project) => (
                  <option key={project.id} value={project.id}>
                    {project.name}
                  </option>
                ))}
              </SelectField>

              <SelectField
                label="Задача (незадолжително)"
                name="calculation-task-id"
                value={paintingForm.project_task_id}
                onChange={handleFormField("project_task_id")}
              >
                <option value="">Без задача</option>
                {tasks.map((task) => (
                  <option key={task.id} value={task.id}>
                    Задача: {task.title}
                  </option>
                ))}
              </SelectField>

              <SelectField
                label="Просторија (незадолжително)"
                name="calculation-room-id"
                value={paintingForm.room_id}
                onChange={handleFormField("room_id")}
              >
                <option value="">Без просторија</option>
                {rooms.map((room) => (
                  <option key={room.id} value={room.id}>
                    Просторија: {room.name}
                  </option>
                ))}
              </SelectField>

              <SelectField
                label="Сет мерења (незадолжително)"
                name="calculation-measurement-set-id"
                value={paintingForm.measurement_set_id}
                onChange={handleFormField("measurement_set_id")}
              >
                <option value="">Без сет мерења</option>
                {measurementSets.map((measurementSet) => (
                  <option key={measurementSet.id} value={measurementSet.id}>
                    Сет: {measurementSet.name}
                  </option>
                ))}
              </SelectField>

              <div className="grid gap-2 sm:grid-cols-2">
                <CheckboxField
                  label="Вклучи ѕидови"
                  name="calculation-include-walls"
                  checked={paintingForm.include_walls}
                  onChange={handleCheckboxField("include_walls")}
                />
                <CheckboxField
                  label="Вклучи таван"
                  name="calculation-include-ceiling"
                  checked={paintingForm.include_ceiling}
                  onChange={handleCheckboxField("include_ceiling")}
                />
              </div>

              <div className="grid gap-3 sm:grid-cols-2">
                <FormField
                  label="Слоеви боја"
                  name="calculation-coats"
                  type="number"
                  value={paintingForm.coats}
                  required
                  onChange={handleFormField("coats")}
                />
                <FormField
                  label="Прајмер слоеви"
                  name="calculation-primer-coats"
                  type="number"
                  value={paintingForm.primer_coats}
                  required
                  onChange={handleFormField("primer_coats")}
                />
              </div>

              <SelectField
                label="Материјал за боја"
                name="calculation-paint-material"
                value={paintingForm.paint_material_id}
                onChange={handleFormField("paint_material_id")}
              >
                <option value="">Без материјал</option>
                {materials.map((material) => (
                  <option key={material.id} value={material.id}>
                    {material.name}
                  </option>
                ))}
              </SelectField>

              <SelectField
                label="Прајмер материјал"
                name="calculation-primer-material"
                value={paintingForm.primer_material_id}
                onChange={handleFormField("primer_material_id")}
              >
                <option value="">Без прајмер</option>
                {materials.map((material) => (
                  <option key={material.id} value={material.id}>
                    {material.name}
                  </option>
                ))}
              </SelectField>

              <div className="grid gap-3 sm:grid-cols-2">
                <FormField
                  label="Отпад (%)"
                  name="calculation-waste"
                  type="number"
                  value={paintingForm.waste_percentage}
                  onChange={handleFormField("waste_percentage")}
                />
                <FormField
                  label="Работна цена по m²"
                  name="calculation-labor-rate"
                  type="number"
                  value={paintingForm.labor_rate_per_m2}
                  onChange={handleFormField("labor_rate_per_m2")}
                />
              </div>

              <TextAreaField label="Белешки" name="calculation-notes" value={paintingForm.notes} onChange={handleFormField("notes")} />

              <PrimaryButton disabled={runPaintingMutation.isPending}>Стартувај пресметка</PrimaryButton>
            </form>
          </Panel>

          <Panel title="Мотори">
            {enginesQuery.isLoading ? <Message>Се вчитуваат моторите за пресметки.</Message> : null}
            {enginesQuery.isError ? <Message tone="error">Моторите не може да се вчитаат.</Message> : null}
            <div className="space-y-2">
              {(enginesQuery.data ?? []).map((engine) => (
                <div key={engine.engine_type} className="ui-data-tile">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-sm font-bold text-ink">{formatEngine(engine.engine_type)}</p>
                      <p className="mt-1 text-xs text-slate-500">{engine.engine_version}</p>
                    </div>
                    <span className="rounded-md border border-line bg-white px-2 py-1 text-xs font-bold text-slate-700">
                      {engine.implemented ? "Имплементирано" : "Во подготовка"}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </Panel>
        </aside>

        <div className="space-y-6">
          <Panel title="Историја на пресметки">
            {calculationsQuery.isLoading ? <Message>Се вчитуваат пресметките.</Message> : null}
            {calculationsQuery.isError ? <Message tone="error">Пресметките не може да се вчитаат.</Message> : null}
            {!calculationsQuery.isLoading && (calculationsQuery.data ?? []).length === 0 ? (
              <EmptyState>Нема зачувани пресметки.</EmptyState>
            ) : null}
            <div className="grid gap-3 lg:grid-cols-2">
              {(calculationsQuery.data ?? []).map((calculation) => (
                <button
                  key={calculation.id}
                  type="button"
                  onClick={() => setSelectedCalculationId(calculation.id)}
                  className={[
                    "rounded-md border px-3 py-3 text-left transition",
                    selectedCalculationId === calculation.id
                      ? "border-brand bg-brand/10"
                      : "border-line bg-white hover:border-brand",
                  ].join(" ")}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-sm font-bold text-ink">{formatEngine(calculation.engine_type)}</p>
                      <p className="mt-1 text-xs text-slate-500">
                        {projectLabel(calculation.project_id)} - {roomLabel(calculation.room_id)}
                      </p>
                      <p className="mt-1 text-xs text-slate-500">{formatDate(calculation.created_at)}</p>
                    </div>
                    <StatusBadge status={calculation.status} />
                  </div>
                </button>
              ))}
            </div>
          </Panel>

          <Panel title="Детали за пресметка">
            {selectedCalculation ? (
              <CalculationDetail
                calculation={selectedCalculation}
                materials={materials}
                measurementSetLabel={measurementSetLabel}
                onCreateEstimate={(calculationRunId) => createEstimateMutation.mutate(calculationRunId)}
                projectLabel={projectLabel}
                roomLabel={roomLabel}
                taskLabel={taskLabel}
              />
            ) : (
              <EmptyState>Изберете пресметка за да ги видите деталите.</EmptyState>
            )}
          </Panel>
        </div>
      </div>
    </section>
  );
}

function CalculationDetail({
  calculation,
  materials,
  measurementSetLabel,
  onCreateEstimate,
  projectLabel,
  roomLabel,
  taskLabel,
}: {
  calculation: CalculationRunResponse;
  materials: MaterialResponse[];
  measurementSetLabel: (measurementSetId: string | null) => string;
  onCreateEstimate: (calculationRunId: string) => void;
  projectLabel: (projectId: string | null) => string;
  roomLabel: (roomId: string | null) => string;
  taskLabel: (taskId: string | null) => string;
}) {
  const outputPayload = calculation.output_payload ?? {};
  const inputPayload = calculation.input_payload ?? {};
  const assumptions = Array.isArray(outputPayload.assumptions) ? outputPayload.assumptions : [];
  const warnings = Array.isArray(outputPayload.warnings) ? outputPayload.warnings : [];

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-xl font-bold tracking-normal text-ink">{formatEngine(calculation.engine_type)}</p>
          <p className="mt-1 text-sm text-slate-600">
            {projectLabel(calculation.project_id)} - {roomLabel(calculation.room_id)}
          </p>
        </div>
        <div className="flex flex-wrap items-center justify-end gap-2">
          {calculation.status === "completed" ? (
            <button
              type="button"
              onClick={() => onCreateEstimate(calculation.id)}
              className="ui-button-secondary"
            >
              <FileText aria-hidden="true" className="h-4 w-4" />
              Креирај понуда
            </button>
          ) : null}
          <StatusBadge status={calculation.status} />
        </div>
      </div>

      <dl className="grid gap-4 rounded-md border border-line bg-slate-50 p-3 sm:grid-cols-2 xl:grid-cols-4">
        <div>
          <dt className="text-xs font-semibold uppercase text-slate-500">Проект</dt>
          <dd className="mt-1 text-sm text-slate-800">{projectLabel(calculation.project_id)}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-slate-500">Задача</dt>
          <dd className="mt-1 text-sm text-slate-800">{taskLabel(calculation.project_task_id)}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-slate-500">Просторија</dt>
          <dd className="mt-1 text-sm text-slate-800">{roomLabel(calculation.room_id)}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase text-slate-500">Сет мерења</dt>
          <dd className="mt-1 text-sm text-slate-800">{measurementSetLabel(calculation.measurement_set_id)}</dd>
        </div>
      </dl>

      <ListSection title="Влезни податоци">
        <dl className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <OutputTile label="Вклучени ѕидови" value={formatOutputValue(inputPayload.include_walls)} />
          <OutputTile label="Вклучен таван" value={formatOutputValue(inputPayload.include_ceiling)} />
          <OutputTile label="Слоеви боја" value={formatOutputValue(inputPayload.coats)} />
          <OutputTile label="Прајмер слоеви" value={formatOutputValue(inputPayload.primer_coats)} />
          <OutputTile label="Материјал за боја" value={materialName(materials, inputPayload.paint_material_id)} />
          <OutputTile label="Прајмер материјал" value={materialName(materials, inputPayload.primer_material_id)} />
          <OutputTile label="Отпад" value={formatOutputValue(inputPayload.waste_percentage, "percent")} />
          <OutputTile label="Работна цена" value={formatOutputValue(inputPayload.labor_rate_per_m2, "money")} />
        </dl>
      </ListSection>

      {calculation.status === "failed" ? (
        <Message tone="error">{formatOutputValue(outputPayload.message)}</Message>
      ) : (
        <ListSection title="Резултат">
          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            {outputLabels.map((item) => (
              <OutputTile
                key={item.key}
                label={item.label}
                value={formatOutputValue(outputPayload[item.key], item.unit)}
              />
            ))}
          </div>
        </ListSection>
      )}

      <div className="grid gap-4 xl:grid-cols-2">
        <ListSection title="Претпоставки">
          {assumptions.length > 0 ? (
            <ul className="space-y-2">
              {assumptions.map((assumption) => (
                <li key={String(assumption)} className="rounded-md border border-line bg-slate-50 px-3 py-2 text-sm text-slate-700">
                  {String(assumption)}
                </li>
              ))}
            </ul>
          ) : (
            <EmptyState>Нема претпоставки од серверот.</EmptyState>
          )}
        </ListSection>

        <ListSection title="Предупредувања">
          {warnings.length > 0 ? (
            <ul className="space-y-2">
              {warnings.map((warning) => (
                <li key={String(warning)} className="rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-900">
                  {String(warning)}
                </li>
              ))}
            </ul>
          ) : (
            <EmptyState>Нема предупредувања.</EmptyState>
          )}
        </ListSection>
      </div>

      <ListSection title="Ставки">
        {calculation.line_items.length > 0 ? (
          <div className="overflow-x-auto rounded-md border border-line">
            <table className="min-w-full divide-y divide-line text-sm">
              <thead className="bg-slate-50 text-left text-xs uppercase text-slate-500">
                <tr>
                  <th className="px-3 py-2">Име</th>
                  <th className="px-3 py-2">Опис</th>
                  <th className="px-3 py-2">Количина</th>
                  <th className="px-3 py-2">Трошок</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line bg-white">
                {calculation.line_items.map((item) => (
                  <tr key={item.id}>
                    <td className="px-3 py-2 font-semibold text-ink">{item.name}</td>
                    <td className="px-3 py-2 text-slate-700">{item.description ?? "Не е внесено"}</td>
                    <td className="px-3 py-2 text-slate-700">{formatQuantity(item.quantity, item.unit)}</td>
                    <td className="px-3 py-2 text-slate-700">{formatOutputValue(item.payload?.total_cost, "money")}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <EmptyState>Нема ставки за оваа пресметка.</EmptyState>
        )}
      </ListSection>
    </div>
  );
}
