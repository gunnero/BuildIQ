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

export type MaterialResponse = {
  id: string;
  company_id: string;
  name: string;
  sku: string | null;
  description: string | null;
  category_id: string | null;
  manufacturer_id: string | null;
  unit_id: string;
  coverage_value: number | null;
  coverage_unit: string | null;
  package_quantity: number | null;
  waste_percentage_default: number | null;
  is_active: boolean;
  archived_at: string | null;
  created_at: string;
  updated_at: string;
};

export type CalculationEngineResponse = {
  engine_type: string;
  engine_version: string;
  implemented: boolean;
  status: string;
};

export type CalculationLineItemResponse = {
  id: string;
  company_id: string;
  calculation_run_id: string;
  sort_order: number;
  name: string;
  description: string | null;
  unit: string | null;
  quantity: number | null;
  payload: Record<string, unknown> | null;
  created_at: string;
};

export type CalculationRunResponse = {
  id: string;
  company_id: string;
  project_id: string | null;
  project_task_id: string | null;
  room_id: string | null;
  measurement_set_id: string | null;
  engine_type: string;
  engine_version: string;
  status: string;
  input_payload: Record<string, unknown>;
  output_payload: Record<string, unknown>;
  line_items: CalculationLineItemResponse[];
  created_by_user_id: string;
  created_at: string;
  archived_at: string | null;
};

export type CalculationRunCreateRequest = {
  engine_type: string;
  project_id: string | null;
  project_task_id: string | null;
  room_id: string | null;
  measurement_set_id: string | null;
  input_payload: Record<string, unknown>;
};

export type EstimateResponse = {
  id: string;
  company_id: string;
  customer_id: string;
  property_id: string;
  project_id: string;
  estimate_number: string | null;
  title: string;
  description: string | null;
  status: string;
  source_calculation_run_id: string | null;
  sent_at: string | null;
  accepted_at: string | null;
  rejected_at: string | null;
  archived_at: string | null;
  created_at: string;
  updated_at: string;
};

export type EstimateCreateRequest = {
  project_id: string;
  customer_id: string | null;
  property_id: string | null;
  title: string;
  description: string | null;
};

export type EstimateFromCalculationCreateRequest = {
  title: string | null;
  description: string | null;
};

export type EstimateStatusUpdateRequest = {
  status: string;
};

export type EstimateRevisionResponse = {
  id: string;
  company_id: string;
  estimate_id: string;
  revision_number: number;
  status: string;
  notes: string | null;
  terms: string | null;
  source_calculation_run_id: string | null;
  subtotal: number;
  discount_total: number;
  adjustment_total: number;
  tax_total: number;
  total: number;
  sent_at: string | null;
  accepted_at: string | null;
  rejected_at: string | null;
  archived_at: string | null;
  created_at: string;
  updated_at: string;
};

export type EstimateItemResponse = {
  id: string;
  company_id: string;
  estimate_revision_id: string;
  item_type: string;
  name: string;
  description: string | null;
  material_id: string | null;
  quantity: number;
  unit: string | null;
  unit_price: number;
  total_price: number;
  source_calculation_run_id: string | null;
  source_calculation_line_item_id: string | null;
  sort_order: number;
  archived_at: string | null;
  created_at: string;
  updated_at: string;
};

export type EstimateItemCreateRequest = {
  item_type: string;
  name: string;
  description: string | null;
  material_id: string | null;
  quantity: number;
  unit: string | null;
  unit_price: number;
};

export type EstimateItemUpdateRequest = Partial<EstimateItemCreateRequest>;

export type PaymentAllocationCreateRequest = {
  project_id: string | null;
  estimate_id: string | null;
  amount: number;
  note: string | null;
};

export type PaymentAllocationResponse = {
  id: string;
  company_id: string;
  payment_id: string;
  project_id: string | null;
  estimate_id: string | null;
  amount: number;
  note: string | null;
  archived_at: string | null;
  created_at: string;
  updated_at: string;
};

export type PaymentCreateRequest = {
  customer_id: string;
  project_id: string;
  estimate_id: string | null;
  amount: number;
  payment_method: string;
  payment_date: string;
  status: string;
  note: string | null;
  allocations: PaymentAllocationCreateRequest[];
};

export type ReverseRequest = {
  reason: string;
};

export type PaymentResponse = {
  id: string;
  company_id: string;
  customer_id: string;
  project_id: string;
  estimate_id: string | null;
  amount: number;
  currency: string;
  payment_method: string;
  payment_date: string;
  status: string;
  note: string | null;
  created_by_user_id: string;
  reversal_reason: string | null;
  reversed_at: string | null;
  reversed_by_user_id: string | null;
  archived_at: string | null;
  created_at: string;
  updated_at: string;
  allocations: PaymentAllocationResponse[];
};

export type ExpenseCategoryCreateRequest = {
  name: string;
  description: string | null;
};

export type ExpenseCategoryUpdateRequest = Partial<ExpenseCategoryCreateRequest>;

export type ExpenseCategoryResponse = {
  id: string;
  company_id: string;
  name: string;
  description: string | null;
  archived_at: string | null;
  created_at: string;
  updated_at: string;
};

export type ExpenseCreateRequest = {
  project_id: string | null;
  category_id: string | null;
  supplier_id: string | null;
  material_id: string | null;
  description: string;
  amount: number;
  expense_date: string;
  payment_method: string;
  status: string;
  note: string | null;
};

export type ExpenseResponse = {
  id: string;
  company_id: string;
  project_id: string | null;
  category_id: string | null;
  supplier_id: string | null;
  material_id: string | null;
  description: string;
  amount: number;
  currency: string;
  expense_date: string;
  payment_method: string;
  status: string;
  note: string | null;
  created_by_user_id: string;
  reversal_reason: string | null;
  reversed_at: string | null;
  reversed_by_user_id: string | null;
  archived_at: string | null;
  created_at: string;
  updated_at: string;
};

export type ProjectFinancialSummaryResponse = {
  project_id: string;
  customer_id: string;
  accepted_estimate_total: number | null;
  agreed_project_price: number | null;
  revenue_basis: string;
  total_received_payments: number;
  total_pending_payments: number;
  total_reversed_payments: number;
  outstanding_balance: number | null;
  total_recorded_expenses: number;
  total_reversed_expenses: number;
  estimated_profit: number | null;
  payment_status: string;
};
