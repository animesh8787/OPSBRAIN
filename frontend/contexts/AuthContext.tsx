"use client";

import React, { createContext, useContext, useState, useEffect, type ReactNode } from "react";
import { FirebaseError } from "firebase/app";
import { onIdTokenChanged, signInWithEmailAndPassword, signOut } from "firebase/auth";
import { getFirebaseAuth } from "@/lib/firebase";

type AuthContextValue = {
  token: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

const INVALID_CREDENTIAL_CODES = new Set([
  "auth/invalid-credential",
  "auth/invalid-email",
  "auth/user-not-found",
  "auth/wrong-password",
]);

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    return onIdTokenChanged(getFirebaseAuth(), async (user) => {
      setToken(user ? await user.getIdToken() : null);
    });
  }, []);

  async function login(email: string, password: string): Promise<{ success: boolean; error?: string }> {
    try {
      await signInWithEmailAndPassword(getFirebaseAuth(), email, password);
      return { success: true };
    } catch (err) {
      if (err instanceof FirebaseError && INVALID_CREDENTIAL_CODES.has(err.code)) {
        return { success: false, error: "Invalid email or password." };
      }
      return { success: false, error: "Could not reach the authentication server." };
    }
  }

  function logout() {
    signOut(getFirebaseAuth());
  }

  return (
    <AuthContext.Provider value={{ token, isAuthenticated: !!token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
