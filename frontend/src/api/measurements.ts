import { apiRequest } from "./client";
import type {
  MeasurementItemCreateRequest,
  MeasurementItemResponse,
  MeasurementItemUpdateRequest,
  MeasurementSetCreateRequest,
  MeasurementSetResponse,
} from "./types";

export function listMeasurementSets(projectId: string): Promise<MeasurementSetResponse[]> {
  return apiRequest<MeasurementSetResponse[]>(`/api/v1/projects/${projectId}/measurement-sets`);
}

export function createMeasurementSet(
  projectId: string,
  payload: MeasurementSetCreateRequest,
): Promise<MeasurementSetResponse> {
  return apiRequest<MeasurementSetResponse>(`/api/v1/projects/${projectId}/measurement-sets`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getMeasurementSet(measurementSetId: string): Promise<MeasurementSetResponse> {
  return apiRequest<MeasurementSetResponse>(`/api/v1/measurement-sets/${measurementSetId}`);
}

export function listMeasurementItems(measurementSetId: string): Promise<MeasurementItemResponse[]> {
  return apiRequest<MeasurementItemResponse[]>(`/api/v1/measurement-sets/${measurementSetId}/items`);
}

export function createMeasurementItem(
  measurementSetId: string,
  payload: MeasurementItemCreateRequest,
): Promise<MeasurementItemResponse> {
  return apiRequest<MeasurementItemResponse>(`/api/v1/measurement-sets/${measurementSetId}/items`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateMeasurementItem(
  measurementItemId: string,
  payload: MeasurementItemUpdateRequest,
): Promise<MeasurementItemResponse> {
  return apiRequest<MeasurementItemResponse>(`/api/v1/measurement-items/${measurementItemId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function archiveMeasurementItem(measurementItemId: string): Promise<MeasurementItemResponse> {
  return apiRequest<MeasurementItemResponse>(`/api/v1/measurement-items/${measurementItemId}/archive`, {
    method: "POST",
  });
}
