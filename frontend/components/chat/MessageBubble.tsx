import React from "react";
import { Network } from "lucide-react";
import CitationBadge from "./CitationBadge";

type Citation = { index: number; filename: string; page: number; content?: string; score?: number; documentId?: string };

type MessageBubbleProps = {
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
};

export default function MessageBubble({
  role,
  content,
  citations,
}: MessageBubbleProps) {
  const isUser = role === "user";

  return (
    <div className={`flex gap-3 mb-6 ${isUser ? "flex-row-reverse" : ""}`}>
      <span
        className={[
          "flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-[12px] font-semibold",
          isUser ? "bg-accent-subtle text-accent" : "bg-accent text-surface",
        ].join(" ")}
        aria-hidden="true"
      >
        {isUser ? "U" : <Network className="h-3.5 w-3.5" />}
      </span>
      <div
        className={[
          "max-w-[75%] break-words",
          isUser
            ? "bg-accent-subtle text-text-primary rounded-md px-4 py-3"
            : "text-text-primary py-1",
        ].join(" ")}
      >
        <p className="text-[15px] leading-[22px]">{content}</p>
        {citations && citations.length > 0 && (
          <div className="flex flex-wrap items-center gap-1.5 mt-2">
            {citations.map((citation) => (
              <CitationBadge
                key={citation.index}
                index={citation.index}
                filename={citation.filename}
                page={citation.page}
                content={citation.content}
                score={citation.score}
                documentId={citation.documentId}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
