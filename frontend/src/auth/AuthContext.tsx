import { useMemo, useState, type ReactNode } from "react";

import { apiRequest } from "../api/client";
import { AuthContext, type AuthContextValue } from "./authContextValue";
import { clearToken, getToken, saveToken } from "./tokenStorage";

type TokenResponse = {
  access_token: string;
  token_type: string;
};

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => getToken());

  const value = useMemo<AuthContextValue>(
    () => ({
      token,
      isAuthenticated: Boolean(token),
      async login(payload) {
        const response = await apiRequest<TokenResponse>("/api/v1/auth/login", {
          method: "POST",
          body: JSON.stringify(payload),
          token: null,
        });
        saveToken(response.access_token);
        setToken(response.access_token);
      },
      logout() {
        clearToken();
        setToken(null);
      },
    }),
    [token],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
