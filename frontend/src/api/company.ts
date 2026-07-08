import { apiRequest } from "./client";
import type { CompanyResponse } from "./types";

export function getCurrentCompany(token?: string | null): Promise<CompanyResponse> {
  return apiRequest<CompanyResponse>("/api/v1/companies/me", { token });
}
