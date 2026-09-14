import React from "react";
import { Network } from "lucide-react";

export default function LoadingIndicator() {
  return (
    <div className="flex gap-3 mb-6" role="status" aria-label="Assistant is responding">
      <span
        className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-accent text-surface"
        aria-hidden="true"
      >
        <Network className="h-3.5 w-3.5" />
      </span>
      <div className="flex items-center gap-1.5 py-2">
        <span className="h-1.5 w-1.5 rounded-full bg-text-tertiary animate-pulse" />
        <span
          className="h-1.5 w-1.5 rounded-full bg-text-tertiary animate-pulse"
          style={{ animationDelay: "150ms" }}
        />
        <span
          className="h-1.5 w-1.5 rounded-full bg-text-tertiary animate-pulse"
          style={{ animationDelay: "300ms" }}
        />
      </div>
    </div>
  );
}
