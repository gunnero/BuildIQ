import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { App } from "./App";
import { getToken, saveToken } from "./auth/tokenStorage";

const now = "2026-07-08T10:00:00Z";

const currentUser = {
  id: "user-1",
  company_id: "company-1",
  name: "Александар Димовски",
  email: "aleksandar@example.com",
  status: "active",
  is_hq_admin: false,
  roles: ["owner"],
  created_at: now,
  updated_at: now,
};

const currentCompany = {
  id: "company-1",
  name: "Демо Градба",
  tax_number: null,
  address: null,
  phone: null,
  email: "info@example.com",
  status: "active",
  is_internal: false,
  created_at: now,
  updated_at: now,
};

const currentSubscription = {
  id: "subscription-1",
  company_id: "company-1",
  status: "active",
  plan: {
    id: "plan-1",
    key: "starter",
    name: "Starter",
    price_mkd: 0,
    billing_period: "monthly",
    is_active: true,
    created_at: now,
    updated_at: now,
  },
  created_at: now,
  updated_at: now,
};

const customer = {
  id: "customer-1",
  company_id: "company-1",
  name: "Ана Стојановска",
  phone: "070111222",
  email: "ana@example.com",
  address: "Партизанска 10",
  note: "Сака понуда по соби.",
  status: "active",
  archived_at: null,
  created_at: now,
  updated_at: now,
};

const createdCustomer = {
  ...customer,
  id: "customer-2",
  name: "Петар Петров",
  phone: "071333444",
  email: null,
  address: null,
  note: null,
};

const customerContact = {
  id: "customer-contact-1",
  company_id: "company-1",
  customer_id: "customer-1",
  full_name: "Игор Стојановски",
  phone: "075111222",
  email: null,
  role: "Сопруг",
  note: null,
  is_primary: true,
  archived_at: null,
  created_at: now,
  updated_at: now,
};

const property = {
  id: "property-1",
  company_id: "company-1",
  customer_id: "customer-1",
  name: "Стан Центар",
  address: "Македонија 12",
  city: "Скопје",
  note: "Трет кат.",
  status: "active",
  archived_at: null,
  created_at: now,
  updated_at: now,
};

const createdProperty = {
  ...property,
  id: "property-2",
  name: "Куќа Кисела Вода",
  address: "Народни херои 5",
  city: "Скопје",
  note: null,
};

const propertyContact = {
  id: "property-contact-1",
  company_id: "company-1",
  property_id: "property-1",
  full_name: "Марко Колев",
  phone: "078555666",
  email: null,
  role: "Домар",
  note: null,
  is_primary: false,
  archived_at: null,
  created_at: now,
  updated_at: now,
};

const propertyNote = {
  id: "property-note-1",
  company_id: "company-1",
  property_id: "property-1",
  content: "Потребна е проверка на влезната врата.",
  created_by_user_id: "user-1",
  archived_at: null,
  created_at: now,
  updated_at: now,
};

const project = {
  id: "project-1",
  company_id: "company-1",
  customer_id: "customer-1",
  property_id: "property-1",
  name: "Реновирање стан",
  description: "Боја и подови.",
  address: "Македонија 12",
  status: "active",
  agreed_project_price: 40000,
  start_date: "2026-07-10",
  due_date: "2026-07-30",
  archived_at: null,
  created_at: now,
  updated_at: now,
};

const createdProject = {
  ...project,
  id: "project-2",
  name: "Нова бања",
  description: null,
  address: null,
  agreed_project_price: null,
  start_date: null,
  due_date: null,
};

const projectTask = {
  id: "task-1",
  company_id: "company-1",
  project_id: "project-1",
  title: "Демонтажа",
  description: "Отстранување стар материјал.",
  status: "pending",
  assigned_user_id: null,
  due_date: "2026-07-12",
  completed_at: null,
  archived_at: null,
  created_at: now,
  updated_at: now,
};

const createdProjectTask = {
  ...projectTask,
  id: "task-2",
  title: "Молерисување",
  description: null,
  due_date: null,
};

const projectTimelineEvent = {
  id: "timeline-1",
  company_id: "company-1",
  project_id: "project-1",
  event_type: "project_created",
  message: "Проектот е креиран.",
  created_by_user_id: "user-1",
  created_at: now,
};

const projectStatusHistory = {
  id: "status-history-1",
  company_id: "company-1",
  project_id: "project-1",
  from_status: "planned",
  to_status: "active",
  note: "Почнато на терен.",
  changed_by_user_id: "user-1",
  created_at: now,
};

const room = {
  id: "room-1",
  company_id: "company-1",
  project_id: "project-1",
  project_task_id: null,
  name: "Дневна соба",
  room_type: "living_room",
  floor: null,
  note: null,
  length: 5,
  width: 4,
  height: 2.7,
  floor_area: 20,
  ceiling_area: 20,
  wall_area_gross: 48.6,
  openings_area_total: 3.2,
  wall_area_net: 45.4,
  total_paintable_area: 65.4,
  archived_at: null,
  created_at: now,
  updated_at: now,
};

const createdRoom = {
  ...room,
  id: "room-2",
  name: "Спална соба",
  room_type: "bedroom",
  length: 4,
  width: 3,
  height: 2.6,
  floor_area: 12,
  ceiling_area: 12,
  wall_area_gross: 36.4,
  openings_area_total: 0,
  wall_area_net: 36.4,
  total_paintable_area: 48.4,
};

const roomOpening = {
  id: "opening-1",
  company_id: "company-1",
  room_id: "room-1",
  opening_type: "door",
  name: "Врата",
  width: 0.9,
  height: 2,
  quantity: 1,
  opening_area: 1.8,
  note: null,
  archived_at: null,
  created_at: now,
  updated_at: now,
};

const createdRoomOpening = {
  ...roomOpening,
  id: "opening-2",
  name: "Прозорец",
  opening_type: "window",
  width: 1.2,
  height: 1.4,
  quantity: 2,
  opening_area: 3.36,
};

const measurementSet = {
  id: "measurement-set-1",
  company_id: "company-1",
  project_id: "project-1",
  project_task_id: null,
  name: "Главни мерења",
  description: "Основни површини.",
  archived_at: null,
  created_at: now,
  updated_at: now,
};

const createdMeasurementSet = {
  ...measurementSet,
  id: "measurement-set-2",
  name: "Дополнителни мерења",
  description: null,
};

const measurementItem = {
  id: "measurement-item-1",
  company_id: "company-1",
  measurement_set_id: "measurement-set-1",
  name: "Ѕидна површина",
  unit: "m2",
  quantity: 54,
  note: null,
  archived_at: null,
  created_at: now,
  updated_at: now,
};

const createdMeasurementItem = {
  ...measurementItem,
  id: "measurement-item-2",
  name: "Лепак",
  unit: "bag",
  quantity: 5,
};

const paintMaterial = {
  id: "material-paint-1",
  company_id: "company-1",
  name: "Мат боја",
  sku: "PAINT-01",
  description: null,
  category_id: null,
  manufacturer_id: null,
  unit_id: "unit-liter",
  coverage_value: 10,
  coverage_unit: "m2/liter",
  package_quantity: 1,
  waste_percentage_default: 10,
  is_active: true,
  archived_at: null,
  created_at: now,
  updated_at: now,
};

const primerMaterial = {
  ...paintMaterial,
  id: "material-primer-1",
  name: "Прајмер",
  sku: "PRIMER-01",
  coverage_value: 12,
  waste_percentage_default: null,
};

const calculationEngines = [
  { engine_type: "painting", engine_version: "painting-1", implemented: true, status: "implemented" },
  { engine_type: "tiles", engine_version: "placeholder-1", implemented: false, status: "not_implemented" },
  { engine_type: "knauf", engine_version: "placeholder-1", implemented: false, status: "not_implemented" },
];

const paintingCalculationRun = {
  id: "calculation-1",
  company_id: "company-1",
  project_id: "project-1",
  project_task_id: "task-1",
  room_id: "room-1",
  measurement_set_id: null,
  engine_type: "painting",
  engine_version: "painting-1",
  status: "completed",
  input_payload: {
    include_walls: true,
    include_ceiling: true,
    coats: 2,
    primer_coats: 1,
    paint_material_id: "material-paint-1",
    primer_material_id: "material-primer-1",
    waste_percentage: 10,
    labor_rate_per_m2: 120,
    notes: "Проверка на дневна соба.",
  },
  output_payload: {
    selected_area_m2: 65.4,
    wall_area_net_m2: 45.4,
    ceiling_area_m2: 20,
    total_paintable_area_m2: 65.4,
    coats: 2,
    primer_coats: 1,
    waste_percentage: 10,
    paint_required_liters: 14.388,
    primer_required_liters: 7.194,
    paint_material_cost: 5100.12,
    primer_material_cost: 1200.34,
    labor_cost: 7848,
    total_cost: 22222.22,
    assumptions: ["Room-computed areas were used.", "Waste percentage is applied to paint and primer quantities."],
    warnings: ["Не е пронајдена цена за прајмер материјалот."],
    notes: "Проверка на дневна соба.",
  },
  line_items: [
    {
      id: "calculation-line-1",
      company_id: "company-1",
      calculation_run_id: "calculation-1",
      sort_order: 1,
      name: "Paint material",
      description: "Мат боја",
      unit: "liter",
      quantity: 14.388,
      payload: { material_id: "material-paint-1", unit_price: 354.47, total_cost: 5100.12 },
      created_at: now,
    },
    {
      id: "calculation-line-2",
      company_id: "company-1",
      calculation_run_id: "calculation-1",
      sort_order: 2,
      name: "Labor",
      description: "Painting labor",
      unit: "m2",
      quantity: 65.4,
      payload: { unit_price: 120, total_cost: 7848 },
      created_at: now,
    },
  ],
  created_by_user_id: "user-1",
  created_at: now,
  archived_at: null,
};

