"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowLeft, Network, TriangleAlert } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    const result = await login(email, password);
    setLoading(false);
    if (result.success) {
      router.push("/documents");
    } else {
      setError(result.error ?? "Login failed.");
    }
  }

  return (
    <div className="relative flex items-center justify-center min-h-[calc(100vh-56px)] px-6 overflow-hidden">
      <div
        aria-hidden
        className="pointer-events-none absolute -top-32 left-1/2 h-[420px] w-[720px] -translate-x-1/2 rounded-full bg-accent-subtle opacity-70 blur-3xl"
      />
      <div className="relative w-full max-w-[360px]">
        <Link
          href="/"
          className="mb-8 inline-flex items-center gap-1.5 text-[13px] font-medium text-text-secondary hover:text-text-primary transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent focus-visible:outline-offset-2 rounded-sm"
        >
          <ArrowLeft className="h-3.5 w-3.5" />
          Back to home
        </Link>

        <span className="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-accent text-surface">
          <Network className="h-5 w-5" />
        </span>
        <h1 className="font-display text-[28px] leading-[36px] font-medium text-text-primary mb-1">
          Sign in
        </h1>
        <p className="text-[14px] text-text-secondary mb-6">
          Access the console to ask questions and manage documents.
        </p>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="flex flex-col gap-1.5">
            <label htmlFor="email" className="text-[13px] font-medium text-text-secondary">
              Email
            </label>
            <input
              id="email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="text-[15px] px-4 py-2.5 rounded-md border border-border-default bg-surface text-text-primary placeholder:text-text-tertiary focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent transition-colors"
            />
          </div>
          <div className="flex flex-col gap-1.5">
            <label htmlFor="password" className="text-[13px] font-medium text-text-secondary">
              Password
            </label>
            <input
              id="password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="text-[15px] px-4 py-2.5 rounded-md border border-border-default bg-surface text-text-primary placeholder:text-text-tertiary focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent transition-colors"
            />
          </div>
          {error && (
            <p className="flex items-center gap-1.5 text-[13px] text-error">
              <TriangleAlert className="h-3.5 w-3.5 shrink-0" />
              {error}
            </p>
          )}
          <button
            type="submit"
            disabled={loading}
            className="text-[14px] font-medium px-4 py-2.5 rounded-md bg-accent text-surface hover:opacity-90 transition-opacity disabled:opacity-40 disabled:cursor-not-allowed mt-2 focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent focus-visible:outline-offset-2"
          >
            {loading ? "Signing in..." : "Sign in"}
          </button>
        </form>
      </div>
    </div>
  );
}
