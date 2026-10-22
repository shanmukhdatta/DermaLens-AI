"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import {
  completeOidcLogin, configuredOidc, OidcPublicConfig, startOidcLogin,
} from "@/lib/oidc-pkce";

type AuthContextValue = {
  accessToken: string | null;
  configured: boolean;
  login: () => Promise<void>;
  logout: () => void;
  completeRedirect: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function ResearchAuthProvider({ children }: { children: React.ReactNode }) {
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [expiresAt, setExpiresAt] = useState<number>(0);

  const config = useMemo<OidcPublicConfig | null>(() => {
    try { return configuredOidc(); }
    catch { return null; }
  }, []);

  const logout = useCallback(() => {
    setAccessToken(null);
    setExpiresAt(0);
  }, []);
  useEffect(() => {
    if (!accessToken || expiresAt <= Date.now()) {
      if (accessToken) logout();
      return;
    }
    const task = window.setTimeout(logout, Math.max(100, expiresAt - Date.now()));
    return () => window.clearTimeout(task);
  }, [accessToken, expiresAt, logout]);

  const login = useCallback(async () => {
    if (!config) throw new Error("OIDC sign-in is not configured.");
    await startOidcLogin(config);
  }, [config]);

  const completeRedirect = useCallback(async () => {
    if (!config) throw new Error("OIDC sign-in is not configured.");
    const api = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";
    const result = await completeOidcLogin(config, api);
    setAccessToken(result.accessToken);
    setExpiresAt(result.expiresAt);
  }, [config]);

  return (
    <AuthContext.Provider value={{
      accessToken, configured: Boolean(config), login, logout, completeRedirect,
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useResearchAuth(): AuthContextValue {
  const value = useContext(AuthContext);
  if (!value) throw new Error("ResearchAuthProvider is missing.");
  return value;
}