const failedCalculationRun = {
  ...paintingCalculationRun,
  id: "calculation-2",
  status: "failed",
  project_task_id: null,
  room_id: null,
  output_payload: {
    error_code: "painting_area_missing",
    message: "Не е дадена просторија или сет мерења со употреблива површина за бојадисување.",
  },
  line_items: [],
};

const createdPaintingCalculationRun = {
  ...paintingCalculationRun,
  id: "calculation-3",
  created_at: "2026-07-08T11:00:00Z",
};

const estimate = {
  id: "estimate-1",
  company_id: "company-1",
  customer_id: "customer-1",
  property_id: "property-1",
  project_id: "project-1",
  estimate_number: "EST-001",
  title: "Понуда за бојадисување",
  description: "Рачно внесена понуда.",
  status: "draft",
  source_calculation_run_id: null,
  sent_at: null,
  accepted_at: null,
  rejected_at: null,
  archived_at: null,
  created_at: now,
  updated_at: now,
};

const createdEstimate = {
  ...estimate,
  id: "estimate-2",
  estimate_number: "EST-002",
  title: "Рачна понуда",
  description: "Понуда за дневна соба.",
};

const estimateFromCalculation = {
  ...estimate,
  id: "estimate-3",
  estimate_number: "EST-003",
  title: "Понуда од пресметка",
  description: null,
  source_calculation_run_id: "calculation-1",
};

const estimateRevision = {
  id: "revision-1",
  company_id: "company-1",
  estimate_id: "estimate-1",
  revision_number: 1,
  status: "draft",
  notes: null,
  terms: null,
  source_calculation_run_id: null,
  subtotal: 30000,
  discount_total: 2000,
  adjustment_total: 500,
  tax_total: 0,
  total: 28500,
  sent_at: null,
  accepted_at: null,
  rejected_at: null,
  archived_at: null,
  created_at: now,
  updated_at: now,
};

const estimateItem = {
  id: "estimate-item-1",
  company_id: "company-1",
  estimate_revision_id: "revision-1",
  item_type: "material",
  name: "Мат боја",
  description: "Боја од пресметка.",
  material_id: "material-paint-1",
  quantity: 10,
  unit: "liter",
  unit_price: 300,
  total_price: 3000,
  source_calculation_run_id: null,
  source_calculation_line_item_id: null,
  sort_order: 1,
  archived_at: null,
  created_at: now,
  updated_at: now,
};

const createdEstimateItem = {
  ...estimateItem,
  id: "estimate-item-2",
  item_type: "service",
  name: "Дополнителна услуга",
  description: null,
  material_id: null,
  quantity: 2,
  unit: "hour",
  unit_price: 1500,
  total_price: 3000,
  sort_order: 2,
};

const estimateDocument = {
  id: "document-1",
  company_id: "company-1",
  estimate_id: "estimate-1",
  revision_id: "revision-1",
  document_type: "estimate_quote_pdf",
  file_path: "estimate-documents/company-1/estimate-1/document-1.pdf",
  generated_by_user_id: "user-1",
  generated_at: now,
  archived_at: null,
  created_at: now,
  updated_at: now,
};

const payment = {
  id: "payment-1",
  company_id: "company-1",
  customer_id: "customer-1",
  project_id: "project-1",
  estimate_id: "estimate-1",
  amount: 20000,
  currency: "MKD",
  payment_method: "bank_transfer",
  payment_date: "2026-07-08",
  status: "received",
  note: "Прва уплата.",
  created_by_user_id: "user-1",
  reversal_reason: null,
  reversed_at: null,
  reversed_by_user_id: null,
  archived_at: null,
  created_at: now,
  updated_at: now,
  allocations: [
    {
      id: "payment-allocation-1",
      company_id: "company-1",
      payment_id: "payment-1",
      project_id: "project-1",
      estimate_id: "estimate-1",
      amount: 20000,
      note: "Аванс.",
      archived_at: null,
      created_at: now,
      updated_at: now,
    },
  ],
};

const createdPayment = {
  ...payment,
  id: "payment-2",
  amount: 15000,
  payment_method: "cash",
  note: null,
  allocations: [],
};

const expenseCategory = {
  id: "expense-category-1",
  company_id: "company-1",
  name: "Материјали",
  description: "Трошоци за материјали.",
  archived_at: null,
  created_at: now,
  updated_at: now,
};

const createdExpenseCategory = {
  ...expenseCategory,
  id: "expense-category-2",
  name: "Транспорт",
  description: null,
};

const expense = {
  id: "expense-1",
  company_id: "company-1",
  project_id: "project-1",
  category_id: "expense-category-1",
  supplier_id: null,
  material_id: "material-paint-1",
  description: "Купена боја",
  amount: 12000,
  currency: "MKD",
  expense_date: "2026-07-08",
  payment_method: "card",
  status: "recorded",
  note: "Фискална сметка.",
  created_by_user_id: "user-1",
  reversal_reason: null,
  reversed_at: null,
  reversed_by_user_id: null,
  archived_at: null,
  created_at: now,
  updated_at: now,
};

const createdExpense = {
  ...expense,
  id: "expense-2",
  description: "Превоз на материјали",
  amount: 3000,
  category_id: "expense-category-2",
  material_id: null,
  payment_method: "cash",
  note: null,
};

const projectFinancialSummary = {
  project_id: "project-1",
  customer_id: "customer-1",
  accepted_estimate_total: 50000,
  agreed_project_price: 40000,
  revenue_basis: "accepted_estimate",
  total_received_payments: 12345,
  total_pending_payments: 6789,
  total_reversed_payments: 1000,
  outstanding_balance: 33333,
  total_recorded_expenses: 9876,
  total_reversed_expenses: 500,
  estimated_profit: 22222,
  payment_status: "partially_paid",
};

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

function mockSessionFetch(token = "demo-token") {
  return vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input);
    const authorization = init?.headers instanceof Headers ? init.headers.get("Authorization") : null;

    if (url.endsWith("/api/v1/auth/me")) {
      expect(authorization).toBe(`Bearer ${token}`);
      return Promise.resolve(jsonResponse(currentUser));
    }

    if (url.endsWith("/api/v1/companies/me")) {
      expect(authorization).toBe(`Bearer ${token}`);
      return Promise.resolve(jsonResponse(currentCompany));
    }

    if (url.endsWith("/api/v1/subscription/me")) {
      expect(authorization).toBe(`Bearer ${token}`);
      return Promise.resolve(jsonResponse(currentSubscription));
    }

    return Promise.resolve(jsonResponse({ detail: "Not found" }, 404));
  });
}

function mockCustomerPropertyFetch(token = "demo-token") {
  return vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input);
    const method = init?.method ?? "GET";
    const authorization = init?.headers instanceof Headers ? init.headers.get("Authorization") : null;

    expect(authorization).toBe(`Bearer ${token}`);

    if (url.endsWith("/api/v1/auth/me")) {
      return Promise.resolve(jsonResponse(currentUser));
    }

    if (url.endsWith("/api/v1/companies/me")) {
      return Promise.resolve(jsonResponse(currentCompany));
    }

    if (url.endsWith("/api/v1/subscription/me")) {
      return Promise.resolve(jsonResponse(currentSubscription));
    }

    if (url.endsWith("/api/v1/customers") && method === "GET") {
      return Promise.resolve(jsonResponse([customer]));
    }

    if (url.endsWith("/api/v1/customers") && method === "POST") {
      return Promise.resolve(jsonResponse(createdCustomer, 201));
    }

    if (url.endsWith("/api/v1/customers/customer-1") && method === "GET") {
      return Promise.resolve(jsonResponse(customer));
    }

    if (url.endsWith("/api/v1/customers/customer-1/contacts") && method === "GET") {
      return Promise.resolve(jsonResponse([customerContact]));
    }

    if (url.endsWith("/api/v1/properties") && method === "GET") {
      return Promise.resolve(jsonResponse([property]));
    }

    if (url.endsWith("/api/v1/properties") && method === "POST") {
      return Promise.resolve(jsonResponse(createdProperty, 201));
    }

    if (url.endsWith("/api/v1/properties/property-1") && method === "GET") {
      return Promise.resolve(jsonResponse(property));
    }

    if (url.endsWith("/api/v1/properties/property-1/contacts") && method === "GET") {
      return Promise.resolve(jsonResponse([propertyContact]));
    }

    if (url.endsWith("/api/v1/properties/property-1/notes") && method === "GET") {
      return Promise.resolve(jsonResponse([propertyNote]));
    }

    return Promise.resolve(jsonResponse({ detail: "Not found" }, 404));
  });
}

