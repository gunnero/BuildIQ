import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Archive, CheckCircle2, Plus, Save } from "lucide-react";
import { useEffect, useMemo, useState, type ChangeEvent, type FormEvent, type ReactNode } from "react";

import { listCustomers } from "../api/customers";
import {
  archiveMeasurementItem,
  createMeasurementItem,
  createMeasurementSet,
  getMeasurementSet,
  listMeasurementItems,
  listMeasurementSets,
  updateMeasurementItem,
} from "../api/measurements";
import {
  archiveProject,
  archiveProjectTask,
  changeProjectStatus,
  changeProjectTaskStatus,
  createProject,
  createProjectTask,
  getProject,
  listProjectStatusHistory,
  listProjectTasks,
  listProjectTimeline,
  listProjects,
  updateProject,
  updateProjectTask,
} from "../api/projects";
import { listProperties } from "../api/properties";
import {
  archiveRoom,
  archiveRoomOpening,
  createRoom,
  createRoomOpening,
  getRoom,
  listProjectRooms,
  listRoomOpenings,
  updateRoom,
  updateRoomOpening,
} from "../api/rooms";
import type {
  MeasurementItemCreateRequest,
  MeasurementItemResponse,
  MeasurementItemUpdateRequest,
  MeasurementSetCreateRequest,
  MeasurementSetResponse,
  ProjectCreateRequest,
  ProjectResponse,
  ProjectTaskCreateRequest,
  ProjectTaskResponse,
  ProjectUpdateRequest,
  RoomCreateRequest,
  RoomOpeningCreateRequest,
  RoomOpeningResponse,
  RoomOpeningUpdateRequest,
  RoomResponse,
  RoomUpdateRequest,
} from "../api/types";

type ProjectFormState = {
  customer_id: string;
  property_id: string;
  name: string;
  description: string;
  address: string;
  agreed_project_price: string;
  start_date: string;
  due_date: string;
};

type ProjectEditFormState = Omit<ProjectFormState, "customer_id" | "property_id">;

type ProjectStatusFormState = {
  status: string;
  note: string;
};

type TaskFormState = {
  title: string;
  description: string;
  assigned_user_id: string;
  due_date: string;
};

type TaskStatusFormState = {
  status: string;
};

type RoomFormState = {
  name: string;
  room_type: string;
  project_task_id: string;
  floor: string;
  note: string;
  length: string;
  width: string;
  height: string;
};

type OpeningFormState = {
  opening_type: string;
  name: string;
  width: string;
  height: string;
  quantity: string;
  note: string;
};

type MeasurementSetFormState = {
  name: string;
  description: string;
  project_task_id: string;
};

type MeasurementItemFormState = {
  name: string;
  unit: string;
  quantity: string;
  note: string;
};

type MessageTone = "neutral" | "error" | "success";

type PageMessage = {
  text: string;
  tone: MessageTone;
};

const emptyProjectForm: ProjectFormState = {
  customer_id: "",
  property_id: "",
  name: "",
  description: "",
  address: "",
  agreed_project_price: "",
  start_date: "",
  due_date: "",
};

const emptyProjectEditForm: ProjectEditFormState = {
  name: "",
  description: "",
  address: "",
  agreed_project_price: "",
  start_date: "",
  due_date: "",
};

const emptyProjectStatusForm: ProjectStatusFormState = {
  status: "draft",
  note: "",
};

const emptyTaskForm: TaskFormState = {
  title: "",
  description: "",
  assigned_user_id: "",
  due_date: "",
};

const emptyTaskStatusForm: TaskStatusFormState = {
  status: "pending",
};

const emptyRoomForm: RoomFormState = {
  name: "",
  room_type: "room",
  project_task_id: "",
  floor: "",
  note: "",
  length: "",
  width: "",
  height: "",
};

const emptyOpeningForm: OpeningFormState = {
  opening_type: "door",
  name: "",
  width: "",
  height: "",
  quantity: "1",
  note: "",
};

const emptyMeasurementSetForm: MeasurementSetFormState = {
  name: "",
  description: "",
  project_task_id: "",
};

const emptyMeasurementItemForm: MeasurementItemFormState = {
  name: "",
  unit: "m",
  quantity: "",
  note: "",
};

const projectStatuses = [
  { value: "draft", label: "Нацрт" },
  { value: "planned", label: "Планиран" },
  { value: "active", label: "Активен" },
  { value: "paused", label: "Паузиран" },
  { value: "completed", label: "Завршен" },
  { value: "archived", label: "Архивиран" },
  { value: "cancelled", label: "Откажан" },
];

const taskStatuses = [
  { value: "draft", label: "Нацрт" },
  { value: "pending", label: "Чека" },
  { value: "active", label: "Активна" },
  { value: "completed", label: "Завршена" },
  { value: "cancelled", label: "Откажана" },
  { value: "archived", label: "Архивирана" },
];

const roomTypes = [
  { value: "room", label: "Просторија" },
  { value: "bathroom", label: "Бања" },
  { value: "kitchen", label: "Кујна" },
  { value: "hallway", label: "Ходник" },
  { value: "bedroom", label: "Спална соба" },
  { value: "living_room", label: "Дневна соба" },
  { value: "exterior", label: "Надворешно" },
  { value: "other", label: "Друго" },
];

const openingTypes = [
  { value: "door", label: "Врата" },
  { value: "window", label: "Прозорец" },
  { value: "other", label: "Друго" },
];

const measurementUnits = [
  { value: "m", label: "m" },
  { value: "m2", label: "m²" },
  { value: "m3", label: "m³" },
  { value: "piece", label: "парче" },
  { value: "kg", label: "kg" },
  { value: "liter", label: "литар" },
  { value: "bag", label: "вреќа" },
  { value: "roll", label: "ролна" },
  { value: "hour", label: "час" },
];

function toNullable(value: string): string | null {
  const trimmedValue = value.trim();
  return trimmedValue === "" ? null : trimmedValue;
}

function toNullableNumber(value: string): number | null {
  const trimmedValue = value.trim();
  return trimmedValue === "" ? null : Number(trimmedValue);
}

function toRequiredNumber(value: string): number {
  return Number(value.trim());
}

function displayValue(value: string | number | null | undefined): string {
  if (typeof value === "number") {
    return formatNumber(value);
  }

  return value?.toString().trim() ? value.toString() : "Не е внесено";
}

function formatNumber(value: number, minimumFractionDigits = 0): string {
  return value.toFixed(2).replace(/\.?0+$/, minimumFractionDigits > 0 && Number.isInteger(value) ? ".0" : "");
}

function formatSquareMeters(value: number, minimumFractionDigits = 0): string {
  return `${formatNumber(value, minimumFractionDigits)} m²`;
}

function formatMeasurementUnit(unit: string): string {
  return measurementUnits.find((item) => item.value === unit)?.label ?? unit;
}

function formatProjectStatus(status: string): string {
  return projectStatuses.find((item) => item.value === status)?.label ?? status;
}

function formatTaskStatus(status: string): string {
  return taskStatuses.find((item) => item.value === status)?.label ?? status;
}

function formatRoomType(roomType: string): string {
  return roomTypes.find((item) => item.value === roomType)?.label ?? roomType;
}

function formatOpeningType(openingType: string): string {
  return openingTypes.find((item) => item.value === openingType)?.label ?? openingType;
}

function formatDate(value: string | null | undefined): string {
  if (!value) {
    return "Не е внесено";
  }

  return new Intl.DateTimeFormat("mk-MK", { dateStyle: "medium" }).format(new Date(value));
}

function projectPayloadFromForm(form: ProjectFormState): ProjectCreateRequest {
  return {
    customer_id: form.customer_id,
    property_id: form.property_id,
    name: form.name.trim(),
    description: toNullable(form.description),
    address: toNullable(form.address),
    agreed_project_price: toNullableNumber(form.agreed_project_price),
    start_date: toNullable(form.start_date),
    due_date: toNullable(form.due_date),
  };
}

function projectUpdatePayloadFromForm(form: ProjectEditFormState): ProjectUpdateRequest {
  return {
    name: form.name.trim(),
    description: toNullable(form.description),
    address: toNullable(form.address),
    agreed_project_price: toNullableNumber(form.agreed_project_price),
    start_date: toNullable(form.start_date),
    due_date: toNullable(form.due_date),
  };
}

function projectEditFormFromEntity(project: ProjectResponse): ProjectEditFormState {
  return {
    name: project.name,
    description: project.description ?? "",
    address: project.address ?? "",
    agreed_project_price: project.agreed_project_price?.toString() ?? "",
    start_date: project.start_date ?? "",
    due_date: project.due_date ?? "",
  };
}

function taskPayloadFromForm(form: TaskFormState): ProjectTaskCreateRequest {
  return {
    title: form.title.trim(),
    description: toNullable(form.description),
    assigned_user_id: toNullable(form.assigned_user_id),
    due_date: toNullable(form.due_date),
  };
}

function taskFormFromEntity(task: ProjectTaskResponse): TaskFormState {
  return {
    title: task.title,
    description: task.description ?? "",
    assigned_user_id: task.assigned_user_id ?? "",
    due_date: task.due_date ?? "",
  };
}

