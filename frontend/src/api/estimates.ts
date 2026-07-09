import { apiBlobRequest, apiRequest } from "./client";
import type {
  EstimateCreateRequest,
  EstimateDocumentResponse,
  EstimateFromCalculationCreateRequest,
  EstimateItemCreateRequest,
  EstimateItemResponse,
  EstimateItemUpdateRequest,
  EstimatePdfCreateRequest,
  EstimateResponse,
  EstimateRevisionResponse,
  EstimateStatusUpdateRequest,
} from "./types";

export function listEstimates(): Promise<EstimateResponse[]> {
  return apiRequest<EstimateResponse[]>("/api/v1/estimates");
}

export function createEstimate(payload: EstimateCreateRequest): Promise<EstimateResponse> {
  return apiRequest<EstimateResponse>("/api/v1/estimates", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function createEstimateFromCalculation(
  calculationRunId: string,
  payload: EstimateFromCalculationCreateRequest,
): Promise<EstimateResponse> {
  return apiRequest<EstimateResponse>(`/api/v1/estimates/from-calculation/${calculationRunId}`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function changeEstimateStatus(
  estimateId: string,
  payload: EstimateStatusUpdateRequest,
): Promise<EstimateResponse> {
  return apiRequest<EstimateResponse>(`/api/v1/estimates/${estimateId}/status`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function archiveEstimate(estimateId: string): Promise<EstimateResponse> {
  return apiRequest<EstimateResponse>(`/api/v1/estimates/${estimateId}/archive`, {
    method: "POST",
  });
}

export function generateEstimatePdf(
  estimateId: string,
  payload: EstimatePdfCreateRequest,
): Promise<EstimateDocumentResponse> {
  return apiRequest<EstimateDocumentResponse>(`/api/v1/estimates/${estimateId}/pdf`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function downloadEstimateDocument(documentId: string): Promise<Blob> {
  return apiBlobRequest(`/api/v1/estimate-documents/${documentId}/download`, {
    method: "GET",
  });
}

export function listEstimateRevisions(estimateId: string): Promise<EstimateRevisionResponse[]> {
  return apiRequest<EstimateRevisionResponse[]>(`/api/v1/estimates/${estimateId}/revisions`);
}

export function listEstimateItems(revisionId: string): Promise<EstimateItemResponse[]> {
  return apiRequest<EstimateItemResponse[]>(`/api/v1/estimate-revisions/${revisionId}/items`);
}

export function createEstimateItem(
  revisionId: string,
  payload: EstimateItemCreateRequest,
): Promise<EstimateItemResponse> {
  return apiRequest<EstimateItemResponse>(`/api/v1/estimate-revisions/${revisionId}/items`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateEstimateItem(
  itemId: string,
  payload: EstimateItemUpdateRequest,
): Promise<EstimateItemResponse> {
  return apiRequest<EstimateItemResponse>(`/api/v1/estimate-items/${itemId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function archiveEstimateItem(itemId: string): Promise<EstimateItemResponse> {
  return apiRequest<EstimateItemResponse>(`/api/v1/estimate-items/${itemId}/archive`, {
    method: "POST",
  });
}
