"use client";

import React, { createContext, useContext, useState, useEffect, type ReactNode } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { getConversationMessages, createConversation as apiCreateConversation, persistMessage as apiPersistMessage } from "@/lib/api-client";

type Citation = { index: number; filename: string; page: number };

type Message = {
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
};

type ChatContextValue = {
  messages: Message[];
  status: "idle" | "loading" | "error";
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>;
  setStatus: React.Dispatch<React.SetStateAction<"idle" | "loading" | "error">>;
  persistUserMessage: (content: string) => Promise<void>;
  persistAssistantMessage: (content: string, citations: Citation[]) => Promise<void>;
};

const ChatContext = createContext<ChatContextValue | null>(null);

const CONVERSATION_ID_KEY = "opsbrain-conversation-id";

export function useChat() {
  const ctx = useContext(ChatContext);
  if (!ctx) throw new Error("useChat must be used within ChatProvider");
  return ctx;
}

function citationsToDict(citations: Citation[]): Record<string, { document_id: string | null; filename: string; page_number: number }> {
  const dict: Record<string, { document_id: string | null; filename: string; page_number: number }> = {};
  for (const c of citations) {
    dict[String(c.index)] = {
      document_id: null,
      filename: c.filename,
      page_number: c.page,
    };
  }
  return dict;
}

function dictToCitations(dict: Record<string, { document_id?: string | null; filename: string; page_number: number }> | null): Citation[] | undefined {
  if (!dict) return undefined;
  const entries = Object.entries(dict).map(([key, val]) => ({
    index: Number(key),
    filename: val.filename,
    page: val.page_number,
  }));
  entries.sort((a, b) => a.index - b.index);
  return entries.length > 0 ? entries : undefined;
}

export function ChatProvider({ children }: { children: ReactNode }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [status, setStatus] = useState<"idle" | "loading" | "error">("idle");
  const [conversationId, setConversationId] = useState<string | null>(null);
  const { token, isAuthenticated } = useAuth();

  // On mount (once authenticated), check for an existing conversation ID in
  // localStorage and hydrate messages from it. This is what makes chat
  // history survive a hard refresh, not just in-session navigation.
  useEffect(() => {
    if (!isAuthenticated || !token) return;

    const existingId = localStorage.getItem(CONVERSATION_ID_KEY);
    if (!existingId) return;

    async function hydrate(authToken: string, conversationId: string) {
      try {
        const data = await getConversationMessages(authToken, conversationId);
        const hydratedMessages: Message[] = data.map((m) => ({
          role: m.role,
          content: m.content,
          citations: dictToCitations(m.citations),
        }));
        setMessages(hydratedMessages);
        setConversationId(conversationId);
      } catch {
        // Conversation may have been deleted, belong to a stale session,
        // or hydration failed for a network reason - either way, clear
        // the stale ID and fail silently, chat just starts empty.
        localStorage.removeItem(CONVERSATION_ID_KEY);
      }
    }

    hydrate(token, existingId);
  }, [isAuthenticated, token]);

  async function ensureConversation(): Promise<string | null> {
    if (conversationId) return conversationId;
    if (!token) return null;

    try {
      const data = await apiCreateConversation(token);
      setConversationId(data.id);
      localStorage.setItem(CONVERSATION_ID_KEY, data.id);
      return data.id;
    } catch {
      return null;
    }
  }

  async function persistMessage(role: "user" | "assistant", content: string, citations: Citation[] | undefined) {
    const id = await ensureConversation();
    if (!id || !token) return; // Persistence is best-effort - if it fails, the chat UI still works, just won't survive a refresh this time.

    try {
      await apiPersistMessage(token, id, {
        role,
        content,
        citations: citations && citations.length > 0 ? citationsToDict(citations) : null,
      });
    } catch {
      // Best-effort persistence - a failed save should never break the
      // live chat experience, it just means this message won't be there
      // after a refresh.
    }
  }

  async function persistUserMessage(content: string) {
    await persistMessage("user", content, undefined);
  }

  async function persistAssistantMessage(content: string, citations: Citation[]) {
    await persistMessage("assistant", content, citations);
  }

  return (
    <ChatContext.Provider value={{ messages, status, setMessages, setStatus, persistUserMessage, persistAssistantMessage }}>
      {children}
    </ChatContext.Provider>
  );
}
