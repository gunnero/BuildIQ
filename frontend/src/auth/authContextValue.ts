import { createContext } from "react";

import type { CompanyResponse, CurrentUserResponse, SubscriptionResponse } from "../api/types";

export type LoginPayload = {
  email: string;
  password: string;
};

export type AuthContextValue = {
  token: string | null;
  isAuthenticated: boolean;
  isLoadingSession: boolean;
  sessionError: string | null;
  currentUser: CurrentUserResponse | null;
  company: CompanyResponse | null;
  subscription: SubscriptionResponse | null;
  login: (payload: LoginPayload) => Promise<void>;
  logout: () => void;
  refreshSession: () => Promise<void>;
};

export const AuthContext = createContext<AuthContextValue | undefined>(undefined);
