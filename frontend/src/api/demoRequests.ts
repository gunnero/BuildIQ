import { apiRequest } from "./client";

export type DemoRequestInput = {
  name: string;
  email: string;
  company_name: string;
  message: string;
};

export type DemoRequest = DemoRequestInput & {
  id: string;
  created_at: string;
  approved_at: string | null;
  activated_at: string | null;
  invitation_sent_at: string | null;
};

const endpoint = "/api/v1/demo-requests";

export const demoAvailability = () =>
  apiRequest<{ enabled: boolean }>(endpoint + "/availability", { token: null });

export const submitDemoRequest = (input: DemoRequestInput) =>
  apiRequest<null>(endpoint, { method: "POST", body: JSON.stringify(input), token: null });

export const activateDemo = (input: { token: string; password: string }) =>
  apiRequest<{ email: string }>(endpoint + "/activate", {
    method: "POST", body: JSON.stringify(input), token: null,
  });

export const listDemoRequests = (state: "pending" | "approved", offset: number, limit: number) =>
  apiRequest<DemoRequest[]>(endpoint + `?state=${state}&offset=${offset}&limit=${limit}`);

export const getDemoRequest = (id: string) =>
  apiRequest<DemoRequest>(endpoint + "/" + encodeURIComponent(id));

export const approveDemoRequest = (id: string) =>
  apiRequest<DemoRequest>(endpoint + "/" + encodeURIComponent(id) + "/approve", { method: "POST" });
