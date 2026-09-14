"use client";

import React, { createContext, useContext, useState, useEffect, type ReactNode } from "react";
import { login as apiLogin, ApiError } from "@/lib/api-client";

type AuthContextValue = {
  token: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

const STORAGE_KEY = "opsbrain-auth-token";

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) setToken(stored);
  }, []);

  async function login(email: string, password: string): Promise<{ success: boolean; error?: string }> {
    try {
      const data = await apiLogin(null, { email, password });
      setToken(data.access_token);
      localStorage.setItem(STORAGE_KEY, data.access_token);
      return { success: true };
    } catch (err) {
      if (err instanceof ApiError && (err.status === 401 || err.status === 400)) {
        return { success: false, error: "Invalid email or password." };
      }
      return { success: false, error: "Could not reach the login server. Is it running?" };
    }
  }

  function logout() {
    setToken(null);
    localStorage.removeItem(STORAGE_KEY);
  }

  return (
    <AuthContext.Provider value={{ token, isAuthenticated: !!token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
