"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { getDocumentPage } from "@/lib/api-client";

type DocumentViewerProps = {
  documentId: string;
  pageNumber: number;
  highlightedText?: string;
};

type PageData = {
  text: string;
  image_url: string;
  page_count: number;
};

export default function DocumentViewer({
  documentId,
  pageNumber,
  highlightedText,
}: DocumentViewerProps) {
  const { token } = useAuth();
  const router = useRouter();
  const [pageData, setPageData] = useState<PageData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    setPageData(null);

    async function fetchPage() {
      try {
        const data = await getDocumentPage(token, documentId, pageNumber);
        setPageData({
          text: data.text,
          image_url: data.image_url,
          page_count: data.page_count,
        });
        setLoading(false);
      } catch {
        setError(
          "Could not load this page. The document may not be ready yet, or you may need to log in."
        );
        setLoading(false);
      }
    }

    fetchPage();
  }, [documentId, pageNumber, token]);

  useEffect(() => {
    if (!pageData) return;
    document
      .getElementById("cited-highlight")
      ?.scrollIntoView({ behavior: "smooth", block: "center" });
  }, [pageData]);

  function renderText() {
    if (!pageData) return null;

    if (!highlightedText || pageData.text.indexOf(highlightedText) === -1) {
      return (
        <p className="text-[15px] leading-[22px] text-text-primary">
          {pageData.text}
        </p>
      );
    }

    const idx = pageData.text.indexOf(highlightedText);
    const before = pageData.text.slice(0, idx);
    const after = pageData.text.slice(idx + highlightedText.length);

    return (
      <p className="text-[15px] leading-[22px] text-text-primary">
        {before}
        <mark
          id="cited-highlight"
          className="bg-accent-subtle text-text-primary px-1 rounded-sm scroll-mt-20"
        >
          {highlightedText}
        </mark>
        {after}
      </p>
    );
  }

  function goToPage(newPage: number) {
    router.push(`/documents/${documentId}?page=${newPage}`);
  }

  const canGoPrevious = pageNumber > 1;
  const canGoNext =
    pageData !== null && pageData.page_count > 0 && pageNumber < pageData.page_count;

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between px-6 py-4 border-b border-border-subtle bg-surface">
        <Link
          href="/documents"
          className="flex items-center gap-1.5 text-[14px] font-medium text-text-secondary hover:text-text-primary transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent focus-visible:outline-offset-2 rounded-sm"
        >
          <ChevronLeft className="h-4 w-4" />
          Documents
        </Link>
        <span className="text-[13px] text-text-secondary font-mono">
          Page {pageNumber}
          {pageData && pageData.page_count > 0
            ? ` of ${pageData.page_count}`
            : null}
        </span>
      </div>

      <div className="flex-1 overflow-y-auto bg-bg px-6 py-8 flex justify-center">
        <div className="bg-surface border border-border-default rounded-md shadow-raised max-w-[680px] w-full p-4 sm:p-10 min-h-[880px]">
          {loading && (
            <div className="min-h-[880px] flex items-center justify-center">
              <p className="text-[15px] text-text-secondary">Loading page...</p>
            </div>
          )}

          {error && (
            <div className="min-h-[880px] flex items-center justify-center">
              <p className="text-[15px] text-error">{error}</p>
            </div>
          )}

          {pageData && (
            <>
              <img
                src={pageData.image_url}
                alt={`Page ${pageNumber}`}
                className="w-full h-auto mb-6"
              />
              {renderText()}
            </>
          )}
        </div>
      </div>

      <div className="flex items-center justify-center gap-4 px-6 py-4 border-t border-border-subtle bg-surface">
        <button
          type="button"
          disabled={!canGoPrevious}
          onClick={() => goToPage(pageNumber - 1)}
          className="flex items-center gap-1 text-[14px] font-medium px-2 sm:px-3 py-1.5 rounded-md border border-border-default text-text-secondary hover:border-accent/40 hover:text-text-primary disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:border-border-default disabled:hover:text-text-secondary transition-colors"
        >
          <ChevronLeft className="h-4 w-4" />
          Previous
        </button>
        <span className="text-[13px] text-text-secondary font-mono">
          {pageNumber}
        </span>
        <button
          type="button"
          disabled={!canGoNext}
          onClick={() => goToPage(pageNumber + 1)}
          className="flex items-center gap-1 text-[14px] font-medium px-2 sm:px-3 py-1.5 rounded-md border border-border-default text-text-secondary hover:border-accent/40 hover:text-text-primary disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:border-border-default disabled:hover:text-text-secondary transition-colors"
        >
          Next
          <ChevronRight className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}
