"use client";

import React from "react";
import Link from "next/link";

type CitationBadgeProps = {
  index: number;
  filename: string;
  page: number;
  content?: string;
  score?: number;
  documentId?: string;
};

const FILENAME_TO_DOC_ID: Record<string, string> = {
  "P-101A_Manual.pdf": "p101a-manual",
  "Inspection_2025.pdf": "inspection-2025",
};

function slugifyFilename(filename: string): string {
  return filename
    .toLowerCase()
    .replace(/\.pdf$/, "")
    .replace(/_/g, "-");
}

function scoreDotClass(score: number): string {
  if (score >= 0.7) return "bg-success";
  if (score >= 0.4) return "bg-warning";
  return "bg-error";
}

export default function CitationBadge({
  index,
  filename,
  page,
  content,
  score,
  documentId,
}: CitationBadgeProps) {
  const docId = documentId ?? FILENAME_TO_DOC_ID[filename] ?? slugifyFilename(filename);

  let href = `/documents/${docId}?page=${page}`;
  if (content && content.length > 0) {
    href += `&highlight=${encodeURIComponent(content.slice(0, 150))}`;
  }

  let title = `${filename}, p.${page}`;
  if (typeof score === "number") {
    title += ` · ${Math.round(score * 100)}% match`;
  }

  return (
    <Link
      href={href}
      title={title}
      className="inline-flex items-center justify-center gap-1 text-[12px] font-mono font-medium text-accent bg-accent-subtle hover:bg-accent hover:text-surface transition-colors rounded-sm px-1.5 py-0.5 cursor-pointer focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent focus-visible:outline-offset-2"
    >
      {typeof score === "number" && (
        <span className={`h-1.5 w-1.5 rounded-full ${scoreDotClass(score)}`} />
      )}
      [{index}]
    </Link>
  );
}
