import { useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from "react";

import { getCurrentUser, loginRequest } from "../api/auth";
import { setUnauthorizedHandler } from "../api/client";
import { getCurrentCompany } from "../api/company";
import { getCurrentSubscription } from "../api/subscription";
import type { CompanyResponse, CurrentUserResponse, SubscriptionResponse } from "../api/types";
import { AuthContext, type AuthContextValue } from "./authContextValue";
import { clearToken, getToken, saveToken } from "./tokenStorage";

type SessionData = {
  currentUser: CurrentUserResponse;
  company: CompanyResponse;
  subscription: SubscriptionResponse;
};

const SESSION_EXPIRED_MESSAGE = "Сесијата истече. Најавете се повторно.";

async function fetchSessionData(token: string): Promise<SessionData> {
  const [currentUser, company, subscription] = await Promise.all([
    getCurrentUser(token),
    getCurrentCompany(token),
    getCurrentSubscription(token),
  ]);

  return { currentUser, company, subscription };
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => getToken());
  const [currentUser, setCurrentUser] = useState<CurrentUserResponse | null>(null);
  const [company, setCompany] = useState<CompanyResponse | null>(null);
  const [subscription, setSubscription] = useState<SubscriptionResponse | null>(null);
  const [isLoadingSession, setIsLoadingSession] = useState<boolean>(() => Boolean(getToken()));
  const [sessionError, setSessionError] = useState<string | null>(null);
  const hydratedTokenRef = useRef<string | null>(null);

  const clearSession = useCallback(() => {
    hydratedTokenRef.current = null;
    clearToken();
    setToken(null);
    setCurrentUser(null);
    setCompany(null);
    setSubscription(null);
    setSessionError(null);
    setIsLoadingSession(false);
  }, []);

  const applySessionData = useCallback((nextToken: string, sessionData: SessionData) => {
    hydratedTokenRef.current = nextToken;
    setCurrentUser(sessionData.currentUser);
    setCompany(sessionData.company);
    setSubscription(sessionData.subscription);
    setSessionError(null);
  }, []);

  const refreshSession = useCallback(
    async (providedToken?: string | null) => {
      const sessionToken = providedToken ?? token;

      if (!sessionToken) {
        clearSession();
        return;
      }

      setIsLoadingSession(true);
      try {
        const sessionData = await fetchSessionData(sessionToken);
        applySessionData(sessionToken, sessionData);
      } catch (error) {
        clearSession();
        setSessionError(SESSION_EXPIRED_MESSAGE);
        throw error;
      } finally {
        setIsLoadingSession(false);
      }
    },
    [applySessionData, clearSession, token],
  );

  useEffect(() => {
    setUnauthorizedHandler(clearSession);

    return () => setUnauthorizedHandler(null);
  }, [clearSession]);

  useEffect(() => {
    if (!token) {
      hydratedTokenRef.current = null;
      setCurrentUser(null);
      setCompany(null);
      setSubscription(null);
      setIsLoadingSession(false);
      return undefined;
    }

    if (hydratedTokenRef.current === token && currentUser && company && subscription) {
      setIsLoadingSession(false);
      return undefined;
    }

    let isActive = true;

    setIsLoadingSession(true);
    setSessionError(null);

    fetchSessionData(token)
      .then((sessionData) => {
        if (!isActive) {
          return;
        }

        applySessionData(token, sessionData);
      })
      .catch(() => {
        if (!isActive) {
          return;
        }

        clearSession();
        setSessionError(SESSION_EXPIRED_MESSAGE);
      })
      .finally(() => {
        if (isActive) {
          setIsLoadingSession(false);
        }
      });

    return () => {
      isActive = false;
    };
  }, [applySessionData, clearSession, company, currentUser, subscription, token]);

  const value = useMemo<AuthContextValue>(
    () => ({
      token,
      isAuthenticated: Boolean(token),
      isLoadingSession,
      sessionError,
      currentUser,
      company,
      subscription,
      async login(payload) {
        const response = await loginRequest(payload);
        saveToken(response.access_token);
        setToken(response.access_token);
        await refreshSession(response.access_token);
      },
      logout() {
        clearSession();
      },
      refreshSession: () => refreshSession(),
    }),
    [clearSession, company, currentUser, isLoadingSession, refreshSession, sessionError, subscription, token],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
