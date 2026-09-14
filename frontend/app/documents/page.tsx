"use client";

import React from "react";
import { FileStack, FileText } from "lucide-react";
import UploadDropzone from "@/components/documents/UploadDropzone";
import IngestionStatusBadge from "@/components/documents/IngestionStatusBadge";
import StatsWidget from "@/components/documents/StatsWidget";
import KnowledgeGraphView from "@/components/documents/KnowledgeGraphView";
import { useAuth } from "@/contexts/AuthContext";
import { useDocuments, type DocumentItem } from "@/contexts/DocumentsContext";
import RequireAuth from "@/components/auth/RequireAuth";

function pollDocumentStatus(
  documentId: string,
  token: string | null,
  setDocuments: React.Dispatch<React.SetStateAction<DocumentItem[]>>
) {
  const maxAttempts = 30;
  let attempts = 0;

  const poll = async (): Promise<void> => {
    if (attempts >= maxAttempts) return;
    attempts++;

    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/documents/${documentId}/status`,
        {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        }
      );
      if (!response.ok) return;

      const data = await response.json();
      const mappedStatus: DocumentItem["status"] =
        data.status === "ready"
          ? "ready"
          : data.status === "failed"
          ? "error"
          : "processing";

      setDocuments((prev) =>
        prev.map((doc) =>
          doc.id === documentId ? { ...doc, status: mappedStatus } : doc
        )
      );

      if (data.status !== "ready" && data.status !== "failed") {
        setTimeout(poll, 2000);
      }
    } catch {
      return;
    }
  };

  poll();
}

export default function DocumentsPage() {
  const { token } = useAuth();
  const { documents, setDocuments } = useDocuments();

  function handleUploadStarted(documentId: string, filename: string) {
    const newDoc: DocumentItem = {
      id: documentId,
      name: filename,
      uploadedAt: new Date().toLocaleDateString("en-GB", {
        day: "2-digit",
        month: "short",
        year: "numeric",
      }),
      status: "uploading",
    };
    setDocuments((prev) => [newDoc, ...prev]);
    pollDocumentStatus(documentId, token, setDocuments);
  }

  return (
    <RequireAuth>
      <div className="py-8">
        <div className="flex items-center gap-3 mb-8">
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-accent-subtle text-accent">
            <FileStack className="h-4 w-4" />
          </span>
          <h1 className="font-display text-[28px] leading-[36px] font-medium text-text-primary">
            Documents
          </h1>
        </div>

        <StatsWidget />

        <section className="mb-10">
          <UploadDropzone onUploadStarted={handleUploadStarted} />
        </section>

        <section>
          <h2 className="text-[18px] leading-[26px] font-semibold text-text-primary mb-4">
            Uploaded documents
          </h2>

          {documents.length === 0 ? (
            <div className="rounded-md border border-dashed border-border-default bg-surface px-6 py-10 text-center">
              <span className="mx-auto mb-3 flex h-10 w-10 items-center justify-center rounded-full bg-accent-subtle text-accent">
                <FileText className="h-5 w-5" />
              </span>
              <p className="text-[15px] leading-[22px] text-text-secondary mb-1">
                No documents uploaded yet
              </p>
              <p className="text-[13px] leading-[18px] text-text-tertiary">
                Upload a PDF above to start asking questions about it.
              </p>
            </div>
          ) : (
            <div className="flex flex-col gap-3">
              {documents.map((doc) => (
                <div
                  key={doc.id}
                  className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 rounded-md border border-border-subtle bg-surface px-4 py-3 transition-colors hover:border-accent/40"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-accent-subtle text-accent">
                      <FileText className="h-4 w-4" />
                    </span>
                    <div className="flex flex-col gap-0.5 min-w-0">
                      <span className="text-[15px] font-medium text-text-primary truncate">
                        {doc.name}
                      </span>
                      <span className="text-[13px] text-text-tertiary">
                        {doc.uploadedAt}
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-4 sm:shrink-0">
                    <IngestionStatusBadge status={doc.status} />
                    {doc.status === "ready" && (
                      <a
                        href={`/documents/${doc.id}?page=1`}
                        className="text-[14px] font-medium text-accent hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent focus-visible:outline-offset-2 rounded-sm"
                      >
                        View
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        <section className="mt-10">
          <KnowledgeGraphView />
        </section>
      </div>
    </RequireAuth>
  );
}
