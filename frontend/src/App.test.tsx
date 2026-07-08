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
});
