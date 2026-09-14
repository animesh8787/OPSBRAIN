"use client";

import React, { useRef, useEffect } from "react";
import MessageList from "@/components/chat/MessageList";
import MessageInput from "@/components/chat/MessageInput";
import { useAuth } from "@/contexts/AuthContext";
import { useChat } from "@/contexts/ChatContext";
import { sendChatMessage, ApiError } from "@/lib/api-client";
import RequireAuth from "@/components/auth/RequireAuth";

function isNearBottom(container: HTMLDivElement, threshold = 150): boolean {
  return container.scrollHeight - container.scrollTop - container.clientHeight < threshold;
}

export default function ChatPage() {
  const { token, logout } = useAuth();
  const { messages, status, setMessages, setStatus, persistUserMessage, persistAssistantMessage } = useChat();
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  async function handleSend(text: string) {
    const userMessage = { role: "user" as const, content: text };
    setMessages((prev) => [...prev, userMessage]);
    persistUserMessage(text); // fire-and-forget, do not await
    setStatus("loading");

    try {
      const data = await sendChatMessage(token, text);

      const assistantMessage = {
        role: "assistant" as const,
        content: data.answer,
        citations: data.citations.map((c) => ({
          index: c.index,
          filename: c.document_filename,
          page: c.page_number ?? 1,
          content: c.content,
          score: c.score,
          documentId: c.document_id,
        })),
      };

      setMessages((prev) => [...prev, assistantMessage]);
      persistAssistantMessage(assistantMessage.content, assistantMessage.citations ?? []); // fire-and-forget
      setStatus("idle");
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        logout();
        return;
      }
      setStatus("error");
    }
  }

  function handleRetry() {
    setStatus("idle");
  }

  useEffect(() => {
    const container = scrollContainerRef.current;
    if (!container) return;

    const shouldScroll = isNearBottom(container, 300);

    if (shouldScroll) {
      bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
    }
  }, [messages, status]);

  return (
    <RequireAuth>
      <div className="flex flex-col h-[calc(100vh-56px)]">
        <div className="flex-1 overflow-y-auto px-3 sm:px-4 py-6 max-w-[800px] mx-auto w-full" ref={scrollContainerRef}>
          <MessageList
            messages={messages}
            status={status}
            errorMessage="Something went wrong generating a response. Please try again."
            onRetry={handleRetry}
          />
          <div ref={bottomRef} />
        </div>
        <MessageInput onSend={handleSend} disabled={status === "loading" || status === "error"} />
      </div>
    </RequireAuth>
  );
}
