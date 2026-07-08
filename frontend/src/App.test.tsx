import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
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
});
