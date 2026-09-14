"use client";

import React, { createContext, useContext, useState, useEffect, type ReactNode } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { listDocuments, ApiError } from "@/lib/api-client";

export interface DocumentItem {
  id: string;
  name: string;
  uploadedAt: string;
  status: "uploading" | "processing" | "ready" | "error";
}

type DocumentsContextValue = {
  documents: DocumentItem[];
  setDocuments: React.Dispatch<React.SetStateAction<DocumentItem[]>>;
};

const DocumentsContext = createContext<DocumentsContextValue | null>(null);

export function useDocuments() {
  const ctx = useContext(DocumentsContext);
  if (!ctx) throw new Error("useDocuments must be used within DocumentsProvider");
  return ctx;
}

export function DocumentsProvider({ children }: { children: ReactNode }) {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const { token, isAuthenticated, logout } = useAuth();

  useEffect(() => {
    if (!isAuthenticated) return;

    async function fetchDocuments() {
      try {
        const data = await listDocuments(token);
        const mapped: DocumentItem[] = data.map((doc) => ({
          id: doc.id,
          name: doc.filename,
          uploadedAt: new Date(doc.uploaded_at).toLocaleDateString("en-GB", {
            day: "2-digit", month: "short", year: "numeric",
          }),
          status: doc.upload_status === "ready" ? "ready" :
                  doc.upload_status === "failed" ? "error" :
                  "processing",
        }));

        setDocuments(mapped);
      } catch (err) {
        if (err instanceof ApiError && err.status === 401) {
          logout();
          return;
        }
        // Any other failure fetching the list on load - fail silently, the
        // list just stays empty rather than crashing the page. The user can
        // still upload new documents even if this initial fetch fails.
      }
    }

    fetchDocuments();
  }, [isAuthenticated, token]);

  return (
    <DocumentsContext.Provider value={{ documents, setDocuments }}>
      {children}
    </DocumentsContext.Provider>
  );
}