function mockProjectFetch(token = "demo-token") {
  return vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input);
    const method = init?.method ?? "GET";
    const authorization = init?.headers instanceof Headers ? init.headers.get("Authorization") : null;

    expect(authorization).toBe(`Bearer ${token}`);

    if (url.endsWith("/api/v1/auth/me")) {
      return Promise.resolve(jsonResponse(currentUser));
    }

    if (url.endsWith("/api/v1/companies/me")) {
      return Promise.resolve(jsonResponse(currentCompany));
    }

    if (url.endsWith("/api/v1/subscription/me")) {
      return Promise.resolve(jsonResponse(currentSubscription));
    }

    if (url.endsWith("/api/v1/customers") && method === "GET") {
      return Promise.resolve(jsonResponse([customer]));
    }

    if (url.endsWith("/api/v1/properties") && method === "GET") {
      return Promise.resolve(jsonResponse([property]));
    }

    if (url.endsWith("/api/v1/projects") && method === "GET") {
      return Promise.resolve(jsonResponse([project]));
    }

    if (url.endsWith("/api/v1/projects") && method === "POST") {
      return Promise.resolve(jsonResponse(createdProject, 201));
    }

    if (url.endsWith("/api/v1/projects/project-1") && method === "GET") {
      return Promise.resolve(jsonResponse(project));
    }

    if (url.endsWith("/api/v1/projects/project-1") && method === "PATCH") {
      return Promise.resolve(jsonResponse({ ...project, name: "Реновирање стан - фаза 2" }));
    }

    if (url.endsWith("/api/v1/projects/project-1/archive") && method === "POST") {
      return Promise.resolve(jsonResponse({ ...project, status: "archived", archived_at: now }));
    }

    if (url.endsWith("/api/v1/projects/project-1/status-history") && method === "GET") {
      return Promise.resolve(jsonResponse([projectStatusHistory]));
    }

    if (url.endsWith("/api/v1/projects/project-1/timeline") && method === "GET") {
      return Promise.resolve(jsonResponse([projectTimelineEvent]));
    }

    if (url.endsWith("/api/v1/projects/project-1/financial-summary") && method === "GET") {
      return Promise.resolve(jsonResponse(projectFinancialSummary));
    }

    if (url.endsWith("/api/v1/projects/project-1/tasks") && method === "GET") {
      return Promise.resolve(jsonResponse([projectTask]));
    }

    if (url.endsWith("/api/v1/projects/project-1/tasks") && method === "POST") {
      return Promise.resolve(jsonResponse(createdProjectTask, 201));
    }

    if (url.endsWith("/api/v1/tasks/task-1") && method === "PATCH") {
      return Promise.resolve(jsonResponse({ ...projectTask, title: "Подготовка" }));
    }

    if (url.endsWith("/api/v1/tasks/task-1/status") && method === "POST") {
      return Promise.resolve(jsonResponse({ ...projectTask, status: "active" }));
    }

    if (url.endsWith("/api/v1/tasks/task-1/archive") && method === "POST") {
      return Promise.resolve(jsonResponse({ ...projectTask, status: "archived", archived_at: now }));
    }

    if (url.endsWith("/api/v1/projects/project-1/rooms") && method === "GET") {
      return Promise.resolve(jsonResponse([room]));
    }

    if (url.endsWith("/api/v1/projects/project-1/rooms") && method === "POST") {
      return Promise.resolve(jsonResponse(createdRoom, 201));
    }

    if (url.endsWith("/api/v1/rooms/room-1") && method === "GET") {
      return Promise.resolve(jsonResponse(room));
    }

    if (url.endsWith("/api/v1/rooms/room-1") && method === "PATCH") {
      return Promise.resolve(jsonResponse({ ...room, name: "Голема дневна соба" }));
    }

    if (url.endsWith("/api/v1/rooms/room-1/archive") && method === "POST") {
      return Promise.resolve(jsonResponse({ ...room, archived_at: now }));
    }

    if (url.endsWith("/api/v1/rooms/room-1/openings") && method === "GET") {
      return Promise.resolve(jsonResponse([roomOpening]));
    }

    if (url.endsWith("/api/v1/rooms/room-1/openings") && method === "POST") {
      return Promise.resolve(jsonResponse(createdRoomOpening, 201));
    }

    if (url.endsWith("/api/v1/openings/opening-1") && method === "PATCH") {
      return Promise.resolve(jsonResponse({ ...roomOpening, name: "Влезна врата" }));
    }

    if (url.endsWith("/api/v1/openings/opening-1/archive") && method === "POST") {
      return Promise.resolve(jsonResponse({ ...roomOpening, archived_at: now }));
    }

    if (url.endsWith("/api/v1/projects/project-1/measurement-sets") && method === "GET") {
      return Promise.resolve(jsonResponse([measurementSet]));
    }

    if (url.endsWith("/api/v1/projects/project-1/measurement-sets") && method === "POST") {
      return Promise.resolve(jsonResponse(createdMeasurementSet, 201));
    }

    if (url.endsWith("/api/v1/measurement-sets/measurement-set-1") && method === "GET") {
      return Promise.resolve(jsonResponse(measurementSet));
    }

    if (url.endsWith("/api/v1/measurement-sets/measurement-set-1/items") && method === "GET") {
      return Promise.resolve(jsonResponse([measurementItem]));
    }

    if (url.endsWith("/api/v1/measurement-sets/measurement-set-1/items") && method === "POST") {
      return Promise.resolve(jsonResponse(createdMeasurementItem, 201));
    }

    if (url.endsWith("/api/v1/measurement-items/measurement-item-1") && method === "PATCH") {
      return Promise.resolve(jsonResponse({ ...measurementItem, quantity: 60 }));
    }

    if (url.endsWith("/api/v1/measurement-items/measurement-item-1/archive") && method === "POST") {
      return Promise.resolve(jsonResponse({ ...measurementItem, archived_at: now }));
    }

    return Promise.resolve(jsonResponse({ detail: "Not found" }, 404));
  });
}

function mockCalculationFetch(token = "demo-token") {
  return vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input);
    const method = init?.method ?? "GET";
    const authorization = init?.headers instanceof Headers ? init.headers.get("Authorization") : null;

    expect(authorization).toBe(`Bearer ${token}`);

    if (url.endsWith("/api/v1/auth/me")) {
      return Promise.resolve(jsonResponse(currentUser));
    }

    if (url.endsWith("/api/v1/companies/me")) {
      return Promise.resolve(jsonResponse(currentCompany));
    }

    if (url.endsWith("/api/v1/subscription/me")) {
      return Promise.resolve(jsonResponse(currentSubscription));
    }

    if (url.endsWith("/api/v1/projects") && method === "GET") {
      return Promise.resolve(jsonResponse([project]));
    }

    if (url.endsWith("/api/v1/projects/project-1/tasks") && method === "GET") {
      return Promise.resolve(jsonResponse([projectTask]));
    }

    if (url.endsWith("/api/v1/projects/project-1/rooms") && method === "GET") {
      return Promise.resolve(jsonResponse([room]));
    }

    if (url.endsWith("/api/v1/projects/project-1/measurement-sets") && method === "GET") {
      return Promise.resolve(jsonResponse([measurementSet]));
    }

    if (url.endsWith("/api/v1/materials") && method === "GET") {
      return Promise.resolve(jsonResponse([paintMaterial, primerMaterial]));
    }

    if (url.endsWith("/api/v1/calculation-engines") && method === "GET") {
      return Promise.resolve(jsonResponse(calculationEngines));
    }

    if (url.endsWith("/api/v1/calculations") && method === "GET") {
      return Promise.resolve(jsonResponse([paintingCalculationRun, failedCalculationRun]));
    }

    if (url.endsWith("/api/v1/calculations/calculation-1") && method === "GET") {
      return Promise.resolve(jsonResponse(paintingCalculationRun));
    }

    if (url.endsWith("/api/v1/calculations/calculation-2") && method === "GET") {
      return Promise.resolve(jsonResponse(failedCalculationRun));
    }

    if (url.endsWith("/api/v1/calculations/run") && method === "POST") {
      return Promise.resolve(jsonResponse(createdPaintingCalculationRun, 201));
    }

    if (url.endsWith("/api/v1/estimates/from-calculation/calculation-1") && method === "POST") {
      return Promise.resolve(jsonResponse(estimateFromCalculation, 201));
    }

    return Promise.resolve(jsonResponse({ detail: "Not found" }, 404));
  });
}

