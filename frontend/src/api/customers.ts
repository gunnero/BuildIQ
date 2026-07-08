import { apiRequest } from "./client";
import type {
  ContactCreateRequest,
  CustomerContactResponse,
  CustomerCreateRequest,
  CustomerResponse,
  CustomerUpdateRequest,
} from "./types";

export function listCustomers(): Promise<CustomerResponse[]> {
  return apiRequest<CustomerResponse[]>("/api/v1/customers");
}

export function createCustomer(payload: CustomerCreateRequest): Promise<CustomerResponse> {
  return apiRequest<CustomerResponse>("/api/v1/customers", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getCustomer(customerId: string): Promise<CustomerResponse> {
  return apiRequest<CustomerResponse>(`/api/v1/customers/${customerId}`);
}

export function updateCustomer(customerId: string, payload: CustomerUpdateRequest): Promise<CustomerResponse> {
  return apiRequest<CustomerResponse>(`/api/v1/customers/${customerId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function archiveCustomer(customerId: string): Promise<CustomerResponse> {
  return apiRequest<CustomerResponse>(`/api/v1/customers/${customerId}/archive`, {
    method: "POST",
  });
}

export function listCustomerContacts(customerId: string): Promise<CustomerContactResponse[]> {
  return apiRequest<CustomerContactResponse[]>(`/api/v1/customers/${customerId}/contacts`);
}

export function createCustomerContact(
  customerId: string,
  payload: ContactCreateRequest,
): Promise<CustomerContactResponse> {
  return apiRequest<CustomerContactResponse>(`/api/v1/customers/${customerId}/contacts`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
