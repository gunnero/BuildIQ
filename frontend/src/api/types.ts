export type LoginRequest = {
  email: string;
  password: string;
};

export type TokenResponse = {
  access_token: string;
  token_type?: string;
};

export type CurrentUserResponse = {
  id: string;
  company_id: string;
  name: string;
  email: string;
  status: string;
  is_hq_admin: boolean;
  roles: string[];
  created_at: string;
  updated_at: string;
};

export type CompanyResponse = {
  id: string;
  name: string;
  tax_number: string | null;
  address: string | null;
  phone: string | null;
  email: string | null;
  status: string;
  is_internal: boolean;
  created_at: string;
  updated_at: string;
};

export type SubscriptionPlanResponse = {
  id: string;
  key: string;
  name: string;
  price_mkd: number;
  billing_period: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type SubscriptionResponse = {
  id: string;
  company_id: string;
  status: string;
  plan: SubscriptionPlanResponse;
  created_at: string;
  updated_at: string;
};

export type CustomerResponse = {
  id: string;
  company_id: string;
  name: string;
  phone: string | null;
  email: string | null;
  address: string | null;
  note: string | null;
  status: string;
  archived_at: string | null;
  created_at: string;
  updated_at: string;
};

export type CustomerCreateRequest = {
  name: string;
  phone: string | null;
  email: string | null;
  address: string | null;
  note: string | null;
};

export type CustomerUpdateRequest = Partial<CustomerCreateRequest>;

export type CustomerContactResponse = {
  id: string;
  company_id: string;
  customer_id: string;
  full_name: string;
  phone: string | null;
  email: string | null;
  role: string | null;
  note: string | null;
  is_primary: boolean;
  archived_at: string | null;
  created_at: string;
  updated_at: string;
};

export type ContactCreateRequest = {
  full_name: string;
  phone: string | null;
  email: string | null;
  role: string | null;
  note: string | null;
  is_primary: boolean;
};

export type PropertyResponse = {
  id: string;
  company_id: string;
  customer_id: string;
  name: string;
  address: string | null;
  city: string | null;
  note: string | null;
  status: string;
  archived_at: string | null;
  created_at: string;
  updated_at: string;
};

export type PropertyCreateRequest = {
  customer_id: string;
  name: string;
  address: string | null;
  city: string | null;
  note: string | null;
};

export type PropertyUpdateRequest = Partial<Omit<PropertyCreateRequest, "customer_id">>;

export type PropertyContactResponse = {
  id: string;
  company_id: string;
  property_id: string;
  full_name: string;
  phone: string | null;
  email: string | null;
  role: string | null;
  note: string | null;
  is_primary: boolean;
  archived_at: string | null;
  created_at: string;
  updated_at: string;
};

export type PropertyNoteResponse = {
  id: string;
  company_id: string;
  property_id: string;
  content: string;
  created_by_user_id: string | null;
  archived_at: string | null;
  created_at: string;
  updated_at: string;
};

export type PropertyNoteCreateRequest = {
  content: string;
};

export type ProjectResponse = {
  id: string;
  company_id: string;
  customer_id: string;
  property_id: string;
  name: string;
  description: string | null;
  address: string | null;
  status: string;
  agreed_project_price: number | null;
  start_date: string | null;
  due_date: string | null;
  archived_at: string | null;
  created_at: string;
  updated_at: string;
};

export type ProjectCreateRequest = {
  customer_id: string;
  property_id: string;
  name: string;
  description: string | null;
  address: string | null;
  agreed_project_price: number | null;
  start_date: string | null;
  due_date: string | null;
};

export type ProjectUpdateRequest = Partial<Omit<ProjectCreateRequest, "customer_id" | "property_id">>;

export type ProjectStatusUpdateRequest = {
  status: string;
  note?: string | null;
};

export type ProjectStatusHistoryResponse = {
  id: string;
  company_id: string;
  project_id: string;
  from_status: string | null;
  to_status: string;
  note: string | null;
  changed_by_user_id: string | null;
  created_at: string;
};

export type ProjectTimelineEventResponse = {
  id: string;
  company_id: string;
  project_id: string;
  event_type: string;
  message: string | null;
  created_by_user_id: string | null;
  created_at: string;
};

export type ProjectTaskResponse = {
  id: string;
  company_id: string;
  project_id: string;
  title: string;
  description: string | null;
  status: string;
  assigned_user_id: string | null;
  due_date: string | null;
  completed_at: string | null;
  archived_at: string | null;
  created_at: string;
  updated_at: string;
};

export type ProjectTaskCreateRequest = {
  title: string;
  description: string | null;
  assigned_user_id: string | null;
  due_date: string | null;
};

export type ProjectTaskUpdateRequest = Partial<ProjectTaskCreateRequest>;

export type ProjectTaskStatusUpdateRequest = {
  status: string;
};

export type RoomResponse = {
  id: string;
  company_id: string;
  project_id: string;
  project_task_id: string | null;
  name: string;
  room_type: string;
  floor: string | null;
  note: string | null;
  length: number;
  width: number;
  height: number;
  floor_area: number;
  ceiling_area: number;
  wall_area_gross: number;
  openings_area_total: number;
  wall_area_net: number;
  total_paintable_area: number;
  archived_at: string | null;
  created_at: string;
  updated_at: string;
};

export type RoomCreateRequest = {
  name: string;
  room_type: string;
  project_task_id: string | null;
  floor: string | null;
  note: string | null;
  length: number;
  width: number;
  height: number;
};

export type RoomUpdateRequest = Partial<RoomCreateRequest>;

export type RoomOpeningResponse = {
  id: string;
  company_id: string;
  room_id: string;
  opening_type: string;
  name: string;
  width: number;
  height: number;
  quantity: number;
  opening_area: number;
  note: string | null;
  archived_at: string | null;
  created_at: string;
  updated_at: string;
};

export type RoomOpeningCreateRequest = {
  opening_type: string;
  name: string;
  width: number;
  height: number;
  quantity: number;
  note: string | null;
};

export type RoomOpeningUpdateRequest = Partial<RoomOpeningCreateRequest>;

export type MeasurementSetResponse = {
  id: string;
  company_id: string;
  project_id: string;
  project_task_id: string | null;
  name: string;
  description: string | null;
  archived_at: string | null;
  created_at: string;
  updated_at: string;
};

export type MeasurementSetCreateRequest = {
  name: string;
  description: string | null;
  project_task_id: string | null;
};

export type MeasurementItemResponse = {
  id: string;
  company_id: string;
  measurement_set_id: string;
  name: string;
  unit: string;
  quantity: number;
  note: string | null;
  archived_at: string | null;
  created_at: string;
  updated_at: string;
};

export type MeasurementItemCreateRequest = {
  name: string;
  unit: string;
  quantity: number;
  note: string | null;
};

export type MeasurementItemUpdateRequest = Partial<MeasurementItemCreateRequest>;