function mockEstimateFetch(token = "demo-token", options: { pdfError?: boolean } = {}) {
  return vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input);
    const method = init?.method ?? "GET";
    const authorization = init?.headers instanceof Headers ? init.headers.get("Authorization") : null;

    expect(authorization).toBe(`Bearer ${token}`);

    if (url.endsWith("/api/v1/auth/me")) {
      return Promise.resolve(jsonResponse(currentUser));
    }

    if (url.endsWith("/api/v1/companies/me")) {
      return Promise.resolve(jsonResponse(currentCompany));
    }

    if (url.endsWith("/api/v1/subscription/me")) {
      return Promise.resolve(jsonResponse(currentSubscription));
    }

    if (url.endsWith("/api/v1/customers") && method === "GET") {
      return Promise.resolve(jsonResponse([customer]));
    }

    if (url.endsWith("/api/v1/properties") && method === "GET") {
      return Promise.resolve(jsonResponse([property]));
    }

    if (url.endsWith("/api/v1/projects") && method === "GET") {
      return Promise.resolve(jsonResponse([project]));
    }

    if (url.endsWith("/api/v1/materials") && method === "GET") {
      return Promise.resolve(jsonResponse([paintMaterial, primerMaterial]));
    }

    if (url.endsWith("/api/v1/calculations") && method === "GET") {
      return Promise.resolve(jsonResponse([paintingCalculationRun, failedCalculationRun]));
    }

    if (url.endsWith("/api/v1/estimates") && method === "GET") {
      return Promise.resolve(jsonResponse([estimate]));
    }

    if (url.endsWith("/api/v1/estimates") && method === "POST") {
      return Promise.resolve(jsonResponse(createdEstimate, 201));
    }

    if (url.endsWith("/api/v1/estimates/estimate-1") && method === "GET") {
      return Promise.resolve(jsonResponse(estimate));
    }

    if (url.endsWith("/api/v1/estimates/estimate-1/archive") && method === "POST") {
      return Promise.resolve(jsonResponse({ ...estimate, status: "archived", archived_at: now }));
    }

    if (url.endsWith("/api/v1/estimates/estimate-1/status") && method === "POST") {
      const body = typeof init?.body === "string" ? JSON.parse(init.body) : {};
      return Promise.resolve(jsonResponse({ ...estimate, status: body.status, [`${body.status}_at`]: now }));
    }

    if (url.endsWith("/api/v1/estimates/from-calculation/calculation-1") && method === "POST") {
      return Promise.resolve(jsonResponse(estimateFromCalculation, 201));
    }

    if (url.endsWith("/api/v1/estimates/estimate-1/pdf") && method === "POST") {
      if (options.pdfError) {
        return Promise.resolve(jsonResponse({ detail: "Не може да се генерира PDF за архивирана понуда." }, 400));
      }

      return Promise.resolve(jsonResponse(estimateDocument, 201));
    }

    if (url.endsWith("/api/v1/estimates/estimate-1/revisions") && method === "GET") {
      return Promise.resolve(jsonResponse([estimateRevision]));
    }

    if (url.endsWith("/api/v1/estimate-revisions/revision-1") && method === "GET") {
      return Promise.resolve(jsonResponse(estimateRevision));
    }

    if (url.endsWith("/api/v1/estimate-revisions/revision-1/items") && method === "GET") {
      return Promise.resolve(jsonResponse([estimateItem]));
    }

    if (url.endsWith("/api/v1/estimate-revisions/revision-1/items") && method === "POST") {
      return Promise.resolve(jsonResponse(createdEstimateItem, 201));
    }

    if (url.endsWith("/api/v1/estimate-items/estimate-item-1") && method === "PATCH") {
      return Promise.resolve(jsonResponse({ ...estimateItem, name: "Мат боја премиум", quantity: 12, total_price: 3600 }));
    }

    if (url.endsWith("/api/v1/estimate-items/estimate-item-1/archive") && method === "POST") {
      return Promise.resolve(jsonResponse({ ...estimateItem, archived_at: now }));
    }

    if (url.endsWith("/api/v1/estimate-documents/document-1/download") && method === "GET") {
      return Promise.resolve(
        new Response(new Blob(["%PDF-1.4"], { type: "application/pdf" }), {
          status: 200,
          headers: { "Content-Type": "application/pdf" },
        }),
      );
    }

    return Promise.resolve(jsonResponse({ detail: "Not found" }, 404));
  });
}

function mockFinancialFetch(token = "demo-token") {
  return vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input);
    const method = init?.method ?? "GET";
    const authorization = init?.headers instanceof Headers ? init.headers.get("Authorization") : null;

    expect(authorization).toBe(`Bearer ${token}`);

    if (url.endsWith("/api/v1/auth/me")) {
      return Promise.resolve(jsonResponse(currentUser));
    }

    if (url.endsWith("/api/v1/companies/me")) {
      return Promise.resolve(jsonResponse(currentCompany));
    }

    if (url.endsWith("/api/v1/subscription/me")) {
      return Promise.resolve(jsonResponse(currentSubscription));
    }

    if (url.endsWith("/api/v1/customers") && method === "GET") {
      return Promise.resolve(jsonResponse([customer]));
    }

    if (url.endsWith("/api/v1/projects") && method === "GET") {
      return Promise.resolve(jsonResponse([project]));
    }

    if (url.endsWith("/api/v1/materials") && method === "GET") {
      return Promise.resolve(jsonResponse([paintMaterial, primerMaterial]));
    }

    if (url.endsWith("/api/v1/estimates") && method === "GET") {
      return Promise.resolve(jsonResponse([estimate]));
    }

    if (url.endsWith("/api/v1/payments") && method === "GET") {
      return Promise.resolve(jsonResponse([payment]));
    }

    if (url.endsWith("/api/v1/payments") && method === "POST") {
      return Promise.resolve(jsonResponse(createdPayment, 201));
    }

    if (url.endsWith("/api/v1/payments/payment-1") && method === "GET") {
      return Promise.resolve(jsonResponse(payment));
    }

    if (url.endsWith("/api/v1/payments/payment-1/reverse") && method === "POST") {
      return Promise.resolve(jsonResponse({ ...payment, status: "reversed", reversal_reason: "Погрешна уплата.", reversed_at: now }));
    }

    if (url.endsWith("/api/v1/payments/payment-1/archive") && method === "POST") {
      return Promise.resolve(jsonResponse({ ...payment, status: "archived", archived_at: now }));
    }

    if (url.endsWith("/api/v1/expense-categories") && method === "GET") {
      return Promise.resolve(jsonResponse([expenseCategory, createdExpenseCategory]));
    }

    if (url.endsWith("/api/v1/expense-categories") && method === "POST") {
      return Promise.resolve(jsonResponse(createdExpenseCategory, 201));
    }

    if (url.endsWith("/api/v1/expense-categories/expense-category-1") && method === "PATCH") {
      return Promise.resolve(jsonResponse({ ...expenseCategory, name: "Материјали и алат" }));
    }

    if (url.endsWith("/api/v1/expense-categories/expense-category-1/archive") && method === "POST") {
      return Promise.resolve(jsonResponse({ ...expenseCategory, archived_at: now }));
    }

    if (url.endsWith("/api/v1/expenses") && method === "GET") {
      return Promise.resolve(jsonResponse([expense]));
    }

    if (url.endsWith("/api/v1/expenses") && method === "POST") {
      return Promise.resolve(jsonResponse(createdExpense, 201));
    }

    if (url.endsWith("/api/v1/expenses/expense-1") && method === "GET") {
      return Promise.resolve(jsonResponse(expense));
    }

    if (url.endsWith("/api/v1/expenses/expense-1/reverse") && method === "POST") {
      return Promise.resolve(jsonResponse({ ...expense, status: "reversed", reversal_reason: "Погрешен трошок.", reversed_at: now }));
    }

    if (url.endsWith("/api/v1/expenses/expense-1/archive") && method === "POST") {
      return Promise.resolve(jsonResponse({ ...expense, status: "archived", archived_at: now }));
    }

    return Promise.resolve(jsonResponse({ detail: "Not found" }, 404));
  });
}

