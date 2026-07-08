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
