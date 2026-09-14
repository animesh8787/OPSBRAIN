import React from "react";
import { MessageSquare } from "lucide-react";
import MessageBubble from "./MessageBubble";
import LoadingIndicator from "./LoadingIndicator";
import ErrorMessage from "./ErrorMessage";

type Message = {
  role: "user" | "assistant";
  content: string;
  citations?: { index: number; filename: string; page: number; content?: string; score?: number; documentId?: string }[];
};

type MessageListProps = {
  messages: Message[];
  status: "idle" | "loading" | "error";
  errorMessage: string;
  onRetry: () => void;
};

export default function MessageList({
  messages,
  status,
  errorMessage,
  onRetry,
}: MessageListProps) {
  return (
    <div className="flex flex-col">
      {messages.length === 0 && status === "idle" && (
        <div className="flex flex-col items-center justify-center text-center py-16 px-4">
          <span className="mb-4 flex h-10 w-10 items-center justify-center rounded-full bg-accent-subtle text-accent">
            <MessageSquare className="h-5 w-5" />
          </span>
          <p className="text-[15px] leading-[22px] text-text-secondary mb-1">
            Ask a question about your uploaded documents
          </p>
          <p className="text-[13px] leading-[18px] text-text-tertiary">
            Answers are grounded in your documents and cite the exact source page.
          </p>
        </div>
      )}
      {messages.map((message, index) => (
        <MessageBubble
          key={index}
          role={message.role}
          content={message.content}
          citations={message.citations}
        />
      ))}
      {status === "loading" && <LoadingIndicator />}
      {status === "error" && (
        <ErrorMessage message={errorMessage} onRetry={onRetry} />
      )}
    </div>
  );
}
