"use client";

import React from "react";
import { useParams, useSearchParams } from "next/navigation";
import DocumentViewer from "@/components/documents/DocumentViewer";
import RequireAuth from "@/components/auth/RequireAuth";

export default function DocumentPage() {
  const params = useParams();
  const searchParams = useSearchParams();

  const id = typeof params.id === "string" ? params.id : "";
  const pageParam = searchParams.get("page");
  const pageNumber =
    pageParam && /^\d+$/.test(pageParam) ? parseInt(pageParam, 10) : 1;
  const highlightParam = searchParams.get("highlight");

  return (
    <RequireAuth>
      <div className="h-[calc(100vh-56px)] flex flex-col">
        <DocumentViewer
          documentId={id}
          pageNumber={pageNumber}
          highlightedText={highlightParam ?? undefined}
        />
      </div>
    </RequireAuth>
  );
}
