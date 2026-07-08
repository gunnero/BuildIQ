import { createContext } from "react";

export type LoginPayload = {
  email: string;
  password: string;
};

export type AuthContextValue = {
  token: string | null;
  isAuthenticated: boolean;
  login: (payload: LoginPayload) => Promise<void>;
  logout: () => void;
};

export const AuthContext = createContext<AuthContextValue | undefined>(undefined);
