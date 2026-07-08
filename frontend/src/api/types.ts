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
