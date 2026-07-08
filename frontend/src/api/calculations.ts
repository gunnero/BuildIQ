import { apiRequest } from "./client";
import type { CalculationEngineResponse, CalculationRunCreateRequest, CalculationRunResponse } from "./types";

export function listCalculationEngines(): Promise<CalculationEngineResponse[]> {
  return apiRequest<CalculationEngineResponse[]>("/api/v1/calculation-engines");
}

export function listCalculations(): Promise<CalculationRunResponse[]> {
  return apiRequest<CalculationRunResponse[]>("/api/v1/calculations");
}

export function getCalculation(calculationRunId: string): Promise<CalculationRunResponse> {
  return apiRequest<CalculationRunResponse>(`/api/v1/calculations/${calculationRunId}`);
}

export function runCalculation(payload: CalculationRunCreateRequest): Promise<CalculationRunResponse> {
  return apiRequest<CalculationRunResponse>("/api/v1/calculations/run", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
