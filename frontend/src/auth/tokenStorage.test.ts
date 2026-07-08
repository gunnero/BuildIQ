import { afterEach, describe, expect, it } from "vitest";

import { clearToken, getToken, saveToken } from "./tokenStorage";

describe("tokenStorage", () => {
  afterEach(() => {
    localStorage.clear();
  });

  it("stores, reads, and clears the authentication token", () => {
    expect(getToken()).toBeNull();

    saveToken("demo-token");

    expect(getToken()).toBe("demo-token");

    clearToken();

    expect(getToken()).toBeNull();
  });
});
