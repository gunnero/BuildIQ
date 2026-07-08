import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import { App } from "./App";
import { saveToken } from "./auth/tokenStorage";

describe("App", () => {
  afterEach(() => {
    localStorage.clear();
    window.history.pushState(null, "", "/");
  });

  it("shows the Macedonian login page when unauthenticated", () => {
    window.history.pushState(null, "", "/dashboard");

    render(<App />);

    expect(screen.getByRole("heading", { name: "Најава" })).toBeInTheDocument();
    expect(screen.getByLabelText("Е-пошта")).toBeInTheDocument();
    expect(screen.getByLabelText("Лозинка")).toBeInTheDocument();
  });

  it("shows the protected Macedonian app shell when authenticated", () => {
    saveToken("demo-token");
    window.history.pushState(null, "", "/dashboard");

    render(<App />);

    expect(screen.getByRole("heading", { name: "Контролна табла" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Клиенти" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Одјава" })).toBeInTheDocument();
  });
});
