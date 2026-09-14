"use client";

import React, { useState } from "react";
import { ArrowUp } from "lucide-react";

type MessageInputProps = {
  onSend: (text: string) => void;
  disabled: boolean;
};

export default function MessageInput({ onSend, disabled }: MessageInputProps) {
  const [value, setValue] = useState("");

  function handleSubmit() {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue("");
  }

  return (
    <div className="border-t border-border-subtle bg-surface px-4 py-4">
      <div className="flex items-center gap-2 max-w-[800px] mx-auto rounded-full border border-border-default bg-bg pl-4 pr-1.5 py-1.5 focus-within:border-accent focus-within:ring-1 focus-within:ring-accent transition-colors">
        <label htmlFor="chat-input" className="sr-only">
          Ask a question
        </label>
        <input
          id="chat-input"
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              handleSubmit();
            }
          }}
          placeholder="Ask a question about your documents..."
          className="flex-1 text-[15px] py-1.5 bg-transparent text-text-primary placeholder:text-text-tertiary focus:outline-none"
        />
        <button
          type="button"
          onClick={handleSubmit}
          disabled={disabled || value.trim() === ""}
          aria-label="Send message"
          className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-accent text-surface disabled:opacity-30 disabled:cursor-not-allowed transition-opacity hover:opacity-90 focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent focus-visible:outline-offset-2"
        >
          <ArrowUp className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}
