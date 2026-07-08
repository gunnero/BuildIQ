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
});