function roomPayloadFromForm(form: RoomFormState): RoomCreateRequest {
  return {
    name: form.name.trim(),
    room_type: form.room_type,
    project_task_id: toNullable(form.project_task_id),
    floor: toNullable(form.floor),
    note: toNullable(form.note),
    length: toRequiredNumber(form.length),
    width: toRequiredNumber(form.width),
    height: toRequiredNumber(form.height),
  };
}

function roomFormFromEntity(room: RoomResponse): RoomFormState {
  return {
    name: room.name,
    room_type: room.room_type,
    project_task_id: room.project_task_id ?? "",
    floor: room.floor ?? "",
    note: room.note ?? "",
    length: room.length.toString(),
    width: room.width.toString(),
    height: room.height.toString(),
  };
}

function openingPayloadFromForm(form: OpeningFormState): RoomOpeningCreateRequest {
  return {
    opening_type: form.opening_type,
    name: form.name.trim(),
    width: toRequiredNumber(form.width),
    height: toRequiredNumber(form.height),
    quantity: toRequiredNumber(form.quantity),
    note: toNullable(form.note),
  };
}

function openingFormFromEntity(opening: RoomOpeningResponse): OpeningFormState {
  return {
    opening_type: opening.opening_type,
    name: opening.name,
    width: opening.width.toString(),
    height: opening.height.toString(),
    quantity: opening.quantity.toString(),
    note: opening.note ?? "",
  };
}

function measurementSetPayloadFromForm(form: MeasurementSetFormState): MeasurementSetCreateRequest {
  return {
    name: form.name.trim(),
    description: toNullable(form.description),
    project_task_id: toNullable(form.project_task_id),
  };
}

function measurementSetFormFromEntity(measurementSet: MeasurementSetResponse): MeasurementSetFormState {
  return {
    name: measurementSet.name,
    description: measurementSet.description ?? "",
    project_task_id: measurementSet.project_task_id ?? "",
  };
}

function measurementItemPayloadFromForm(form: MeasurementItemFormState): MeasurementItemCreateRequest {
  return {
    name: form.name.trim(),
    unit: form.unit,
    quantity: toRequiredNumber(form.quantity),
    note: toNullable(form.note),
  };
}

function measurementItemFormFromEntity(item: MeasurementItemResponse): MeasurementItemFormState {
  return {
    name: item.name,
    unit: item.unit,
    quantity: item.quantity.toString(),
    note: item.note ?? "",
  };
}

function hasPositiveNumbers(values: string[]): boolean {
  return values.every((value) => Number(value) > 0);
}

