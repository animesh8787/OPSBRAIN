"use client";

import React, { createContext, useContext, useState, useEffect, type ReactNode } from "react";
import { FirebaseError } from "firebase/app";
import { createUserWithEmailAndPassword, onIdTokenChanged, signInWithEmailAndPassword, signOut } from "firebase/auth";
import { getFirebaseAuth } from "@/lib/firebase";

type AuthContextValue = {
  token: string | null;
  isAuthenticated: boolean;
  // True until Firebase's initial session check (reading persisted state,
  // possibly refreshing the token) resolves once, on mount. Consumers that
  // gate access on isAuthenticated must wait for this to go false first -
  // otherwise a real logged-in user reloading a protected page gets bounced
  // to /login before their session has had a chance to rehydrate.
  isLoading: boolean;
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  signup: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
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
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    return onIdTokenChanged(getFirebaseAuth(), async (user) => {
      setToken(user ? await user.getIdToken() : null);
      setIsLoading(false);
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

  async function signup(email: string, password: string): Promise<{ success: boolean; error?: string }> {
    try {
      await createUserWithEmailAndPassword(getFirebaseAuth(), email, password);
      return { success: true };
    } catch (err) {
      if (err instanceof FirebaseError) {
        if (err.code === "auth/email-already-in-use") {
          return { success: false, error: "An account with this email already exists." };
        }
        if (err.code === "auth/weak-password") {
          return { success: false, error: "Password must be at least 6 characters." };
        }
        if (err.code === "auth/invalid-email") {
          return { success: false, error: "Enter a valid email address." };
        }
      }
      return { success: false, error: "Could not reach the authentication server." };
    }
  }

  function logout() {
    signOut(getFirebaseAuth());
  }

  return (
    <AuthContext.Provider value={{ token, isAuthenticated: !!token, isLoading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
