"use client";

import { useEffect, useRef, useState } from "react";
import { apiPost } from "@/lib/api-client";
import { subscribe } from "@/lib/sse";
import { Card } from "@/components/ui/Card";

interface ChatMessage {
  role: "user" | "agent";
  text: string;
  type?: string;
  ts?: string;
}

export function ChatWindow() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const unsubRef = useRef<(() => void) | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function send() {
    const text = input.trim();
    if (!text || loading) return;
    setInput("");
    setLoading(true);

    setMessages((prev) => [...prev, { role: "user", text, ts: new Date().toISOString() }]);

    try {
      const { session_id } = await apiPost<{ session_id: string; run_id: string }>("/api/chat", {
        message: text,
        session_id: sessionId,
      });
      setSessionId(session_id);

      // Clean up previous stream.
      unsubRef.current?.();

      unsubRef.current = subscribe<{ type: string; data?: { text?: string; name?: string; args?: unknown; result?: unknown }; ts: string }>(
        `/api/chat/${session_id}/stream`,
        (event) => {
          if (event.type === "done") {
            setLoading(false);
            unsubRef.current?.();
            return;
          }
          if (event.type === "message" && event.data?.text) {
            setMessages((prev) => [...prev, { role: "agent", text: event.data!.text!, type: "message", ts: event.ts }]);
          } else if (event.type === "thinking" && event.data?.text) {
            setMessages((prev) => [...prev, { role: "agent", text: event.data!.text!, type: "thinking", ts: event.ts }]);
          } else if (event.type === "tool_call" && event.data?.name) {
            setMessages((prev) => [
              ...prev,
              { role: "agent", text: `→ tool: ${event.data!.name}(${JSON.stringify(event.data!.args ?? {})})`, type: "tool_call", ts: event.ts },
            ]);
          } else if (event.type === "tool_result" && event.data?.name) {
            setMessages((prev) => [
              ...prev,
              { role: "agent", text: `← result: ${event.data!.name}: ${JSON.stringify(event.data!.result ?? {}).slice(0, 120)}`, type: "tool_result", ts: event.ts },
            ]);
          }
        }
      );
    } catch {
      setLoading(false);
    }
  }

  const typeStyles: Record<string, string> = {
    message: "bg-white border",
    thinking: "bg-gray-50 border border-dashed italic text-gray-500",
    tool_call: "bg-blue-50 border border-blue-200 font-mono text-blue-700",
    tool_result: "bg-green-50 border border-green-200 font-mono text-green-700",
  };

  return (
    <Card title="Ask DevLens">
      <div className="h-72 overflow-y-auto space-y-2 mb-3">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-[85%] rounded px-3 py-2 text-sm ${
                m.role === "user"
                  ? "bg-blue-600 text-white"
                  : (typeStyles[m.type ?? "message"] ?? typeStyles.message)
              }`}
            >
              {m.text}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="rounded border bg-gray-50 px-3 py-2 text-sm text-gray-400 italic">
              Thinking…
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>
      <div className="flex gap-2">
        <input
          className="flex-1 rounded border px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-400"
          placeholder="Ask about PR lag, team load, on-call noise…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          disabled={loading}
        />
        <button
          onClick={send}
          disabled={loading || !input.trim()}
          className="rounded bg-blue-600 px-4 py-1.5 text-sm text-white hover:bg-blue-700 disabled:opacity-50"
        >
          Send
        </button>
      </div>
    </Card>
  );
}
