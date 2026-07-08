import { apiRequest } from "./client";
import type { MaterialResponse } from "./types";

export function listMaterials(): Promise<MaterialResponse[]> {
  return apiRequest<MaterialResponse[]>("/api/v1/materials");
}
