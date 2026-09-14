import React from "react";
import { TriangleAlert } from "lucide-react";

type ErrorMessageProps = {
  message: string;
  onRetry: () => void;
};

export default function ErrorMessage({ message, onRetry }: ErrorMessageProps) {
  return (
    <div className="flex items-center justify-between gap-4 rounded-md border border-error bg-surface px-4 py-3 my-2">
      <p className="flex items-center gap-2 text-[14px] text-error">
        <TriangleAlert className="h-4 w-4 shrink-0" />
        {message}
      </p>
      <button
        type="button"
        onClick={onRetry}
        className="text-[13px] font-medium text-accent hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent focus-visible:outline-offset-2 rounded-sm shrink-0"
      >
        Retry
      </button>
    </div>
  );
}
