import { apiRequest } from "./client";
import type {
  RoomCreateRequest,
  RoomOpeningCreateRequest,
  RoomOpeningResponse,
  RoomOpeningUpdateRequest,
  RoomResponse,
  RoomUpdateRequest,
} from "./types";

export function listProjectRooms(projectId: string): Promise<RoomResponse[]> {
  return apiRequest<RoomResponse[]>(`/api/v1/projects/${projectId}/rooms`);
}

export function createRoom(projectId: string, payload: RoomCreateRequest): Promise<RoomResponse> {
  return apiRequest<RoomResponse>(`/api/v1/projects/${projectId}/rooms`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getRoom(roomId: string): Promise<RoomResponse> {
  return apiRequest<RoomResponse>(`/api/v1/rooms/${roomId}`);
}

export function updateRoom(roomId: string, payload: RoomUpdateRequest): Promise<RoomResponse> {
  return apiRequest<RoomResponse>(`/api/v1/rooms/${roomId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function archiveRoom(roomId: string): Promise<RoomResponse> {
  return apiRequest<RoomResponse>(`/api/v1/rooms/${roomId}/archive`, {
    method: "POST",
  });
}

export function listRoomOpenings(roomId: string): Promise<RoomOpeningResponse[]> {
  return apiRequest<RoomOpeningResponse[]>(`/api/v1/rooms/${roomId}/openings`);
}

export function createRoomOpening(
  roomId: string,
  payload: RoomOpeningCreateRequest,
): Promise<RoomOpeningResponse> {
  return apiRequest<RoomOpeningResponse>(`/api/v1/rooms/${roomId}/openings`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateRoomOpening(
  openingId: string,
  payload: RoomOpeningUpdateRequest,
): Promise<RoomOpeningResponse> {
  return apiRequest<RoomOpeningResponse>(`/api/v1/openings/${openingId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function archiveRoomOpening(openingId: string): Promise<RoomOpeningResponse> {
  return apiRequest<RoomOpeningResponse>(`/api/v1/openings/${openingId}/archive`, {
    method: "POST",
  });
}
