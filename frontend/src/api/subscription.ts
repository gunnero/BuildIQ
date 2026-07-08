import { apiRequest } from "./client";
import type { SubscriptionResponse } from "./types";

export function getCurrentSubscription(token?: string | null): Promise<SubscriptionResponse> {
  return apiRequest<SubscriptionResponse>("/api/v1/subscription/me", { token });
}
