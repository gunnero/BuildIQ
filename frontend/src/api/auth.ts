import { apiRequest } from "./client";
import type { CurrentUserResponse, LoginRequest, TokenResponse } from "./types";

export function loginRequest(payload: LoginRequest): Promise<TokenResponse> {
  return apiRequest<TokenResponse>("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
    token: null,
  });
}

export function getCurrentUser(token?: string | null): Promise<CurrentUserResponse> {
  return apiRequest<CurrentUserResponse>("/api/v1/auth/me", { token });
}
