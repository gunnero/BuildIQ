import { apiRequest } from "./client";
import type {
  ProjectCreateRequest,
  ProjectResponse,
  ProjectStatusHistoryResponse,
  ProjectStatusUpdateRequest,
  ProjectTaskCreateRequest,
  ProjectTaskResponse,
  ProjectTaskStatusUpdateRequest,
  ProjectTaskUpdateRequest,
  ProjectTimelineEventResponse,
  ProjectUpdateRequest,
} from "./types";

export function listProjects(): Promise<ProjectResponse[]> {
  return apiRequest<ProjectResponse[]>("/api/v1/projects");
}

export function createProject(payload: ProjectCreateRequest): Promise<ProjectResponse> {
  return apiRequest<ProjectResponse>("/api/v1/projects", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getProject(projectId: string): Promise<ProjectResponse> {
  return apiRequest<ProjectResponse>(`/api/v1/projects/${projectId}`);
}

export function updateProject(projectId: string, payload: ProjectUpdateRequest): Promise<ProjectResponse> {
  return apiRequest<ProjectResponse>(`/api/v1/projects/${projectId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function archiveProject(projectId: string): Promise<ProjectResponse> {
  return apiRequest<ProjectResponse>(`/api/v1/projects/${projectId}/archive`, {
    method: "POST",
  });
}

export function changeProjectStatus(
  projectId: string,
  payload: ProjectStatusUpdateRequest,
): Promise<ProjectResponse> {
  return apiRequest<ProjectResponse>(`/api/v1/projects/${projectId}/status`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function listProjectStatusHistory(projectId: string): Promise<ProjectStatusHistoryResponse[]> {
  return apiRequest<ProjectStatusHistoryResponse[]>(`/api/v1/projects/${projectId}/status-history`);
}

export function listProjectTimeline(projectId: string): Promise<ProjectTimelineEventResponse[]> {
  return apiRequest<ProjectTimelineEventResponse[]>(`/api/v1/projects/${projectId}/timeline`);
}

export function listProjectTasks(projectId: string): Promise<ProjectTaskResponse[]> {
  return apiRequest<ProjectTaskResponse[]>(`/api/v1/projects/${projectId}/tasks`);
}

export function createProjectTask(
  projectId: string,
  payload: ProjectTaskCreateRequest,
): Promise<ProjectTaskResponse> {
  return apiRequest<ProjectTaskResponse>(`/api/v1/projects/${projectId}/tasks`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getProjectTask(taskId: string): Promise<ProjectTaskResponse> {
  return apiRequest<ProjectTaskResponse>(`/api/v1/tasks/${taskId}`);
}

export function updateProjectTask(taskId: string, payload: ProjectTaskUpdateRequest): Promise<ProjectTaskResponse> {
  return apiRequest<ProjectTaskResponse>(`/api/v1/tasks/${taskId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function archiveProjectTask(taskId: string): Promise<ProjectTaskResponse> {
  return apiRequest<ProjectTaskResponse>(`/api/v1/tasks/${taskId}/archive`, {
    method: "POST",
  });
}

export function changeProjectTaskStatus(
  taskId: string,
  payload: ProjectTaskStatusUpdateRequest,
): Promise<ProjectTaskResponse> {
  return apiRequest<ProjectTaskResponse>(`/api/v1/tasks/${taskId}/status`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
