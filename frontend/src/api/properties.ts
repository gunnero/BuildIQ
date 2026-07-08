import { apiRequest } from "./client";
import type {
  ContactCreateRequest,
  PropertyContactResponse,
  PropertyCreateRequest,
  PropertyNoteCreateRequest,
  PropertyNoteResponse,
  PropertyResponse,
  PropertyUpdateRequest,
} from "./types";

export function listProperties(): Promise<PropertyResponse[]> {
  return apiRequest<PropertyResponse[]>("/api/v1/properties");
}

export function createProperty(payload: PropertyCreateRequest): Promise<PropertyResponse> {
  return apiRequest<PropertyResponse>("/api/v1/properties", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getProperty(propertyId: string): Promise<PropertyResponse> {
  return apiRequest<PropertyResponse>(`/api/v1/properties/${propertyId}`);
}

export function updateProperty(propertyId: string, payload: PropertyUpdateRequest): Promise<PropertyResponse> {
  return apiRequest<PropertyResponse>(`/api/v1/properties/${propertyId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function archiveProperty(propertyId: string): Promise<PropertyResponse> {
  return apiRequest<PropertyResponse>(`/api/v1/properties/${propertyId}/archive`, {
    method: "POST",
  });
}

export function listPropertyContacts(propertyId: string): Promise<PropertyContactResponse[]> {
  return apiRequest<PropertyContactResponse[]>(`/api/v1/properties/${propertyId}/contacts`);
}

export function createPropertyContact(
  propertyId: string,
  payload: ContactCreateRequest,
): Promise<PropertyContactResponse> {
  return apiRequest<PropertyContactResponse>(`/api/v1/properties/${propertyId}/contacts`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function listPropertyNotes(propertyId: string): Promise<PropertyNoteResponse[]> {
  return apiRequest<PropertyNoteResponse[]>(`/api/v1/properties/${propertyId}/notes`);
}

export function createPropertyNote(
  propertyId: string,
  payload: PropertyNoteCreateRequest,
): Promise<PropertyNoteResponse> {
  return apiRequest<PropertyNoteResponse>(`/api/v1/properties/${propertyId}/notes`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
