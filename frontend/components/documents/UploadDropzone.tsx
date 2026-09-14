"use client";

import React, { useState, useRef } from "react";
import { UploadCloud } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { uploadDocument } from "@/lib/api-client";

type UploadDropzoneProps = {
  onUploadStarted: (documentId: string, filename: string) => void;
};

export default function UploadDropzone({ onUploadStarted }: UploadDropzoneProps) {
  const { token } = useAuth();
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [docType, setDocType] = useState("manual");
  const fileInputRef = useRef<HTMLInputElement>(null);

  async function handleFile(file: File) {
    if (file.type !== "application/pdf") {
      setError("Only PDF files are supported.");
      return;
    }

    setUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("doc_type", docType);

    try {
      const data = await uploadDocument(token, file, docType);
      onUploadStarted(data.document_id, file.name);
      setUploading(false);
    } catch {
      setError("Upload failed. Please try again.");
      setUploading(false);
    }
  }

  function handleFileSelect(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) {
      handleFile(file);
    }
    // Reset the input so the same file can be selected again if needed
    e.target.value = "";
  }

  function handleDrop(e: React.DragEvent<HTMLDivElement>) {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) {
      handleFile(file);
    }
  }

  return (
    <>
      <div className="mb-3">
        <label htmlFor="doc-type" className="sr-only">Document type</label>
        <select
          id="doc-type"
          value={docType}
          onChange={(e) => setDocType(e.target.value)}
          disabled={uploading}
          className="w-full rounded-md border border-border-default bg-bg px-3 py-2 text-[14px] text-text-primary focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent focus-visible:outline-offset-2"
        >
          <option value="manual">Manual</option>
          <option value="inspection_report">Inspection Report</option>
          <option value="sop">SOP</option>
          <option value="maintenance_log">Maintenance Log</option>
        </select>
      </div>
      <div
        className={`
          w-full rounded-md border-2 border-dashed px-4 py-8 sm:px-6 sm:py-10 text-center transition-colors cursor-pointer
          ${isDragging ? "border-accent bg-accent-subtle" : "border-border-default bg-surface hover:border-accent hover:bg-accent-subtle"}
          ${uploading ? "opacity-60 pointer-events-none" : ""}
        `}
        role="button"
        tabIndex={uploading ? -1 : 0}
        aria-label="Upload files. Drop PDF files here or click to browse."
        onClick={() => {
          if (!uploading) {
            fileInputRef.current?.click();
          }
        }}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            if (!uploading) {
              fileInputRef.current?.click();
            }
          }
        }}
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => {
          setIsDragging(false);
        }}
        onDrop={handleDrop}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="application/pdf"
          className="hidden"
          onChange={handleFileSelect}
        />
        <span
          className={[
            "mx-auto mb-3 flex h-10 w-10 items-center justify-center rounded-full transition-colors",
            isDragging ? "bg-accent text-surface" : "bg-accent-subtle text-accent",
          ].join(" ")}
        >
          <UploadCloud className="h-5 w-5" />
        </span>
        <p className="text-[15px] font-medium text-text-primary">
          {uploading ? "Uploading..." : "Drop PDF files here"}
        </p>
        {!uploading && (
          <p className="mt-1 text-[13px] text-text-tertiary">
            or click to browse
          </p>
        )}
        {error && (
          <p className="mt-2 text-[13px] text-error">{error}</p>
        )}
      </div>
    </>
  );
}