describe("App", () => {
  afterEach(() => {
    cleanup();
    localStorage.clear();
    window.history.pushState(null, "", "/");
    vi.unstubAllGlobals();
  });

  it("renders the Macedonian login form", () => {
    window.history.pushState(null, "", "/dashboard");

    render(<App />);

    expect(screen.getByRole("heading", { name: "Најава" })).toBeInTheDocument();
    expect(screen.getByLabelText("Е-пошта")).toBeInTheDocument();
    expect(screen.getByLabelText("Лозинка")).toBeInTheDocument();
  });

  it("redirects protected routes to login when unauthenticated", () => {
    window.history.pushState(null, "", "/customers");

    render(<App />);

    expect(screen.getByRole("heading", { name: "Најава" })).toBeInTheDocument();
    expect(window.location.pathname).toBe("/login");
  });

  it("keeps projects protected when unauthenticated", () => {
    window.history.pushState(null, "", "/projects");

    render(<App />);

    expect(screen.getByRole("heading", { name: "Најава" })).toBeInTheDocument();
    expect(window.location.pathname).toBe("/login");
  });

  it("keeps calculations protected when unauthenticated", () => {
    window.history.pushState(null, "", "/calculations");

    render(<App />);

    expect(screen.getByRole("heading", { name: "Најава" })).toBeInTheDocument();
    expect(window.location.pathname).toBe("/login");
  });

  it("keeps estimates protected when unauthenticated", () => {
    window.history.pushState(null, "", "/estimates");

    render(<App />);

    expect(screen.getByRole("heading", { name: "Најава" })).toBeInTheDocument();
    expect(window.location.pathname).toBe("/login");
  });

  it("keeps payments protected when unauthenticated", () => {
    window.history.pushState(null, "", "/payments");

    render(<App />);

    expect(screen.getByRole("heading", { name: "Најава" })).toBeInTheDocument();
    expect(window.location.pathname).toBe("/login");
  });

  it("keeps expenses protected when unauthenticated", () => {
    window.history.pushState(null, "", "/expenses");

    render(<App />);

    expect(screen.getByRole("heading", { name: "Најава" })).toBeInTheDocument();
    expect(window.location.pathname).toBe("/login");
  });

  it("stores the token and routes to the dashboard after successful login", async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);

      if (url.endsWith("/api/v1/auth/login")) {
        expect(init?.method).toBe("POST");
        expect(init?.body).toBe(JSON.stringify({ email: "aleksandar@example.com", password: "secret" }));
        return Promise.resolve(jsonResponse({ access_token: "login-token", token_type: "bearer" }));
      }

      return mockSessionFetch("login-token")(input, init);
    });
    vi.stubGlobal("fetch", fetchMock);
    window.history.pushState(null, "", "/login");

    render(<App />);

    fireEvent.change(screen.getByLabelText("Е-пошта"), {
      target: { value: "aleksandar@example.com" },
    });
    fireEvent.change(screen.getByLabelText("Лозинка"), {
      target: { value: "secret" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Најава" }));

    expect(await screen.findByRole("heading", { name: "Контролна табла" })).toBeInTheDocument();
    expect(getToken()).toBe("login-token");
    expect(window.location.pathname).toBe("/dashboard");
    expect(screen.getAllByText("Демо Градба").length).toBeGreaterThan(0);
    expect(screen.getByText(/Претплата: Активна/)).toBeInTheDocument();
  });

  it("shows company and subscription data on the dashboard when authenticated", async () => {
    vi.stubGlobal("fetch", mockSessionFetch());
    saveToken("demo-token");
    window.history.pushState(null, "", "/dashboard");

    render(<App />);

    expect(await screen.findByRole("heading", { name: "Контролна табла" })).toBeInTheDocument();
    expect(screen.getAllByText("Александар Димовски").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Демо Градба").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Статус: Активна").length).toBeGreaterThan(0);
    expect(screen.getByText("Starter")).toBeInTheDocument();
    expect(screen.getByText("Започнете со додавање клиент.")).toBeInTheDocument();
    expect(screen.getByText("Потоа креирајте проект и простории. Потоа направете пресметка и понуда.")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Клиенти" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Одјава" })).toBeInTheDocument();
  });

  it("clears the token on logout", async () => {
    vi.stubGlobal("fetch", mockSessionFetch());
    saveToken("demo-token");
    window.history.pushState(null, "", "/dashboard");

    render(<App />);

    const logoutButton = await screen.findByRole("button", { name: "Одјава" });
    fireEvent.click(logoutButton);

    await waitFor(() => expect(getToken()).toBeNull());
    expect(screen.getByRole("heading", { name: "Најава" })).toBeInTheDocument();
  });

  it("renders the customers workspace with Macedonian labels", async () => {
    vi.stubGlobal("fetch", mockCustomerPropertyFetch());
    saveToken("demo-token");
    window.history.pushState(null, "", "/customers");

    render(<App />);

    expect(await screen.findByRole("heading", { name: "Клиенти" })).toBeInTheDocument();
    expect(screen.getByLabelText("Име на клиент")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Додај клиент" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Објекти" })).toBeInTheDocument();
    expect(screen.getByLabelText("Име на објект")).toBeInTheDocument();
  });

  it("calls the backend when creating a customer", async () => {
    const fetchMock = mockCustomerPropertyFetch();
    vi.stubGlobal("fetch", fetchMock);
    saveToken("demo-token");
    window.history.pushState(null, "", "/customers");

    render(<App />);

    fireEvent.change(await screen.findByLabelText("Име на клиент"), {
      target: { value: "Петар Петров" },
    });
    fireEvent.change(screen.getByLabelText("Телефон на клиент"), {
      target: { value: "071333444" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Додај клиент" }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/customers"),
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({
            name: "Петар Петров",
            phone: "071333444",
            email: null,
            address: null,
            note: null,
          }),
        }),
      ),
    );
  });

  it("loads customer detail and contacts from the backend", async () => {
    vi.stubGlobal("fetch", mockCustomerPropertyFetch());
    saveToken("demo-token");
    window.history.pushState(null, "", "/customers");

    render(<App />);

    const customersSection = await screen.findByRole("region", { name: "Клиенти" });
    fireEvent.click(within(customersSection).getByRole("button", { name: /Ана Стојановска/ }));

    expect(await screen.findByText("Партизанска 10")).toBeInTheDocument();
    expect(screen.getAllByText("Сака понуда по соби.").length).toBeGreaterThan(0);
    expect(screen.getByText("Игор Стојановски")).toBeInTheDocument();
  });

  it("loads the properties list from the backend", async () => {
    vi.stubGlobal("fetch", mockCustomerPropertyFetch());
    saveToken("demo-token");
    window.history.pushState(null, "", "/customers");

    render(<App />);

    const propertiesSection = await screen.findByRole("region", { name: "Објекти" });

    expect(within(propertiesSection).getByText("Стан Центар")).toBeInTheDocument();
    expect(within(propertiesSection).getByText("Скопје")).toBeInTheDocument();
  });

  it("calls the backend when creating a property", async () => {
    const fetchMock = mockCustomerPropertyFetch();
    vi.stubGlobal("fetch", fetchMock);
    saveToken("demo-token");
    window.history.pushState(null, "", "/customers");

    render(<App />);

    fireEvent.change(await screen.findByLabelText("Клиент за објект"), {
      target: { value: "customer-1" },
    });
    fireEvent.change(screen.getByLabelText("Име на објект"), {
      target: { value: "Куќа Кисела Вода" },
    });
    fireEvent.change(screen.getByLabelText("Адреса на објект"), {
      target: { value: "Народни херои 5" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Додај објект" }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/properties"),
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({
            customer_id: "customer-1",
            name: "Куќа Кисела Вода",
            address: "Народни херои 5",
            city: null,
            note: null,
          }),
        }),
      ),
    );
  });

  it("renders the projects workspace with Macedonian labels and backend room values", async () => {
    vi.stubGlobal("fetch", mockProjectFetch());
    saveToken("demo-token");
    window.history.pushState(null, "", "/projects");

    render(<App />);

    expect(await screen.findByRole("heading", { name: "Проекти" })).toBeInTheDocument();
    expect(screen.getByLabelText("Име на проект")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Додај проект" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Преглед" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Задачи" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Простории" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Мерења" })).toBeInTheDocument();
    expect(await screen.findByText("Подна површина")).toBeInTheDocument();
    expect(await screen.findByText("20 m²")).toBeInTheDocument();
    expect(await screen.findByText("65.4 m²")).toBeInTheDocument();
  });

  it("calls the backend when creating and editing a project", async () => {
    const fetchMock = mockProjectFetch();
    vi.stubGlobal("fetch", fetchMock);
    saveToken("demo-token");
    window.history.pushState(null, "", "/projects");

    render(<App />);

    fireEvent.change(await screen.findByLabelText("Клиент за проект"), {
      target: { value: "customer-1" },
    });
    fireEvent.change(screen.getByLabelText("Објект за проект"), {
      target: { value: "property-1" },
    });
    fireEvent.change(screen.getByLabelText("Име на проект"), {
      target: { value: "Нова бања" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Додај проект" }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/projects"),
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({
            customer_id: "customer-1",
            property_id: "property-1",
            name: "Нова бања",
            description: null,
            address: null,
            agreed_project_price: null,
            start_date: null,
            due_date: null,
          }),
        }),
      ),
    );

    fireEvent.change(screen.getByLabelText("Име за уредување на проект"), {
      target: { value: "Реновирање стан - фаза 2" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Зачувај проект" }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/projects/project-1"),
        expect.objectContaining({
          method: "PATCH",
        }),
      ),
    );

    fireEvent.click(screen.getByRole("button", { name: "Архивирај проект" }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/projects/project-1/archive"),
        expect.objectContaining({ method: "POST" }),
      ),
    );
  });

  it("loads project detail, timeline, and task list from the backend", async () => {
    vi.stubGlobal("fetch", mockProjectFetch());
    saveToken("demo-token");
    window.history.pushState(null, "", "/projects");

    render(<App />);

    expect(await screen.findByText("Реновирање стан")).toBeInTheDocument();
    expect(screen.getByText("Активен")).toBeInTheDocument();
    expect(screen.getByText("Проектот е креиран.")).toBeInTheDocument();
    expect(screen.getByText("Демонтажа")).toBeInTheDocument();
    expect(screen.getByText("Почнато на терен.")).toBeInTheDocument();
  });

  it("displays project financial summary backend values without local totals", async () => {
    const fetchMock = mockProjectFetch();
    vi.stubGlobal("fetch", fetchMock);
    saveToken("demo-token");
    window.history.pushState(null, "", "/projects");

    render(<App />);

    expect(await screen.findByRole("heading", { name: "Финансии" })).toBeInTheDocument();
    expect(await screen.findByText("50000 MKD")).toBeInTheDocument();
    expect(screen.getByText("40000 MKD")).toBeInTheDocument();
    expect(screen.getAllByText("Прифатена понуда").length).toBeGreaterThan(0);
    expect(screen.getByText("12345 MKD")).toBeInTheDocument();
    expect(screen.getByText("6789 MKD")).toBeInTheDocument();
    expect(screen.getByText("33333 MKD")).toBeInTheDocument();
    expect(screen.getByText("9876 MKD")).toBeInTheDocument();
    expect(screen.getByText("22222 MKD")).toBeInTheDocument();
    expect(screen.getByText("Делумно платено")).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/projects/project-1/financial-summary"),
      expect.any(Object),
    );
  });

  it("calls task create, status, and archive endpoints", async () => {
    const fetchMock = mockProjectFetch();
    vi.stubGlobal("fetch", fetchMock);
    saveToken("demo-token");
    window.history.pushState(null, "", "/projects");

    render(<App />);

    fireEvent.change(await screen.findByLabelText("Наслов на задача"), {
      target: { value: "Молерисување" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Додај задача" }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/projects/project-1/tasks"),
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({
            title: "Молерисување",
            description: null,
            assigned_user_id: null,
            due_date: null,
          }),
        }),
      ),
    );

    fireEvent.change(screen.getByLabelText("Наслов за уредување на задача"), {
      target: { value: "Подготовка" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Зачувај задача" }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/tasks/task-1"),
        expect.objectContaining({
          method: "PATCH",
          body: JSON.stringify({
            title: "Подготовка",
            description: "Отстранување стар материјал.",
            assigned_user_id: null,
            due_date: "2026-07-12",
          }),
        }),
      ),
    );

    fireEvent.change(screen.getByLabelText("Статус на задача"), {
      target: { value: "active" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Промени статус" }));
    fireEvent.click(screen.getByRole("button", { name: "Архивирај задача" }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/tasks/task-1/status"),
        expect.objectContaining({ method: "POST", body: JSON.stringify({ status: "active" }) }),
      ),
    );
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/tasks/task-1/archive"),
      expect.objectContaining({ method: "POST" }),
    );
  });

  it("calls room and opening endpoints without local calculations", async () => {
    const fetchMock = mockProjectFetch();
    vi.stubGlobal("fetch", fetchMock);
    saveToken("demo-token");
    window.history.pushState(null, "", "/projects");

    render(<App />);

    fireEvent.change(await screen.findByLabelText("Име на просторија"), {
      target: { value: "Спална соба" },
    });
    fireEvent.change(screen.getByLabelText("Тип на просторија"), {
      target: { value: "bedroom" },
    });
    fireEvent.change(screen.getByLabelText("Должина"), {
      target: { value: "4" },
    });
    fireEvent.change(screen.getByLabelText("Ширина"), {
      target: { value: "3" },
    });
    fireEvent.change(screen.getByLabelText("Висина"), {
      target: { value: "2.6" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Додај просторија" }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/projects/project-1/rooms"),
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({
            name: "Спална соба",
            room_type: "bedroom",
            project_task_id: null,
            floor: null,
            note: null,
            length: 4,
            width: 3,
            height: 2.6,
          }),
        }),
      ),
    );

    fireEvent.change(screen.getByLabelText("Име за уредување на просторија"), {
      target: { value: "Голема дневна соба" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Зачувај просторија" }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/rooms/room-1"),
        expect.objectContaining({
          method: "PATCH",
        }),
      ),
    );

    fireEvent.change(screen.getByLabelText("Име на отвор"), {
      target: { value: "Прозорец" },
    });
    fireEvent.change(screen.getByLabelText("Тип на отвор"), {
      target: { value: "window" },
    });
    fireEvent.change(screen.getByLabelText("Ширина на отвор"), {
      target: { value: "1.2" },
    });
    fireEvent.change(screen.getByLabelText("Висина на отвор"), {
      target: { value: "1.4" },
    });
    fireEvent.change(screen.getByLabelText("Количина на отвори"), {
      target: { value: "2" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Додај отвор" }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/rooms/room-1/openings"),
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({
            opening_type: "window",
            name: "Прозорец",
            width: 1.2,
            height: 1.4,
            quantity: 2,
            note: null,
          }),
        }),
      ),
    );

    fireEvent.change(screen.getByLabelText("Име за уредување на отвор"), {
      target: { value: "Влезна врата" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Зачувај отвор" }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/openings/opening-1"),
        expect.objectContaining({ method: "PATCH" }),
      ),
    );

    fireEvent.click(screen.getByRole("button", { name: "Архивирај отвор" }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/openings/opening-1/archive"),
        expect.objectContaining({ method: "POST" }),
      ),
    );

    fireEvent.click(screen.getByRole("button", { name: "Архивирај просторија" }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/rooms/room-1/archive"),
        expect.objectContaining({ method: "POST" }),
      ),
    );
  });

  it("calls measurement set and item endpoints", async () => {
    const fetchMock = mockProjectFetch();
    vi.stubGlobal("fetch", fetchMock);
    saveToken("demo-token");
    window.history.pushState(null, "", "/projects");

    render(<App />);

    fireEvent.change(await screen.findByLabelText("Име на сет"), {
      target: { value: "Дополнителни мерења" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Додај сет" }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/projects/project-1/measurement-sets"),
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({
            name: "Дополнителни мерења",
            description: null,
            project_task_id: null,
          }),
        }),
      ),
    );

    fireEvent.change(screen.getByLabelText("Име на мерка"), {
      target: { value: "Лепак" },
    });
    fireEvent.change(screen.getByLabelText("Единица"), {
      target: { value: "bag" },
    });
    fireEvent.change(screen.getByLabelText("Количина"), {
      target: { value: "5" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Додај мерка" }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/measurement-sets/measurement-set-1/items"),
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({
            name: "Лепак",
            unit: "bag",
            quantity: 5,
            note: null,
          }),
        }),
      ),
    );

    fireEvent.change(screen.getByLabelText("Количина за уредување"), {
      target: { value: "60" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Зачувај мерка" }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/measurement-items/measurement-item-1"),
        expect.objectContaining({
          method: "PATCH",
          body: JSON.stringify({
            name: "Ѕидна површина",
            unit: "m2",
            quantity: 60,
            note: null,
          }),
        }),
      ),
    );

    fireEvent.click(screen.getByRole("button", { name: "Архивирај мерка" }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/measurement-items/measurement-item-1/archive"),
        expect.objectContaining({ method: "POST" }),
      ),
    );
  });

  it("renders the calculations workspace with Macedonian labels and engine states", async () => {
    vi.stubGlobal("fetch", mockCalculationFetch());
    saveToken("demo-token");
    window.history.pushState(null, "", "/calculations");

    render(<App />);

    expect(await screen.findByRole("heading", { name: "Пресметки" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Бојадисување" })).toBeInTheDocument();
    expect(screen.getByLabelText("Проект за пресметка")).toBeInTheDocument();
    expect(screen.getByLabelText("Вклучи ѕидови")).toBeInTheDocument();
    expect(screen.getByLabelText("Вклучи таван")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Стартувај пресметка" })).toBeInTheDocument();
    expect(screen.getAllByText("Бојадисување").length).toBeGreaterThanOrEqual(1);
    expect(await screen.findByText("Имплементирано")).toBeInTheDocument();
    expect((await screen.findAllByText("Во подготовка")).length).toBeGreaterThanOrEqual(2);
    expect((await screen.findAllByText("Завршена")).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("Неуспешна")).toBeInTheDocument();
  });

  it("submits the painting calculation payload to the backend", async () => {
    const fetchMock = mockCalculationFetch();
    vi.stubGlobal("fetch", fetchMock);
    saveToken("demo-token");
    window.history.pushState(null, "", "/calculations");

    render(<App />);

    fireEvent.change(await screen.findByLabelText("Проект за пресметка"), {
      target: { value: "project-1" },
    });
    fireEvent.change(await screen.findByLabelText("Задача (незадолжително)"), {
      target: { value: "task-1" },
    });
    fireEvent.change(screen.getByLabelText("Просторија (незадолжително)"), {
      target: { value: "room-1" },
    });
    fireEvent.change(screen.getByLabelText("Сет мерења (незадолжително)"), {
      target: { value: "measurement-set-1" },
    });
    fireEvent.change(screen.getByLabelText("Слоеви боја"), {
      target: { value: "2" },
    });
    fireEvent.change(screen.getByLabelText("Прајмер слоеви"), {
      target: { value: "1" },
    });
    fireEvent.change(screen.getByLabelText("Материјал за боја"), {
      target: { value: "material-paint-1" },
    });
    fireEvent.change(screen.getByLabelText("Прајмер материјал"), {
      target: { value: "material-primer-1" },
    });
    fireEvent.change(screen.getByLabelText("Отпад (%)"), {
      target: { value: "10" },
    });
    fireEvent.change(screen.getByLabelText("Работна цена по m²"), {
      target: { value: "120" },
    });
    fireEvent.change(screen.getByLabelText("Белешки"), {
      target: { value: "Проверка на дневна соба." },
    });
    fireEvent.click(screen.getByRole("button", { name: "Стартувај пресметка" }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/calculations/run"),
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({
            engine_type: "painting",
            project_id: "project-1",
            project_task_id: "task-1",
            room_id: "room-1",
            measurement_set_id: "measurement-set-1",
            input_payload: {
              include_walls: true,
              include_ceiling: true,
              coats: 2,
              primer_coats: 1,
              paint_material_id: "material-paint-1",
              primer_material_id: "material-primer-1",
              waste_percentage: 10,
              labor_rate_per_m2: 120,
              notes: "Проверка на дневна соба.",
            },
          }),
        }),
      ),
    );
    expect(await screen.findByText("Пресметката е стартувана.")).toBeInTheDocument();
  });

  it("displays backend calculation output values and line items without local totals", async () => {
    vi.stubGlobal("fetch", mockCalculationFetch());
    saveToken("demo-token");
    window.history.pushState(null, "", "/calculations");

    render(<App />);

    expect(await screen.findByText("Избрана површина")).toBeInTheDocument();
    expect(screen.getAllByText("65.4 m²").length).toBeGreaterThanOrEqual(2);
    expect(screen.getByText("45.4 m²")).toBeInTheDocument();
    expect(screen.getByText("14.388 l")).toBeInTheDocument();
    expect(screen.getByText("7.194 l")).toBeInTheDocument();
    expect(screen.getAllByText("5100.12 MKD").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("1200.34 MKD").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("7848 MKD").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("22222.22 MKD")).toBeInTheDocument();
    expect(screen.getByText("Room-computed areas were used.")).toBeInTheDocument();
    expect(screen.getByText("Не е пронајдена цена за прајмер материјалот.")).toBeInTheDocument();
    expect(screen.getByText("Paint material")).toBeInTheDocument();
    expect(screen.getAllByText("Мат боја").length).toBeGreaterThanOrEqual(1);
  });

  it("renders the estimates workspace with Macedonian labels and backend list data", async () => {
    vi.stubGlobal("fetch", mockEstimateFetch());
    saveToken("demo-token");
    window.history.pushState(null, "", "/estimates");

    render(<App />);

    expect(await screen.findByRole("heading", { name: "Понуди" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Нова понуда" })).toBeInTheDocument();
    expect(screen.getByLabelText("Проект за понуда")).toBeInTheDocument();
    expect(screen.getByLabelText("Наслов на понуда")).toBeInTheDocument();
    expect((await screen.findAllByText("Понуда за бојадисување")).length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("Ана Стојановска").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Реновирање стан").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Нацрт").length).toBeGreaterThan(0);
    expect((await screen.findAllByText("28500 MKD")).length).toBeGreaterThanOrEqual(1);
  });

  it("calls the backend when creating a manual estimate", async () => {
    const fetchMock = mockEstimateFetch();
    vi.stubGlobal("fetch", fetchMock);
    saveToken("demo-token");
    window.history.pushState(null, "", "/estimates");

    render(<App />);

    const createSection = await screen.findByRole("region", { name: "Нова понуда" });
    fireEvent.change(within(createSection).getByLabelText("Проект за понуда"), {
      target: { value: "project-1" },
    });
    fireEvent.change(within(createSection).getByLabelText("Наслов на понуда"), {
      target: { value: "Рачна понуда" },
    });
    fireEvent.change(within(createSection).getByLabelText("Опис на понуда"), {
      target: { value: "Понуда за дневна соба." },
    });
    fireEvent.click(within(createSection).getByRole("button", { name: "Креирај понуда" }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/estimates"),
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({
            project_id: "project-1",
            customer_id: null,
            property_id: null,
            title: "Рачна понуда",
            description: "Понуда за дневна соба.",
          }),
        }),
      ),
    );
  });

  it("calls the backend when creating an estimate from a calculation", async () => {
    const fetchMock = mockEstimateFetch();
    vi.stubGlobal("fetch", fetchMock);
    saveToken("demo-token");
    window.history.pushState(null, "", "/estimates");

    render(<App />);

    const calculationSection = await screen.findByRole("region", { name: "Понуда од пресметка" });
    fireEvent.change(within(calculationSection).getByLabelText("Пресметка за понуда"), {
      target: { value: "calculation-1" },
    });
    fireEvent.change(within(calculationSection).getByLabelText("Наслов од пресметка"), {
      target: { value: "Понуда од пресметка" },
    });
    fireEvent.click(within(calculationSection).getByRole("button", { name: "Креирај од пресметка" }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/estimates/from-calculation/calculation-1"),
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({
            title: "Понуда од пресметка",
            description: null,
          }),
        }),
      ),
    );
  });

  it("creates an estimate from the painting calculation detail action", async () => {
    const fetchMock = mockCalculationFetch();
    vi.stubGlobal("fetch", fetchMock);
    saveToken("demo-token");
    window.history.pushState(null, "", "/calculations");

    render(<App />);

    fireEvent.click(await screen.findByRole("button", { name: "Креирај понуда" }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/estimates/from-calculation/calculation-1"),
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({
            title: null,
            description: null,
          }),
        }),
      ),
    );
  });

  it("displays estimate detail backend totals without local calculation", async () => {
    vi.stubGlobal("fetch", mockEstimateFetch());
    saveToken("demo-token");
    window.history.pushState(null, "", "/estimates");

    render(<App />);

    expect(await screen.findByText("Меѓузбир")).toBeInTheDocument();
    expect(screen.getByText("30000 MKD")).toBeInTheDocument();
    expect(screen.getByText("2000 MKD")).toBeInTheDocument();
    expect(screen.getByText("500 MKD")).toBeInTheDocument();
    expect(screen.getByText("0 MKD")).toBeInTheDocument();
    expect(screen.getAllByText("28500 MKD").length).toBeGreaterThanOrEqual(2);
    expect(screen.getAllByText("Мат боја").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("3000 MKD").length).toBeGreaterThanOrEqual(1);
  });

  it("shows the estimate PDF generation button", async () => {
    vi.stubGlobal("fetch", mockEstimateFetch());
    saveToken("demo-token");
    window.history.pushState(null, "", "/estimates");

    render(<App />);

    const detailSection = await screen.findByRole("region", { name: "Детали за понуда" });

    expect(within(detailSection).getByRole("button", { name: "Генерирај PDF понуда" })).toBeInTheDocument();
  });

  it("generates a PDF through the backend and displays the returned document", async () => {
    const fetchMock = mockEstimateFetch();
    vi.stubGlobal("fetch", fetchMock);
    saveToken("demo-token");
    window.history.pushState(null, "", "/estimates");

    render(<App />);

    fireEvent.click(await screen.findByRole("button", { name: "Генерирај PDF понуда" }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/estimates/estimate-1/pdf"),
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({ revision_id: "revision-1" }),
        }),
      ),
    );
    expect(await screen.findByText("PDF понудата е генерирана.")).toBeInTheDocument();
    expect(screen.getByText("Генерирани PDF документи")).toBeInTheDocument();
    expect(screen.getByText("PDF понуда")).toBeInTheDocument();
    expect(
      screen.getByText(new Intl.DateTimeFormat("mk-MK", { dateStyle: "medium", timeStyle: "short" }).format(new Date(estimateDocument.generated_at))),
    ).toBeInTheDocument();

    const pdfRequest = fetchMock.mock.calls.find((call) => String(call[0]).endsWith("/api/v1/estimates/estimate-1/pdf"));
    expect(String(pdfRequest?.[1]?.body)).not.toContain("total");
  });

  it("downloads the generated PDF from the backend document endpoint", async () => {
    const fetchMock = mockEstimateFetch();
    const createObjectUrl = vi.fn(() => "blob:buildiq-pdf");
    const revokeObjectUrl = vi.fn();
    const anchorClick = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => undefined);
    Object.defineProperty(URL, "createObjectURL", { value: createObjectUrl, configurable: true });
    Object.defineProperty(URL, "revokeObjectURL", { value: revokeObjectUrl, configurable: true });
    vi.stubGlobal("fetch", fetchMock);
    saveToken("demo-token");
    window.history.pushState(null, "", "/estimates");

    render(<App />);

    fireEvent.click(await screen.findByRole("button", { name: "Генерирај PDF понуда" }));
    fireEvent.click(await screen.findByRole("button", { name: "Преземи PDF" }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/estimate-documents/document-1/download"),
        expect.objectContaining({ method: "GET" }),
      ),
    );
    expect(createObjectUrl).toHaveBeenCalled();
    expect(anchorClick).toHaveBeenCalled();
    expect(revokeObjectUrl).toHaveBeenCalledWith("blob:buildiq-pdf");
  });

  it("shows a Macedonian error when PDF generation is rejected", async () => {
    vi.stubGlobal("fetch", mockEstimateFetch("demo-token", { pdfError: true }));
    saveToken("demo-token");
    window.history.pushState(null, "", "/estimates");

    render(<App />);

    fireEvent.click(await screen.findByRole("button", { name: "Генерирај PDF понуда" }));

    expect(await screen.findByText("Не може да се генерира PDF за архивирана понуда.")).toBeInTheDocument();
  });

  it("calls item create, edit, and archive estimate APIs", async () => {
    const fetchMock = mockEstimateFetch();
    vi.stubGlobal("fetch", fetchMock);
    saveToken("demo-token");
    window.history.pushState(null, "", "/estimates");

    render(<App />);

    fireEvent.change(await screen.findByLabelText("Тип на ставка"), {
      target: { value: "service" },
    });
    fireEvent.change(screen.getByLabelText("Име на ставка"), {
      target: { value: "Дополнителна услуга" },
    });
    fireEvent.change(screen.getByLabelText("Количина на ставка"), {
      target: { value: "2" },
    });
    fireEvent.change(screen.getByLabelText("Единица на ставка"), {
      target: { value: "hour" },
    });
    fireEvent.change(screen.getByLabelText("Единечна цена"), {
      target: { value: "1500" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Додај ставка" }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/estimate-revisions/revision-1/items"),
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({
            item_type: "service",
            name: "Дополнителна услуга",
            description: null,
            material_id: null,
            quantity: 2,
            unit: "hour",
            unit_price: 1500,
          }),
        }),
      ),
    );

    fireEvent.change(screen.getByLabelText("Име за уредување на ставка"), {
      target: { value: "Мат боја премиум" },
    });
    fireEvent.change(screen.getByLabelText("Количина за уредување на ставка"), {
      target: { value: "12" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Зачувај ставка" }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/estimate-items/estimate-item-1"),
        expect.objectContaining({
          method: "PATCH",
          body: JSON.stringify({
            item_type: "material",
            name: "Мат боја премиум",
            description: "Боја од пресметка.",
            material_id: "material-paint-1",
            quantity: 12,
            unit: "liter",
            unit_price: 300,
          }),
        }),
      ),
    );

    fireEvent.click(screen.getByRole("button", { name: "Архивирај ставка" }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/estimate-items/estimate-item-1/archive"),
        expect.objectContaining({ method: "POST" }),
      ),
    );
  });

  it("calls estimate status and archive APIs", async () => {
    const fetchMock = mockEstimateFetch();
    vi.stubGlobal("fetch", fetchMock);
    saveToken("demo-token");
    window.history.pushState(null, "", "/estimates");

    render(<App />);

    fireEvent.click(await screen.findByRole("button", { name: "Означи како испратена" }));
    fireEvent.click(screen.getByRole("button", { name: "Означи како прифатена" }));
    fireEvent.click(screen.getByRole("button", { name: "Означи како одбиена" }));
    fireEvent.click(screen.getByRole("button", { name: "Архивирај понуда" }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/estimates/estimate-1/status"),
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({ status: "sent" }),
        }),
      ),
    );
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/estimates/estimate-1/status"),
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ status: "accepted" }),
      }),
    );
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/estimates/estimate-1/status"),
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ status: "rejected" }),
      }),
    );
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/estimates/estimate-1/archive"),
      expect.objectContaining({ method: "POST" }),
    );
  });

  it("renders the payments workspace with Macedonian labels and backend data", async () => {
    vi.stubGlobal("fetch", mockFinancialFetch());
    saveToken("demo-token");
    window.history.pushState(null, "", "/payments");

    render(<App />);

    expect(await screen.findByRole("heading", { name: "Уплати" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Нова уплата" })).toBeInTheDocument();
    expect(screen.getByLabelText("Клиент за уплата")).toBeInTheDocument();
    expect(screen.getByLabelText("Проект за уплата")).toBeInTheDocument();
    expect(screen.getByLabelText("Начин на плаќање")).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "Кеш" })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "Банкарски трансфер" })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "Картичка" })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "Друго" })).toBeInTheDocument();
    expect((await screen.findAllByText("20000 MKD")).length).toBeGreaterThan(0);
    expect(screen.getAllByText("Банкарски трансфер").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Примена").length).toBeGreaterThan(0);
  });

  it("calls payment create, reverse, and archive APIs", async () => {
    const fetchMock = mockFinancialFetch();
    vi.stubGlobal("fetch", fetchMock);
    vi.stubGlobal("confirm", vi.fn(() => true));
    saveToken("demo-token");
    window.history.pushState(null, "", "/payments");

    render(<App />);

    const createSection = await screen.findByRole("region", { name: "Нова уплата" });
    fireEvent.change(within(createSection).getByLabelText("Клиент за уплата"), {
      target: { value: "customer-1" },
    });
    fireEvent.change(within(createSection).getByLabelText("Проект за уплата"), {
      target: { value: "project-1" },
    });
    fireEvent.change(within(createSection).getByLabelText("Понуда за уплата"), {
      target: { value: "estimate-1" },
    });
    fireEvent.change(within(createSection).getByLabelText("Износ на уплата"), {
      target: { value: "15000" },
    });
    fireEvent.change(within(createSection).getByLabelText("Начин на плаќање"), {
      target: { value: "cash" },
    });
    fireEvent.change(within(createSection).getByLabelText("Датум на уплата"), {
      target: { value: "2026-07-09" },
    });
    fireEvent.change(within(createSection).getByLabelText("Белешка за уплата"), {
      target: { value: "Втора уплата." },
    });
    fireEvent.click(within(createSection).getByRole("button", { name: "Додај уплата" }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/payments"),
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({
            customer_id: "customer-1",
            project_id: "project-1",
            estimate_id: "estimate-1",
            amount: 15000,
            payment_method: "cash",
            payment_date: "2026-07-09",
            status: "received",
            note: "Втора уплата.",
            allocations: [],
          }),
        }),
      ),
    );

    fireEvent.change(screen.getByLabelText("Причина за сторно уплата"), {
      target: { value: "Погрешна уплата." },
    });
    fireEvent.click(screen.getByRole("button", { name: "Сторнирај уплата" }));
    fireEvent.click(screen.getByRole("button", { name: "Архивирај уплата" }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/payments/payment-1/reverse"),
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({ reason: "Погрешна уплата." }),
        }),
      ),
    );
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/payments/payment-1/archive"),
      expect.objectContaining({ method: "POST" }),
    );
  });

  it("renders the expenses workspace with Macedonian labels and backend data", async () => {
    vi.stubGlobal("fetch", mockFinancialFetch());
    saveToken("demo-token");
    window.history.pushState(null, "", "/expenses");

    render(<App />);

    expect(await screen.findByRole("heading", { name: "Трошоци" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Категории на трошоци" })).toBeInTheDocument();
    expect(screen.getByLabelText("Име на категорија")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Нов трошок" })).toBeInTheDocument();
    expect(screen.getByLabelText("Опис на трошок")).toBeInTheDocument();
    expect(screen.getByLabelText("Начин на плаќање за трошок")).toBeInTheDocument();
    expect(screen.getAllByText("Материјали").length).toBeGreaterThan(0);
    expect((await screen.findAllByText("Купена боја")).length).toBeGreaterThan(0);
    expect(screen.getAllByText("12000 MKD").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Картичка").length).toBeGreaterThan(0);
  });

  it("calls expense category create, edit, and archive APIs", async () => {
    const fetchMock = mockFinancialFetch();
    vi.stubGlobal("fetch", fetchMock);
    vi.stubGlobal("confirm", vi.fn(() => true));
    saveToken("demo-token");
    window.history.pushState(null, "", "/expenses");

    render(<App />);

    const categorySection = await screen.findByRole("region", { name: "Категории на трошоци" });
    fireEvent.change(within(categorySection).getByLabelText("Име на категорија"), {
      target: { value: "Транспорт" },
    });
    fireEvent.click(within(categorySection).getByRole("button", { name: "Додај категорија" }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/expense-categories"),
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({
            name: "Транспорт",
            description: null,
          }),
        }),
      ),
    );

    fireEvent.click(within(categorySection).getByRole("button", { name: /Материјали/ }));
    fireEvent.change(screen.getByLabelText("Име за уредување на категорија"), {
      target: { value: "Материјали и алат" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Зачувај категорија" }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/expense-categories/expense-category-1"),
        expect.objectContaining({
          method: "PATCH",
          body: JSON.stringify({
            name: "Материјали и алат",
            description: "Трошоци за материјали.",
          }),
        }),
      ),
    );

    fireEvent.click(screen.getByRole("button", { name: "Архивирај категорија" }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/expense-categories/expense-category-1/archive"),
        expect.objectContaining({ method: "POST" }),
      ),
    );
  });

  it("calls expense create, reverse, and archive APIs", async () => {
    const fetchMock = mockFinancialFetch();
    vi.stubGlobal("fetch", fetchMock);
    vi.stubGlobal("confirm", vi.fn(() => true));
    saveToken("demo-token");
    window.history.pushState(null, "", "/expenses");

    render(<App />);

    const expenseSection = await screen.findByRole("region", { name: "Нов трошок" });
    fireEvent.change(within(expenseSection).getByLabelText("Проект за трошок"), {
      target: { value: "project-1" },
    });
    fireEvent.change(within(expenseSection).getByLabelText("Категорија за трошок"), {
      target: { value: "expense-category-2" },
    });
    fireEvent.change(within(expenseSection).getByLabelText("Опис на трошок"), {
      target: { value: "Превоз на материјали" },
    });
    fireEvent.change(within(expenseSection).getByLabelText("Износ на трошок"), {
      target: { value: "3000" },
    });
    fireEvent.change(within(expenseSection).getByLabelText("Датум на трошок"), {
      target: { value: "2026-07-09" },
    });
    fireEvent.change(within(expenseSection).getByLabelText("Начин на плаќање за трошок"), {
      target: { value: "cash" },
    });
    fireEvent.click(within(expenseSection).getByRole("button", { name: "Додај трошок" }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/expenses"),
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({
            project_id: "project-1",
            category_id: "expense-category-2",
            supplier_id: null,
            material_id: null,
            description: "Превоз на материјали",
            amount: 3000,
            expense_date: "2026-07-09",
            payment_method: "cash",
            status: "recorded",
            note: null,
          }),
        }),
      ),
    );

    fireEvent.change(screen.getByLabelText("Причина за сторно трошок"), {
      target: { value: "Погрешен трошок." },
    });
    fireEvent.click(screen.getByRole("button", { name: "Сторнирај трошок" }));
    fireEvent.click(screen.getByRole("button", { name: "Архивирај трошок" }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/expenses/expense-1/reverse"),
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({ reason: "Погрешен трошок." }),
        }),
      ),
    );
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/expenses/expense-1/archive"),
      expect.objectContaining({ method: "POST" }),
    );
  });
});
