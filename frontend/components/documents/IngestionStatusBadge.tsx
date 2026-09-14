import React from "react";

type IngestionStatus = "uploading" | "processing" | "ready" | "error";

interface IngestionStatusBadgeProps {
  status: IngestionStatus;
}

const statusConfig: Record<
  IngestionStatus,
  { label: string; textClass: string; dotClass: string }
> = {
  uploading: {
    label: "Uploading",
    textClass: "text-text-secondary",
    dotClass: "bg-text-secondary",
  },
  processing: {
    label: "Processing",
    textClass: "text-warning",
    dotClass: "bg-warning",
  },
  ready: {
    label: "Ready",
    textClass: "text-success",
    dotClass: "bg-success",
  },
  error: {
    label: "Error",
    textClass: "text-error",
    dotClass: "bg-error",
  },
};

export default function IngestionStatusBadge({
  status,
}: IngestionStatusBadgeProps) {
  const config = statusConfig[status];

  return (
    <span className="inline-flex items-center gap-1.5 text-[13px] font-medium">
      <span className={`h-1.5 w-1.5 rounded-full ${config.dotClass}`} />
      <span className={config.textClass}>{config.label}</span>
    </span>
  );
}