function Panel({ children, title }: { children: ReactNode; title: string }) {
  return (
    <section className="rounded-md border border-line bg-white p-4 shadow-sm">
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

function NumberField({
  label,
  name,
  onChange,
  required = false,
  value,
}: {
  label: string;
  name: string;
  onChange: (event: ChangeEvent<HTMLInputElement>) => void;
  required?: boolean;
  value: string;
}) {
  return (
    <FormField label={label} name={name} type="number" value={value} required={required} onChange={onChange} />
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

function SecondaryButton({
  children,
  disabled = false,
  icon = "save",
  onClick,
  type = "button",
}: {
  children: ReactNode;
  disabled?: boolean;
  icon?: "archive" | "check" | "save";
  onClick?: () => void;
  type?: "button" | "submit";
}) {
  const Icon = icon === "archive" ? Archive : icon === "check" ? CheckCircle2 : Save;

  return (
    <button
      type={type}
      disabled={disabled}
      onClick={onClick}
      className="inline-flex h-10 items-center justify-center gap-2 rounded-md border border-line bg-white px-3 text-sm font-semibold text-slate-700 transition hover:border-brand hover:text-brand focus:outline-none focus:ring-2 focus:ring-brand focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60"
    >
      <Icon aria-hidden="true" className="h-4 w-4" />
      {children}
    </button>
  );
}

function DetailRow({ label, value }: { label: string; value: string | number | null | undefined }) {
  return (
    <div>
      <dt className="text-xs font-semibold uppercase text-slate-500">{label}</dt>
      <dd className="mt-1 text-sm text-slate-800">{displayValue(value)}</dd>
    </div>
  );
}

function StatusBadge({ children }: { children: ReactNode }) {
  return (
    <span className="inline-flex items-center rounded-md border border-brand/20 bg-brand/10 px-2 py-1 text-xs font-bold text-brand">
      {children}
    </span>
  );
}

function EmptyState({ children }: { children: ReactNode }) {
  return <p className="rounded-md border border-dashed border-line bg-slate-50 px-3 py-4 text-sm text-slate-600">{children}</p>;
}

function AreaTile({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-line bg-slate-50 px-3 py-3">
      <p className="text-xs font-semibold uppercase text-slate-500">{label}</p>
      <p className="mt-1 text-lg font-bold tracking-normal text-ink">{value}</p>
    </div>
  );
}

export function ProjectsPage() {
  const queryClient = useQueryClient();
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);
  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(null);
  const [selectedRoomId, setSelectedRoomId] = useState<string | null>(null);
  const [selectedOpeningId, setSelectedOpeningId] = useState<string | null>(null);
  const [selectedMeasurementSetId, setSelectedMeasurementSetId] = useState<string | null>(null);
  const [selectedMeasurementItemId, setSelectedMeasurementItemId] = useState<string | null>(null);
  const [projectForm, setProjectForm] = useState<ProjectFormState>(emptyProjectForm);
  const [projectEditForm, setProjectEditForm] = useState<ProjectEditFormState>(emptyProjectEditForm);
  const [projectStatusForm, setProjectStatusForm] = useState<ProjectStatusFormState>(emptyProjectStatusForm);
  const [taskForm, setTaskForm] = useState<TaskFormState>(emptyTaskForm);
  const [taskEditForm, setTaskEditForm] = useState<TaskFormState>(emptyTaskForm);
  const [taskStatusForm, setTaskStatusForm] = useState<TaskStatusFormState>(emptyTaskStatusForm);
  const [roomForm, setRoomForm] = useState<RoomFormState>(emptyRoomForm);
  const [roomEditForm, setRoomEditForm] = useState<RoomFormState>(emptyRoomForm);
  const [openingForm, setOpeningForm] = useState<OpeningFormState>(emptyOpeningForm);
  const [openingEditForm, setOpeningEditForm] = useState<OpeningFormState>(emptyOpeningForm);
  const [measurementSetForm, setMeasurementSetForm] = useState<MeasurementSetFormState>(emptyMeasurementSetForm);
  const [measurementSetEditForm, setMeasurementSetEditForm] =
    useState<MeasurementSetFormState>(emptyMeasurementSetForm);
  const [measurementItemForm, setMeasurementItemForm] = useState<MeasurementItemFormState>(emptyMeasurementItemForm);
  const [measurementItemEditForm, setMeasurementItemEditForm] =
    useState<MeasurementItemFormState>(emptyMeasurementItemForm);
  const [pageMessage, setPageMessage] = useState<PageMessage | null>(null);

  const customersQuery = useQuery({
    queryKey: ["customers"],
    queryFn: listCustomers,
  });

  const propertiesQuery = useQuery({
    queryKey: ["properties"],
    queryFn: listProperties,
  });

  const projectsQuery = useQuery({
    queryKey: ["projects"],
    queryFn: listProjects,
  });

  const selectedProjectListItem = useMemo(() => {
    return (projectsQuery.data ?? []).find((project) => project.id === selectedProjectId) ?? null;
  }, [projectsQuery.data, selectedProjectId]);

  const selectedProjectQuery = useQuery({
    queryKey: ["projects", selectedProjectId],
    queryFn: () => getProject(selectedProjectId ?? ""),
    enabled: Boolean(selectedProjectId),
  });

  const selectedProject = selectedProjectQuery.data ?? selectedProjectListItem;

  const tasksQuery = useQuery({
    queryKey: ["project-tasks", selectedProjectId],
    queryFn: () => listProjectTasks(selectedProjectId ?? ""),
    enabled: Boolean(selectedProjectId),
  });

  const timelineQuery = useQuery({
    queryKey: ["project-timeline", selectedProjectId],
    queryFn: () => listProjectTimeline(selectedProjectId ?? ""),
    enabled: Boolean(selectedProjectId),
  });

  const statusHistoryQuery = useQuery({
    queryKey: ["project-status-history", selectedProjectId],
    queryFn: () => listProjectStatusHistory(selectedProjectId ?? ""),
    enabled: Boolean(selectedProjectId),
  });

  const roomsQuery = useQuery({
    queryKey: ["project-rooms", selectedProjectId],
    queryFn: () => listProjectRooms(selectedProjectId ?? ""),
    enabled: Boolean(selectedProjectId),
  });

  const selectedRoomListItem = useMemo(() => {
    return (roomsQuery.data ?? []).find((room) => room.id === selectedRoomId) ?? null;
  }, [roomsQuery.data, selectedRoomId]);

  const selectedRoomQuery = useQuery({
    queryKey: ["rooms", selectedRoomId],
    queryFn: () => getRoom(selectedRoomId ?? ""),
    enabled: Boolean(selectedRoomId),
  });

  const selectedRoom = selectedRoomQuery.data ?? selectedRoomListItem ?? roomsQuery.data?.[0] ?? null;
  const activeRoomId = selectedRoomId ?? selectedRoom?.id ?? null;

  const openingsQuery = useQuery({
    queryKey: ["room-openings", selectedRoomId],
    queryFn: () => listRoomOpenings(selectedRoomId ?? ""),
    enabled: Boolean(selectedRoomId),
  });

  const measurementSetsQuery = useQuery({
    queryKey: ["measurement-sets", selectedProjectId],
    queryFn: () => listMeasurementSets(selectedProjectId ?? ""),
    enabled: Boolean(selectedProjectId),
  });

  const selectedMeasurementSetListItem = useMemo(() => {
    return (measurementSetsQuery.data ?? []).find((measurementSet) => measurementSet.id === selectedMeasurementSetId) ?? null;
  }, [measurementSetsQuery.data, selectedMeasurementSetId]);

  const selectedMeasurementSetQuery = useQuery({
    queryKey: ["measurement-sets", selectedMeasurementSetId],
    queryFn: () => getMeasurementSet(selectedMeasurementSetId ?? ""),
    enabled: Boolean(selectedMeasurementSetId),
  });

  const selectedMeasurementSet = selectedMeasurementSetQuery.data ?? selectedMeasurementSetListItem;

  const measurementItemsQuery = useQuery({
    queryKey: ["measurement-items", selectedMeasurementSetId],
    queryFn: () => listMeasurementItems(selectedMeasurementSetId ?? ""),
    enabled: Boolean(selectedMeasurementSetId),
  });

  const customerNameById = useMemo(() => {
    return new Map((customersQuery.data ?? []).map((customer) => [customer.id, customer.name]));
  }, [customersQuery.data]);

  const propertyNameById = useMemo(() => {
    return new Map((propertiesQuery.data ?? []).map((property) => [property.id, property.name]));
  }, [propertiesQuery.data]);

  const taskTitleById = useMemo(() => {
    return new Map((tasksQuery.data ?? []).map((task) => [task.id, task.title]));
  }, [tasksQuery.data]);

  useEffect(() => {
    if (!selectedProjectId && projectsQuery.data && projectsQuery.data.length > 0) {
      setSelectedProjectId(projectsQuery.data[0].id);
    }
  }, [projectsQuery.data, selectedProjectId]);

  useEffect(() => {
    if (selectedProject) {
      setProjectEditForm(projectEditFormFromEntity(selectedProject));
      setProjectStatusForm({ status: selectedProject.status, note: "" });
    }
  }, [selectedProject]);

  useEffect(() => {
    if (!selectedTaskId && tasksQuery.data && tasksQuery.data.length > 0) {
      setSelectedTaskId(tasksQuery.data[0].id);
    }
  }, [selectedTaskId, tasksQuery.data]);

  useEffect(() => {
    const selectedTask = (tasksQuery.data ?? []).find((task) => task.id === selectedTaskId);

    if (selectedTask) {
      setTaskEditForm(taskFormFromEntity(selectedTask));
      setTaskStatusForm({ status: selectedTask.status });
    }
  }, [selectedTaskId, tasksQuery.data]);

  useEffect(() => {
    if (!selectedRoomId && roomsQuery.data && roomsQuery.data.length > 0) {
      setSelectedRoomId(roomsQuery.data[0].id);
    }
  }, [roomsQuery.data, selectedRoomId]);

  useEffect(() => {
    if (selectedRoom) {
      setRoomEditForm(roomFormFromEntity(selectedRoom));
    }
  }, [selectedRoom]);

  useEffect(() => {
    if (!selectedOpeningId && openingsQuery.data && openingsQuery.data.length > 0) {
      setSelectedOpeningId(openingsQuery.data[0].id);
    }
  }, [openingsQuery.data, selectedOpeningId]);

  useEffect(() => {
    const selectedOpening = (openingsQuery.data ?? []).find((opening) => opening.id === selectedOpeningId);

    if (selectedOpening) {
      setOpeningEditForm(openingFormFromEntity(selectedOpening));
    }
  }, [openingsQuery.data, selectedOpeningId]);

  useEffect(() => {
    if (!selectedMeasurementSetId && measurementSetsQuery.data && measurementSetsQuery.data.length > 0) {
      setSelectedMeasurementSetId(measurementSetsQuery.data[0].id);
    }
  }, [measurementSetsQuery.data, selectedMeasurementSetId]);

  useEffect(() => {
    if (selectedMeasurementSet) {
      setMeasurementSetEditForm(measurementSetFormFromEntity(selectedMeasurementSet));
    }
  }, [selectedMeasurementSet]);

  useEffect(() => {
    if (!selectedMeasurementItemId && measurementItemsQuery.data && measurementItemsQuery.data.length > 0) {
      setSelectedMeasurementItemId(measurementItemsQuery.data[0].id);
    }
  }, [measurementItemsQuery.data, selectedMeasurementItemId]);

  useEffect(() => {
    const selectedItem = (measurementItemsQuery.data ?? []).find((item) => item.id === selectedMeasurementItemId);

    if (selectedItem) {
      setMeasurementItemEditForm(measurementItemFormFromEntity(selectedItem));
    }
  }, [measurementItemsQuery.data, selectedMeasurementItemId]);

  const createProjectMutation = useMutation({
    mutationFn: createProject,
    onSuccess: (createdProject) => {
      setPageMessage({ text: "Проектот е додаден.", tone: "success" });
      setProjectForm(emptyProjectForm);

      if (!selectedProjectId) {
        setSelectedProjectId(createdProject.id);
      }

      void queryClient.invalidateQueries({ queryKey: ["projects"] });
    },
    onError: () => setPageMessage({ text: "Проектот не беше додаден. Обидете се повторно.", tone: "error" }),
  });

  const updateProjectMutation = useMutation({
    mutationFn: (payload: ProjectUpdateRequest) => {
      if (!selectedProjectId) {
        throw new Error("Missing selected project");
      }

      return updateProject(selectedProjectId, payload);
    },
    onSuccess: (updatedProject) => {
      setPageMessage({ text: "Проектот е ажуриран.", tone: "success" });
      setProjectEditForm(projectEditFormFromEntity(updatedProject));
      void queryClient.invalidateQueries({ queryKey: ["projects"] });
      void queryClient.invalidateQueries({ queryKey: ["projects", updatedProject.id] });
      void queryClient.invalidateQueries({ queryKey: ["project-timeline", updatedProject.id] });
    },
    onError: () => setPageMessage({ text: "Проектот не беше ажуриран. Обидете се повторно.", tone: "error" }),
  });

  const archiveProjectMutation = useMutation({
    mutationFn: (projectId: string) => archiveProject(projectId),
    onSuccess: (archivedProject) => {
      setPageMessage({ text: "Проектот е архивиран.", tone: "success" });
      void queryClient.invalidateQueries({ queryKey: ["projects"] });
      void queryClient.invalidateQueries({ queryKey: ["projects", archivedProject.id] });
      void queryClient.invalidateQueries({ queryKey: ["project-timeline", archivedProject.id] });
    },
    onError: () => setPageMessage({ text: "Проектот не беше архивиран. Обидете се повторно.", tone: "error" }),
  });

  const changeProjectStatusMutation = useMutation({
    mutationFn: (payload: ProjectStatusFormState) => {
      if (!selectedProjectId) {
        throw new Error("Missing selected project");
      }

      return changeProjectStatus(selectedProjectId, { status: payload.status, note: toNullable(payload.note) });
    },
    onSuccess: (updatedProject) => {
      setPageMessage({ text: "Статусот на проектот е ажуриран.", tone: "success" });
      setProjectStatusForm({ status: updatedProject.status, note: "" });
      void queryClient.invalidateQueries({ queryKey: ["projects"] });
      void queryClient.invalidateQueries({ queryKey: ["projects", updatedProject.id] });
      void queryClient.invalidateQueries({ queryKey: ["project-status-history", updatedProject.id] });
      void queryClient.invalidateQueries({ queryKey: ["project-timeline", updatedProject.id] });
    },
    onError: () => setPageMessage({ text: "Статусот не беше ажуриран. Обидете се повторно.", tone: "error" }),
  });

  const createTaskMutation = useMutation({
    mutationFn: (payload: ProjectTaskCreateRequest) => {
      if (!selectedProjectId) {
        throw new Error("Missing selected project");
      }

      return createProjectTask(selectedProjectId, payload);
    },
    onSuccess: (createdTask) => {
      setPageMessage({ text: "Задачата е додадена.", tone: "success" });
      setTaskForm(emptyTaskForm);

      if (!selectedTaskId) {
        setSelectedTaskId(createdTask.id);
      }

      void queryClient.invalidateQueries({ queryKey: ["project-tasks", selectedProjectId] });
    },
    onError: () => setPageMessage({ text: "Задачата не беше додадена. Обидете се повторно.", tone: "error" }),
  });

  const updateTaskMutation = useMutation({
    mutationFn: (payload: ProjectTaskCreateRequest) => {
      if (!selectedTaskId) {
        throw new Error("Missing selected task");
      }

      return updateProjectTask(selectedTaskId, payload);
    },
    onSuccess: () => {
      setPageMessage({ text: "Задачата е ажурирана.", tone: "success" });
      void queryClient.invalidateQueries({ queryKey: ["project-tasks", selectedProjectId] });
    },
    onError: () => setPageMessage({ text: "Задачата не беше ажурирана. Обидете се повторно.", tone: "error" }),
  });

  const changeTaskStatusMutation = useMutation({
    mutationFn: (payload: TaskStatusFormState) => {
      if (!selectedTaskId) {
        throw new Error("Missing selected task");
      }

      return changeProjectTaskStatus(selectedTaskId, { status: payload.status });
    },
    onSuccess: () => {
      setPageMessage({ text: "Статусот на задачата е ажуриран.", tone: "success" });
      void queryClient.invalidateQueries({ queryKey: ["project-tasks", selectedProjectId] });
    },
    onError: () => setPageMessage({ text: "Статусот на задачата не беше ажуриран.", tone: "error" }),
  });

  const archiveTaskMutation = useMutation({
    mutationFn: (taskId: string) => archiveProjectTask(taskId),
    onSuccess: () => {
      setPageMessage({ text: "Задачата е архивирана.", tone: "success" });
      void queryClient.invalidateQueries({ queryKey: ["project-tasks", selectedProjectId] });
    },
    onError: () => setPageMessage({ text: "Задачата не беше архивирана. Обидете се повторно.", tone: "error" }),
  });

  const createRoomMutation = useMutation({
    mutationFn: (payload: RoomCreateRequest) => {
      if (!selectedProjectId) {
        throw new Error("Missing selected project");
      }

      return createRoom(selectedProjectId, payload);
    },
    onSuccess: (createdRoom) => {
      setPageMessage({ text: "Просторијата е додадена.", tone: "success" });
      setRoomForm(emptyRoomForm);

      if (!selectedRoomId) {
        setSelectedRoomId(createdRoom.id);
      }

      void queryClient.invalidateQueries({ queryKey: ["project-rooms", selectedProjectId] });
    },
    onError: () => setPageMessage({ text: "Просторијата не беше додадена. Обидете се повторно.", tone: "error" }),
  });

  const updateRoomMutation = useMutation({
    mutationFn: (payload: RoomUpdateRequest) => {
      if (!selectedRoomId) {
        throw new Error("Missing selected room");
      }

      return updateRoom(selectedRoomId, payload);
    },
    onSuccess: (updatedRoom) => {
      setPageMessage({ text: "Просторијата е ажурирана.", tone: "success" });
      setRoomEditForm(roomFormFromEntity(updatedRoom));
      void queryClient.invalidateQueries({ queryKey: ["project-rooms", selectedProjectId] });
      void queryClient.invalidateQueries({ queryKey: ["rooms", updatedRoom.id] });
    },
    onError: () => setPageMessage({ text: "Просторијата не беше ажурирана. Обидете се повторно.", tone: "error" }),
  });

  const archiveRoomMutation = useMutation({
    mutationFn: (roomId: string) => archiveRoom(roomId),
    onSuccess: (archivedRoom) => {
      setPageMessage({ text: "Просторијата е архивирана.", tone: "success" });
      void queryClient.invalidateQueries({ queryKey: ["project-rooms", selectedProjectId] });
      void queryClient.invalidateQueries({ queryKey: ["rooms", archivedRoom.id] });
    },
    onError: () => setPageMessage({ text: "Просторијата не беше архивирана. Обидете се повторно.", tone: "error" }),
  });

  const createOpeningMutation = useMutation({
    mutationFn: (payload: RoomOpeningCreateRequest) => {
      if (!activeRoomId) {
        throw new Error("Missing selected room");
      }

      return createRoomOpening(activeRoomId, payload);
    },
    onSuccess: (createdOpening) => {
      setPageMessage({ text: "Отворот е додаден.", tone: "success" });
      setOpeningForm(emptyOpeningForm);

      if (!selectedOpeningId) {
        setSelectedOpeningId(createdOpening.id);
      }

      void queryClient.invalidateQueries({ queryKey: ["room-openings", activeRoomId] });
      void queryClient.invalidateQueries({ queryKey: ["rooms", activeRoomId] });
      void queryClient.invalidateQueries({ queryKey: ["project-rooms", selectedProjectId] });
    },
    onError: () => setPageMessage({ text: "Отворот не беше додаден. Обидете се повторно.", tone: "error" }),
  });

  const updateOpeningMutation = useMutation({
    mutationFn: (payload: RoomOpeningUpdateRequest) => {
      if (!selectedOpeningId) {
        throw new Error("Missing selected opening");
      }

      return updateRoomOpening(selectedOpeningId, payload);
    },
    onSuccess: () => {
      setPageMessage({ text: "Отворот е ажуриран.", tone: "success" });
      void queryClient.invalidateQueries({ queryKey: ["room-openings", selectedRoomId] });
      void queryClient.invalidateQueries({ queryKey: ["rooms", selectedRoomId] });
      void queryClient.invalidateQueries({ queryKey: ["project-rooms", selectedProjectId] });
    },
    onError: () => setPageMessage({ text: "Отворот не беше ажуриран. Обидете се повторно.", tone: "error" }),
  });

  const archiveOpeningMutation = useMutation({
    mutationFn: (openingId: string) => archiveRoomOpening(openingId),
    onSuccess: () => {
      setPageMessage({ text: "Отворот е архивиран.", tone: "success" });
      void queryClient.invalidateQueries({ queryKey: ["room-openings", selectedRoomId] });
      void queryClient.invalidateQueries({ queryKey: ["rooms", selectedRoomId] });
      void queryClient.invalidateQueries({ queryKey: ["project-rooms", selectedProjectId] });
    },
    onError: () => setPageMessage({ text: "Отворот не беше архивиран. Обидете се повторно.", tone: "error" }),
  });

  const createMeasurementSetMutation = useMutation({
    mutationFn: (payload: MeasurementSetCreateRequest) => {
      if (!selectedProjectId) {
        throw new Error("Missing selected project");
      }

      return createMeasurementSet(selectedProjectId, payload);
    },
    onSuccess: (createdMeasurementSet) => {
      setPageMessage({ text: "Сетот за мерење е додаден.", tone: "success" });
      setMeasurementSetForm(emptyMeasurementSetForm);

      if (!selectedMeasurementSetId) {
        setSelectedMeasurementSetId(createdMeasurementSet.id);
      }

      void queryClient.invalidateQueries({ queryKey: ["measurement-sets", selectedProjectId] });
    },
    onError: () => setPageMessage({ text: "Сетот не беше додаден. Обидете се повторно.", tone: "error" }),
  });

  const createMeasurementItemMutation = useMutation({
    mutationFn: (payload: MeasurementItemCreateRequest) => {
      if (!selectedMeasurementSetId) {
        throw new Error("Missing selected measurement set");
      }

      return createMeasurementItem(selectedMeasurementSetId, payload);
    },
    onSuccess: (createdItem) => {
      setPageMessage({ text: "Мерката е додадена.", tone: "success" });
      setMeasurementItemForm(emptyMeasurementItemForm);

      if (!selectedMeasurementItemId) {
        setSelectedMeasurementItemId(createdItem.id);
      }

      void queryClient.invalidateQueries({ queryKey: ["measurement-items", selectedMeasurementSetId] });
    },
    onError: () => setPageMessage({ text: "Мерката не беше додадена. Обидете се повторно.", tone: "error" }),
  });

  const updateMeasurementItemMutation = useMutation({
    mutationFn: (payload: MeasurementItemUpdateRequest) => {
      if (!selectedMeasurementItemId) {
        throw new Error("Missing selected measurement item");
      }

      return updateMeasurementItem(selectedMeasurementItemId, payload);
    },
    onSuccess: () => {
      setPageMessage({ text: "Мерката е ажурирана.", tone: "success" });
      void queryClient.invalidateQueries({ queryKey: ["measurement-items", selectedMeasurementSetId] });
    },
    onError: () => setPageMessage({ text: "Мерката не беше ажурирана. Обидете се повторно.", tone: "error" }),
  });

  const archiveMeasurementItemMutation = useMutation({
    mutationFn: (measurementItemId: string) => archiveMeasurementItem(measurementItemId),
    onSuccess: () => {
      setPageMessage({ text: "Мерката е архивирана.", tone: "success" });
      void queryClient.invalidateQueries({ queryKey: ["measurement-items", selectedMeasurementSetId] });
    },
    onError: () => setPageMessage({ text: "Мерката не беше архивирана. Обидете се повторно.", tone: "error" }),
  });

  function handleProjectField(field: keyof ProjectFormState) {
    return (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) =>
      setProjectForm((current) => ({ ...current, [field]: event.target.value }));
  }

  function handleProjectEditField(field: keyof ProjectEditFormState) {
    return (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
      setProjectEditForm((current) => ({ ...current, [field]: event.target.value }));
  }

  function handleTaskField(field: keyof TaskFormState) {
    return (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
      setTaskForm((current) => ({ ...current, [field]: event.target.value }));
  }

  function handleTaskEditField(field: keyof TaskFormState) {
    return (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
      setTaskEditForm((current) => ({ ...current, [field]: event.target.value }));
  }

  function handleRoomField(field: keyof RoomFormState) {
    return (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) =>
      setRoomForm((current) => ({ ...current, [field]: event.target.value }));
  }

  function handleRoomEditField(field: keyof RoomFormState) {
    return (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) =>
      setRoomEditForm((current) => ({ ...current, [field]: event.target.value }));
  }

  function handleOpeningField(field: keyof OpeningFormState) {
    return (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) =>
      setOpeningForm((current) => ({ ...current, [field]: event.target.value }));
  }

  function handleOpeningEditField(field: keyof OpeningFormState) {
    return (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) =>
      setOpeningEditForm((current) => ({ ...current, [field]: event.target.value }));
  }

  function handleMeasurementSetField(field: keyof MeasurementSetFormState) {
    return (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) =>
      setMeasurementSetForm((current) => ({ ...current, [field]: event.target.value }));
  }

  function handleMeasurementItemField(field: keyof MeasurementItemFormState) {
    return (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) =>
      setMeasurementItemForm((current) => ({ ...current, [field]: event.target.value }));
  }

  function handleMeasurementItemEditField(field: keyof MeasurementItemFormState) {
    return (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) =>
      setMeasurementItemEditForm((current) => ({ ...current, [field]: event.target.value }));
  }

  function handleCreateProject(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const payload = projectPayloadFromForm(projectForm);

    if (!payload.customer_id) {
      setPageMessage({ text: "Изберете клиент за проектот.", tone: "error" });
      return;
    }

    if (!payload.property_id) {
      setPageMessage({ text: "Изберете објект за проектот.", tone: "error" });
      return;
    }

    if (!payload.name) {
      setPageMessage({ text: "Внесете име на проект.", tone: "error" });
      return;
    }

    createProjectMutation.mutate(payload);
  }

  function handleUpdateProject(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const payload = projectUpdatePayloadFromForm(projectEditForm);

    if (!payload.name) {
      setPageMessage({ text: "Внесете име на проект.", tone: "error" });
      return;
    }

    updateProjectMutation.mutate(payload);
  }

  function handleProjectStatus(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    changeProjectStatusMutation.mutate(projectStatusForm);
  }

  function handleCreateTask(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const payload = taskPayloadFromForm(taskForm);

    if (!payload.title) {
      setPageMessage({ text: "Внесете наслов на задача.", tone: "error" });
      return;
    }

    createTaskMutation.mutate(payload);
  }

  function handleUpdateTask(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const payload = taskPayloadFromForm(taskEditForm);

    if (!payload.title) {
      setPageMessage({ text: "Внесете наслов на задача.", tone: "error" });
      return;
    }

    updateTaskMutation.mutate(payload);
  }

  function handleTaskStatus(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    changeTaskStatusMutation.mutate(taskStatusForm);
  }

  function handleCreateRoom(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const payload = roomPayloadFromForm(roomForm);

    if (!payload.name) {
      setPageMessage({ text: "Внесете име на просторија.", tone: "error" });
      return;
    }

    if (!hasPositiveNumbers([roomForm.length, roomForm.width, roomForm.height])) {
      setPageMessage({ text: "Димензиите мора да бидат поголеми од нула.", tone: "error" });
      return;
    }

    createRoomMutation.mutate(payload);
  }

  function handleUpdateRoom(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const payload = roomPayloadFromForm(roomEditForm);

    if (!payload.name) {
      setPageMessage({ text: "Внесете име на просторија.", tone: "error" });
      return;
    }

    if (!hasPositiveNumbers([roomEditForm.length, roomEditForm.width, roomEditForm.height])) {
      setPageMessage({ text: "Димензиите мора да бидат поголеми од нула.", tone: "error" });
      return;
    }

    updateRoomMutation.mutate(payload);
  }

  function handleCreateOpening(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const payload = openingPayloadFromForm(openingForm);

    if (!payload.name) {
      setPageMessage({ text: "Внесете име на отвор.", tone: "error" });
      return;
    }

    if (!hasPositiveNumbers([openingForm.width, openingForm.height, openingForm.quantity])) {
      setPageMessage({ text: "Димензиите и количината мора да бидат поголеми од нула.", tone: "error" });
      return;
    }

    createOpeningMutation.mutate(payload);
  }

  function handleUpdateOpening(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const payload = openingPayloadFromForm(openingEditForm);

    if (!payload.name) {
      setPageMessage({ text: "Внесете име на отвор.", tone: "error" });
      return;
    }

    if (!hasPositiveNumbers([openingEditForm.width, openingEditForm.height, openingEditForm.quantity])) {
      setPageMessage({ text: "Димензиите и количината мора да бидат поголеми од нула.", tone: "error" });
      return;
    }

    updateOpeningMutation.mutate(payload);
  }

  function handleCreateMeasurementSet(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const payload = measurementSetPayloadFromForm(measurementSetForm);

    if (!payload.name) {
      setPageMessage({ text: "Внесете име на сет.", tone: "error" });
      return;
    }

    createMeasurementSetMutation.mutate(payload);
  }

  function handleCreateMeasurementItem(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const payload = measurementItemPayloadFromForm(measurementItemForm);

    if (!payload.name) {
      setPageMessage({ text: "Внесете име на мерка.", tone: "error" });
      return;
    }

    if (!hasPositiveNumbers([measurementItemForm.quantity])) {
      setPageMessage({ text: "Количината мора да биде поголема од нула.", tone: "error" });
      return;
    }

    createMeasurementItemMutation.mutate(payload);
  }

  function handleUpdateMeasurementItem(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const payload = measurementItemPayloadFromForm(measurementItemEditForm);

    if (!payload.name) {
      setPageMessage({ text: "Внесете име на мерка.", tone: "error" });
      return;
    }

    if (!hasPositiveNumbers([measurementItemEditForm.quantity])) {
      setPageMessage({ text: "Количината мора да биде поголема од нула.", tone: "error" });
      return;
    }

    updateMeasurementItemMutation.mutate(payload);
  }

  const selectedTask = (tasksQuery.data ?? []).find((task) => task.id === selectedTaskId) ?? null;
  const selectedOpening = (openingsQuery.data ?? []).find((opening) => opening.id === selectedOpeningId) ?? null;
  const selectedMeasurementItem =
    (measurementItemsQuery.data ?? []).find((item) => item.id === selectedMeasurementItemId) ?? null;

  return (
    <section className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-normal text-ink">Проекти</h1>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
          Управувајте со проекти, задачи, простории, отвори и мерења преку податоците од серверот.
        </p>
      </div>

      {pageMessage ? <Message tone={pageMessage.tone}>{pageMessage.text}</Message> : null}

      <div className="grid gap-6 xl:grid-cols-[360px_minmax(0,1fr)]">
        <aside className="space-y-4">
          <Panel title="Нов проект">
            <form onSubmit={handleCreateProject} className="space-y-4">
              <SelectField
                label="Клиент за проект"
                name="project-customer-id"
                value={projectForm.customer_id}
                required
                onChange={handleProjectField("customer_id")}
              >
                <option value="">Изберете клиент</option>
                {(customersQuery.data ?? []).map((customer) => (
                  <option key={customer.id} value={customer.id}>
                    {customer.name}
                  </option>
                ))}
              </SelectField>
              <SelectField
                label="Објект за проект"
                name="project-property-id"
                value={projectForm.property_id}
                required
                onChange={handleProjectField("property_id")}
              >
                <option value="">Изберете објект</option>
                {(propertiesQuery.data ?? []).map((property) => (
                  <option key={property.id} value={property.id}>
                    {property.name}
                  </option>
                ))}
              </SelectField>
              <FormField
                label="Име на проект"
                name="project-name"
                value={projectForm.name}
                required
                onChange={handleProjectField("name")}
              />
              <TextAreaField
                label="Опис на проект"
                name="project-description"
                value={projectForm.description}
                onChange={handleProjectField("description")}
              />
              <FormField
                label="Адреса на проект"
                name="project-address"
                value={projectForm.address}
                onChange={handleProjectField("address")}
              />
              <NumberField
                label="Договорена цена"
                name="project-agreed-price"
                value={projectForm.agreed_project_price}
                onChange={handleProjectField("agreed_project_price")}
              />
              <div className="grid gap-3 sm:grid-cols-2">
                <FormField
                  label="Почеток"
                  name="project-start-date"
                  type="date"
                  value={projectForm.start_date}
                  onChange={handleProjectField("start_date")}
                />
                <FormField
                  label="Рок"
                  name="project-due-date"
                  type="date"
                  value={projectForm.due_date}
                  onChange={handleProjectField("due_date")}
                />
              </div>
              <PrimaryButton disabled={createProjectMutation.isPending}>Додај проект</PrimaryButton>
            </form>
          </Panel>

          <Panel title="Листа на проекти">
            {projectsQuery.isLoading ? <Message>Се вчитуваат проектите.</Message> : null}
            {projectsQuery.isError ? <Message tone="error">Проектите не може да се вчитаат.</Message> : null}
            {!projectsQuery.isLoading && (projectsQuery.data ?? []).length === 0 ? (
              <EmptyState>Нема проекти. Додајте проект поврзан со клиент и објект.</EmptyState>
            ) : null}
            <div className="space-y-2">
              {(projectsQuery.data ?? []).map((project) => (
                <button
                  key={project.id}
                  type="button"
                  onClick={() => setSelectedProjectId(project.id)}
                  className={[
                    "w-full rounded-md border px-3 py-3 text-left text-sm transition",
                    selectedProjectId === project.id
                      ? "border-brand bg-brand/10 text-brand"
                      : "border-line bg-white text-slate-700 hover:border-brand",
                  ].join(" ")}
                >
                  <span className="block font-bold">Отвори: {project.name}</span>
                  <span className="mt-1 block text-xs text-slate-500">
                    Статус: {formatProjectStatus(project.status)}
                  </span>
                </button>
              ))}
            </div>
          </Panel>
        </aside>

        <div className="space-y-6">
          <Panel title="Преглед">
            {selectedProject ? (
              <div className="space-y-5">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <p className="text-xl font-bold tracking-normal text-ink">{selectedProject.name}</p>
                    <p className="mt-1 text-sm text-slate-600">
                      {customerNameById.get(selectedProject.customer_id) ?? "Клиент"} -{" "}
                      {propertyNameById.get(selectedProject.property_id) ?? "Објект"}
                    </p>
                  </div>
                  <StatusBadge>{formatProjectStatus(selectedProject.status)}</StatusBadge>
                </div>

                <dl className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
                  <DetailRow label="Опис" value={selectedProject.description} />
                  <DetailRow label="Адреса" value={selectedProject.address} />
                  <DetailRow label="Договорена цена" value={selectedProject.agreed_project_price} />
                  <DetailRow label="Почеток" value={formatDate(selectedProject.start_date)} />
                  <DetailRow label="Рок" value={formatDate(selectedProject.due_date)} />
                  <DetailRow label="Архивирано" value={selectedProject.archived_at ? formatDate(selectedProject.archived_at) : null} />
                </dl>

                <form onSubmit={handleUpdateProject} className="grid gap-3 lg:grid-cols-2">
                  <FormField
                    label="Име за уредување на проект"
                    name="project-edit-name"
                    value={projectEditForm.name}
                    required
                    onChange={handleProjectEditField("name")}
                  />
                  <FormField
                    label="Адреса за уредување"
                    name="project-edit-address"
                    value={projectEditForm.address}
                    onChange={handleProjectEditField("address")}
                  />
                  <NumberField
                    label="Договорена цена за уредување"
                    name="project-edit-agreed-price"
                    value={projectEditForm.agreed_project_price}
                    onChange={handleProjectEditField("agreed_project_price")}
                  />
                  <div className="grid gap-3 sm:grid-cols-2">
                    <FormField
                      label="Почеток за уредување"
                      name="project-edit-start-date"
                      type="date"
                      value={projectEditForm.start_date}
                      onChange={handleProjectEditField("start_date")}
                    />
                    <FormField
                      label="Рок за уредување"
                      name="project-edit-due-date"
                      type="date"
                      value={projectEditForm.due_date}
                      onChange={handleProjectEditField("due_date")}
                    />
                  </div>
                  <div className="lg:col-span-2">
                    <TextAreaField
                      label="Опис за уредување"
                      name="project-edit-description"
                      value={projectEditForm.description}
                      onChange={handleProjectEditField("description")}
                    />
                  </div>
                  <div className="flex flex-wrap gap-2 lg:col-span-2">
                    <SecondaryButton type="submit" disabled={updateProjectMutation.isPending}>
                      Зачувај проект
                    </SecondaryButton>
                    <SecondaryButton
                      icon="archive"
                      onClick={() => selectedProjectId && archiveProjectMutation.mutate(selectedProjectId)}
                      disabled={archiveProjectMutation.isPending}
                    >
                      Архивирај проект
                    </SecondaryButton>
                  </div>
                </form>

                <form onSubmit={handleProjectStatus} className="grid gap-3 md:grid-cols-[220px_minmax(0,1fr)_auto]">
                  <SelectField
                    label="Статус на проект"
                    name="project-status"
                    value={projectStatusForm.status}
                    onChange={(event) => setProjectStatusForm((current) => ({ ...current, status: event.target.value }))}
                  >
                    {projectStatuses.map((status) => (
                      <option key={status.value} value={status.value}>
                        Статус: {status.label}
                      </option>
                    ))}
                  </SelectField>
                  <FormField
                    label="Белешка за статус"
                    name="project-status-note"
                    value={projectStatusForm.note}
                    onChange={(event) => setProjectStatusForm((current) => ({ ...current, note: event.target.value }))}
                  />
                  <div className="flex items-end">
                    <SecondaryButton type="submit" icon="check" disabled={changeProjectStatusMutation.isPending}>
                      Зачувај статус
                    </SecondaryButton>
                  </div>
                </form>

                <div className="grid gap-4 xl:grid-cols-2">
                  <div>
                    <h3 className="text-sm font-bold text-ink">Историја на статус</h3>
                    <div className="mt-3 space-y-2">
                      {(statusHistoryQuery.data ?? []).length > 0 ? (
                        (statusHistoryQuery.data ?? []).map((entry) => (
                          <div key={entry.id} className="rounded-md border border-line bg-slate-50 px-3 py-2 text-sm">
                            <p className="font-semibold text-slate-800">
                              {entry.from_status ? formatProjectStatus(entry.from_status) : "Почеток"} →{" "}
                              {formatProjectStatus(entry.to_status)}
                            </p>
                            <p className="mt-1 text-slate-600">{entry.note ?? "Без белешка"}</p>
                          </div>
                        ))
                      ) : (
                        <EmptyState>Нема статусна историја.</EmptyState>
                      )}
                    </div>
                  </div>

                  <div>
                    <h3 className="text-sm font-bold text-ink">Временска линија</h3>
                    <div className="mt-3 space-y-2">
                      {(timelineQuery.data ?? []).length > 0 ? (
                        (timelineQuery.data ?? []).map((event) => (
                          <div key={event.id} className="rounded-md border border-line bg-slate-50 px-3 py-2 text-sm">
                            <p className="font-semibold text-slate-800">{event.message ?? event.event_type}</p>
                            <p className="mt-1 text-xs text-slate-500">{formatDate(event.created_at)}</p>
                          </div>
                        ))
                      ) : (
                        <EmptyState>Нема активности за проектот.</EmptyState>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <EmptyState>Изберете проект или креирајте нов проект.</EmptyState>
            )}
          </Panel>

          <Panel title="Задачи">
            {selectedProject ? (
              <div className="space-y-5">
                <form onSubmit={handleCreateTask} className="grid gap-3 lg:grid-cols-2">
                  <FormField
                    label="Наслов на задача"
                    name="task-title"
                    value={taskForm.title}
                    required
                    onChange={handleTaskField("title")}
                  />
                  <FormField
                    label="Рок за задача"
                    name="task-due-date"
                    type="date"
                    value={taskForm.due_date}
                    onChange={handleTaskField("due_date")}
                  />
                  <div className="lg:col-span-2">
                    <TextAreaField
                      label="Опис на задача"
                      name="task-description"
                      value={taskForm.description}
                      onChange={handleTaskField("description")}
                    />
                  </div>
                  <div className="lg:col-span-2">
                    <PrimaryButton disabled={createTaskMutation.isPending}>Додај задача</PrimaryButton>
                  </div>
                </form>

                <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
                  <div className="space-y-2">
                    {(tasksQuery.data ?? []).length > 0 ? (
                      (tasksQuery.data ?? []).map((task) => (
                        <button
                          key={task.id}
                          type="button"
                          onClick={() => setSelectedTaskId(task.id)}
                          className={[
                            "w-full rounded-md border px-3 py-3 text-left text-sm transition",
                            selectedTaskId === task.id
                              ? "border-brand bg-brand/10"
                              : "border-line bg-white hover:border-brand",
                          ].join(" ")}
                        >
                          <span className="block font-bold text-ink">{task.title}</span>
                          <span className="mt-1 block text-xs text-slate-500">{formatTaskStatus(task.status)}</span>
                        </button>
                      ))
                    ) : (
                      <EmptyState>Нема задачи за проектот.</EmptyState>
                    )}
                  </div>

                  {selectedTask ? (
                    <div className="space-y-4 rounded-md border border-line bg-slate-50 p-3">
                      <form onSubmit={handleUpdateTask} className="space-y-3">
                        <FormField
                          label="Наслов за уредување на задача"
                          name="task-edit-title"
                          value={taskEditForm.title}
                          required
                          onChange={handleTaskEditField("title")}
                        />
                        <FormField
                          label="Рок за уредување на задача"
                          name="task-edit-due-date"
                          type="date"
                          value={taskEditForm.due_date}
                          onChange={handleTaskEditField("due_date")}
                        />
                        <TextAreaField
                          label="Опис за уредување на задача"
                          name="task-edit-description"
                          value={taskEditForm.description}
                          onChange={handleTaskEditField("description")}
                        />
                        <SecondaryButton type="submit" disabled={updateTaskMutation.isPending}>
                          Зачувај задача
                        </SecondaryButton>
                      </form>

                      <form onSubmit={handleTaskStatus} className="flex flex-wrap items-end gap-3">
                        <SelectField
                          label="Статус на задача"
                          name="task-status"
                          value={taskStatusForm.status}
                          onChange={(event) => setTaskStatusForm({ status: event.target.value })}
                        >
                          {taskStatuses.map((status) => (
                            <option key={status.value} value={status.value}>
                              {status.label}
                            </option>
                          ))}
                        </SelectField>
                        <SecondaryButton type="submit" icon="check" disabled={changeTaskStatusMutation.isPending}>
                          Промени статус
                        </SecondaryButton>
                        <SecondaryButton
                          icon="archive"
                          onClick={() => selectedTaskId && archiveTaskMutation.mutate(selectedTaskId)}
                          disabled={archiveTaskMutation.isPending}
                        >
                          Архивирај задача
                        </SecondaryButton>
                      </form>
                    </div>
                  ) : null}
                </div>
              </div>
            ) : (
              <EmptyState>Изберете проект за да додадете задачи.</EmptyState>
            )}
          </Panel>

          <Panel title="Простории">
            {selectedProject ? (
              <div className="space-y-5">
                <form onSubmit={handleCreateRoom} className="grid gap-3 lg:grid-cols-3">
                  <FormField
                    label="Име на просторија"
                    name="room-name"
                    value={roomForm.name}
                    required
                    onChange={handleRoomField("name")}
                  />
                  <SelectField
                    label="Тип на просторија"
                    name="room-type"
                    value={roomForm.room_type}
                    onChange={handleRoomField("room_type")}
                  >
                    {roomTypes.map((roomType) => (
                      <option key={roomType.value} value={roomType.value}>
                        {roomType.label}
                      </option>
                    ))}
                  </SelectField>
                  <SelectField
                    label="Задача за просторија"
                    name="room-project-task"
                    value={roomForm.project_task_id}
                    onChange={handleRoomField("project_task_id")}
                  >
                    <option value="">Без задача</option>
                    {(tasksQuery.data ?? []).map((task) => (
                      <option key={task.id} value={task.id}>
                        Задача: {task.title}
                      </option>
                    ))}
                  </SelectField>
                  <NumberField label="Должина" name="room-length" value={roomForm.length} required onChange={handleRoomField("length")} />
                  <NumberField label="Ширина" name="room-width" value={roomForm.width} required onChange={handleRoomField("width")} />
                  <NumberField label="Висина" name="room-height" value={roomForm.height} required onChange={handleRoomField("height")} />
                  <div className="lg:col-span-3">
                    <TextAreaField label="Белешка за просторија" name="room-note" value={roomForm.note} onChange={handleRoomField("note")} />
                  </div>
                  <div className="lg:col-span-3">
                    <PrimaryButton disabled={createRoomMutation.isPending}>Додај просторија</PrimaryButton>
                  </div>
                </form>

                <div className="grid gap-4 lg:grid-cols-[minmax(0,280px)_minmax(0,1fr)]">
                  <div className="space-y-2">
                    {(roomsQuery.data ?? []).length > 0 ? (
                      (roomsQuery.data ?? []).map((room) => (
                        <button
                          key={room.id}
                          type="button"
                          onClick={() => setSelectedRoomId(room.id)}
                          className={[
                            "w-full rounded-md border px-3 py-3 text-left text-sm transition",
                            selectedRoomId === room.id ? "border-brand bg-brand/10" : "border-line bg-white hover:border-brand",
                          ].join(" ")}
                        >
                          <span className="block font-bold text-ink">{room.name}</span>
                          <span className="mt-1 block text-xs text-slate-500">{formatRoomType(room.room_type)}</span>
                        </button>
                      ))
                    ) : (
                      <EmptyState>Нема простории за проектот.</EmptyState>
                    )}
                  </div>

                  {selectedRoom ? (
                    <div className="space-y-5">
                      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
                        <AreaTile label="Подна површина" value={formatSquareMeters(selectedRoom.floor_area)} />
                        <AreaTile label="Таванска површина" value={formatSquareMeters(selectedRoom.ceiling_area, 1)} />
                        <AreaTile label="Бруто ѕидови" value={formatSquareMeters(selectedRoom.wall_area_gross)} />
                        <AreaTile label="Нето ѕидови" value={formatSquareMeters(selectedRoom.wall_area_net)} />
                        <AreaTile label="Површина за бојадисување" value={formatSquareMeters(selectedRoom.total_paintable_area)} />
                      </div>

                      <form onSubmit={handleUpdateRoom} className="grid gap-3 lg:grid-cols-3">
                        <FormField
                          label="Име за уредување на просторија"
                          name="room-edit-name"
                          value={roomEditForm.name}
                          required
                          onChange={handleRoomEditField("name")}
                        />
                        <SelectField
                          label="Тип за уредување на просторија"
                          name="room-edit-type"
                          value={roomEditForm.room_type}
                          onChange={handleRoomEditField("room_type")}
                        >
                          {roomTypes.map((roomType) => (
                            <option key={roomType.value} value={roomType.value}>
                              {roomType.label}
                            </option>
                          ))}
                        </SelectField>
                        <SelectField
                          label="Задача за уредување на просторија"
                          name="room-edit-project-task"
                          value={roomEditForm.project_task_id}
                          onChange={handleRoomEditField("project_task_id")}
                        >
                          <option value="">Без задача</option>
                          {(tasksQuery.data ?? []).map((task) => (
                            <option key={task.id} value={task.id}>
                              Задача: {task.title}
                            </option>
                          ))}
                        </SelectField>
                        <NumberField
                          label="Должина за уредување"
                          name="room-edit-length"
                          value={roomEditForm.length}
                          required
                          onChange={handleRoomEditField("length")}
                        />
                        <NumberField
                          label="Ширина за уредување"
                          name="room-edit-width"
                          value={roomEditForm.width}
                          required
                          onChange={handleRoomEditField("width")}
                        />
                        <NumberField
                          label="Висина за уредување"
                          name="room-edit-height"
                          value={roomEditForm.height}
                          required
                          onChange={handleRoomEditField("height")}
                        />
                        <div className="flex flex-wrap gap-2 lg:col-span-3">
                          <SecondaryButton type="submit" disabled={updateRoomMutation.isPending}>
                            Зачувај просторија
                          </SecondaryButton>
                          <SecondaryButton
                            icon="archive"
                            onClick={() => selectedRoomId && archiveRoomMutation.mutate(selectedRoomId)}
                            disabled={archiveRoomMutation.isPending}
                          >
                            Архивирај просторија
                          </SecondaryButton>
                        </div>
                      </form>

                      <div className="rounded-md border border-line bg-slate-50 p-3">
                        <h3 className="text-sm font-bold text-ink">Отвори</h3>
                        <form onSubmit={handleCreateOpening} className="mt-3 grid gap-3 lg:grid-cols-3">
                          <FormField
                            label="Име на отвор"
                            name="opening-name"
                            value={openingForm.name}
                            required
                            onChange={handleOpeningField("name")}
                          />
                          <SelectField
                            label="Тип на отвор"
                            name="opening-type"
                            value={openingForm.opening_type}
                            onChange={handleOpeningField("opening_type")}
                          >
                            {openingTypes.map((openingType) => (
                              <option key={openingType.value} value={openingType.value}>
                                {openingType.label}
                              </option>
                            ))}
                          </SelectField>
                          <NumberField
                            label="Количина на отвори"
                            name="opening-quantity"
                            value={openingForm.quantity}
                            required
                            onChange={handleOpeningField("quantity")}
                          />
                          <NumberField
                            label="Ширина на отвор"
                            name="opening-width"
                            value={openingForm.width}
                            required
                            onChange={handleOpeningField("width")}
                          />
                          <NumberField
                            label="Висина на отвор"
                            name="opening-height"
                            value={openingForm.height}
                            required
                            onChange={handleOpeningField("height")}
                          />
                          <div className="flex items-end">
                            <PrimaryButton disabled={createOpeningMutation.isPending}>Додај отвор</PrimaryButton>
                          </div>
                        </form>

                        <div className="mt-4 grid gap-4 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
                          <div className="space-y-2">
                            {(openingsQuery.data ?? []).length > 0 ? (
                              (openingsQuery.data ?? []).map((opening) => (
                                <button
                                  key={opening.id}
                                  type="button"
                                  onClick={() => setSelectedOpeningId(opening.id)}
                                  className={[
                                    "w-full rounded-md border px-3 py-2 text-left text-sm transition",
                                    selectedOpeningId === opening.id
                                      ? "border-brand bg-white"
                                      : "border-line bg-white hover:border-brand",
                                  ].join(" ")}
                                >
                                  <span className="block font-bold text-ink">{opening.name}</span>
                                  <span className="text-xs text-slate-500">
                                    {formatOpeningType(opening.opening_type)} - {formatSquareMeters(opening.opening_area)}
                                  </span>
                                </button>
                              ))
                            ) : (
                              <EmptyState>Нема отвори за просторијата.</EmptyState>
                            )}
                          </div>

                          {selectedOpening ? (
                            <form onSubmit={handleUpdateOpening} className="space-y-3 rounded-md border border-line bg-white p-3">
                              <FormField
                                label="Име за уредување на отвор"
                                name="opening-edit-name"
                                value={openingEditForm.name}
                                required
                                onChange={handleOpeningEditField("name")}
                              />
                              <SelectField
                                label="Тип за уредување на отвор"
                                name="opening-edit-type"
                                value={openingEditForm.opening_type}
                                onChange={handleOpeningEditField("opening_type")}
                              >
                                {openingTypes.map((openingType) => (
                                  <option key={openingType.value} value={openingType.value}>
                                    {openingType.label}
                                  </option>
                                ))}
                              </SelectField>
                              <div className="grid gap-3 sm:grid-cols-3">
                                <NumberField
                                  label="Ширина за уредување на отвор"
                                  name="opening-edit-width"
                                  value={openingEditForm.width}
                                  required
                                  onChange={handleOpeningEditField("width")}
                                />
                                <NumberField
                                  label="Висина за уредување на отвор"
                                  name="opening-edit-height"
                                  value={openingEditForm.height}
                                  required
                                  onChange={handleOpeningEditField("height")}
                                />
                                <NumberField
                                  label="Количина за уредување на отвори"
                                  name="opening-edit-quantity"
                                  value={openingEditForm.quantity}
                                  required
                                  onChange={handleOpeningEditField("quantity")}
                                />
                              </div>
                              <div className="flex flex-wrap gap-2">
                                <SecondaryButton type="submit" disabled={updateOpeningMutation.isPending}>
                                  Зачувај отвор
                                </SecondaryButton>
                                <SecondaryButton
                                  icon="archive"
                                  onClick={() => selectedOpeningId && archiveOpeningMutation.mutate(selectedOpeningId)}
                                  disabled={archiveOpeningMutation.isPending}
                                >
                                  Архивирај отвор
                                </SecondaryButton>
                              </div>
                            </form>
                          ) : null}
                        </div>
                      </div>
                    </div>
                  ) : null}
                </div>
              </div>
            ) : (
              <EmptyState>Изберете проект за да додадете простории.</EmptyState>
            )}
          </Panel>

          <Panel title="Мерења">
            {selectedProject ? (
              <div className="space-y-5">
                <form onSubmit={handleCreateMeasurementSet} className="grid gap-3 lg:grid-cols-3">
                  <FormField
                    label="Име на сет"
                    name="measurement-set-name"
                    value={measurementSetForm.name}
                    required
                    onChange={handleMeasurementSetField("name")}
                  />
                  <SelectField
                    label="Задача за сет"
                    name="measurement-set-task"
                    value={measurementSetForm.project_task_id}
                    onChange={handleMeasurementSetField("project_task_id")}
                  >
                    <option value="">Без задача</option>
                    {(tasksQuery.data ?? []).map((task) => (
                      <option key={task.id} value={task.id}>
                        Задача: {task.title}
                      </option>
                    ))}
                  </SelectField>
                  <div className="flex items-end">
                    <PrimaryButton disabled={createMeasurementSetMutation.isPending}>Додај сет</PrimaryButton>
                  </div>
                  <div className="lg:col-span-3">
                    <TextAreaField
                      label="Опис на сет"
                      name="measurement-set-description"
                      value={measurementSetForm.description}
                      onChange={handleMeasurementSetField("description")}
                    />
                  </div>
                </form>

                <div className="grid gap-4 lg:grid-cols-[minmax(0,280px)_minmax(0,1fr)]">
                  <div className="space-y-2">
                    {(measurementSetsQuery.data ?? []).length > 0 ? (
                      (measurementSetsQuery.data ?? []).map((measurementSet) => (
                        <button
                          key={measurementSet.id}
                          type="button"
                          onClick={() => setSelectedMeasurementSetId(measurementSet.id)}
                          className={[
                            "w-full rounded-md border px-3 py-3 text-left text-sm transition",
                            selectedMeasurementSetId === measurementSet.id
                              ? "border-brand bg-brand/10"
                              : "border-line bg-white hover:border-brand",
                          ].join(" ")}
                        >
                          <span className="block font-bold text-ink">{measurementSet.name}</span>
                          <span className="mt-1 block text-xs text-slate-500">
                            {measurementSet.project_task_id
                              ? taskTitleById.get(measurementSet.project_task_id) ?? "Задача"
                              : "Без задача"}
                          </span>
                        </button>
                      ))
                    ) : (
                      <EmptyState>Нема сетови за мерење.</EmptyState>
                    )}
                  </div>

                  {selectedMeasurementSet ? (
                    <div className="space-y-5">
                      <dl className="grid gap-4 rounded-md border border-line bg-slate-50 p-3 sm:grid-cols-2">
                        <DetailRow label="Сет" value={selectedMeasurementSet.name} />
                        <DetailRow
                          label="Задача"
                          value={
                            selectedMeasurementSet.project_task_id
                              ? taskTitleById.get(selectedMeasurementSet.project_task_id) ?? "Задача"
                              : null
                          }
                        />
                        <DetailRow label="Опис" value={measurementSetEditForm.description} />
                      </dl>

                      <form onSubmit={handleCreateMeasurementItem} className="grid gap-3 lg:grid-cols-4">
                        <FormField
                          label="Име на мерка"
                          name="measurement-item-name"
                          value={measurementItemForm.name}
                          required
                          onChange={handleMeasurementItemField("name")}
                        />
                        <SelectField
                          label="Единица"
                          name="measurement-item-unit"
                          value={measurementItemForm.unit}
                          onChange={handleMeasurementItemField("unit")}
                        >
                          {measurementUnits.map((unit) => (
                            <option key={unit.value} value={unit.value}>
                              {unit.label}
                            </option>
                          ))}
                        </SelectField>
                        <NumberField
                          label="Количина"
                          name="measurement-item-quantity"
                          value={measurementItemForm.quantity}
                          required
                          onChange={handleMeasurementItemField("quantity")}
                        />
                        <div className="flex items-end">
                          <PrimaryButton disabled={createMeasurementItemMutation.isPending}>Додај мерка</PrimaryButton>
                        </div>
                      </form>

                      <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
                        <div className="space-y-2">
                          {(measurementItemsQuery.data ?? []).length > 0 ? (
                            (measurementItemsQuery.data ?? []).map((item) => (
                              <button
                                key={item.id}
                                type="button"
                                onClick={() => setSelectedMeasurementItemId(item.id)}
                                className={[
                                  "w-full rounded-md border px-3 py-2 text-left text-sm transition",
                                  selectedMeasurementItemId === item.id
                                    ? "border-brand bg-white"
                                    : "border-line bg-white hover:border-brand",
                                ].join(" ")}
                              >
                                <span className="block font-bold text-ink">{item.name}</span>
                                <span className="text-xs text-slate-500">
                                  {formatNumber(item.quantity)} {formatMeasurementUnit(item.unit)}
                                </span>
                              </button>
                            ))
                          ) : (
                            <EmptyState>Нема мерки во сетот.</EmptyState>
                          )}
                        </div>

                        {selectedMeasurementItem ? (
                          <form onSubmit={handleUpdateMeasurementItem} className="space-y-3 rounded-md border border-line bg-slate-50 p-3">
                            <FormField
                              label="Име за уредување на мерка"
                              name="measurement-item-edit-name"
                              value={measurementItemEditForm.name}
                              required
                              onChange={handleMeasurementItemEditField("name")}
                            />
                            <SelectField
                              label="Единица за уредување"
                              name="measurement-item-edit-unit"
                              value={measurementItemEditForm.unit}
                              onChange={handleMeasurementItemEditField("unit")}
                            >
                              {measurementUnits.map((unit) => (
                                <option key={unit.value} value={unit.value}>
                                  {unit.label}
                                </option>
                              ))}
                            </SelectField>
                            <NumberField
                              label="Количина за уредување"
                              name="measurement-item-edit-quantity"
                              value={measurementItemEditForm.quantity}
                              required
                              onChange={handleMeasurementItemEditField("quantity")}
                            />
                            <div className="flex flex-wrap gap-2">
                              <SecondaryButton type="submit" disabled={updateMeasurementItemMutation.isPending}>
                                Зачувај мерка
                              </SecondaryButton>
                              <SecondaryButton
                                icon="archive"
                                onClick={() =>
                                  selectedMeasurementItemId &&
                                  archiveMeasurementItemMutation.mutate(selectedMeasurementItemId)
                                }
                                disabled={archiveMeasurementItemMutation.isPending}
                              >
                                Архивирај мерка
                              </SecondaryButton>
                            </div>
                          </form>
                        ) : null}
                      </div>
                    </div>
                  ) : null}
                </div>
              </div>
            ) : (
              <EmptyState>Изберете проект за да внесете мерења.</EmptyState>
            )}
          </Panel>

          <Panel title="Подоцна">
            <div className="flex flex-wrap gap-2 text-sm text-slate-600">
              {["Пресметки", "Понуди", "Уплати", "Фотографии", "Документи"].map((item) => (
                <span key={item} className="rounded-md border border-line bg-slate-50 px-3 py-2">
                  {item}
                </span>
              ))}
            </div>
          </Panel>
        </div>
      </div>
    </section>
  );
}
