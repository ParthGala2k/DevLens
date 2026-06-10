"use client";

import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { apiPost } from "@/lib/api-client";
import { subscribe } from "@/lib/sse";

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
      const { session_id, run_id } = await apiPost<{ session_id: string; run_id: string }>("/api/chat", {
        message: text,
        session_id: sessionId,
      });
      setSessionId(session_id);
      unsubRef.current?.();
      unsubRef.current = subscribe<{
        type: string;
        data?: { text?: string; name?: string; args?: unknown; result?: unknown };
        ts: string;
      }>(`/api/chat/run/${run_id}/stream`, (event) => {
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
            { role: "agent", text: `${event.data!.name}`, type: "tool_call", ts: event.ts },
          ]);
        } else if (event.type === "tool_result" && event.data?.name) {
          setMessages((prev) => [
            ...prev,
            { role: "agent", text: `${event.data!.name}: ${JSON.stringify(event.data!.result ?? {}).slice(0, 120)}`, type: "tool_result", ts: event.ts },
          ]);
        }
      });
    } catch {
      setLoading(false);
    }
  }

  return (
    <div className="flex h-full flex-col rounded-xl border border-gray-200 bg-white shadow-sm">
      {/* Header */}
      <div className="border-b border-gray-100 px-4 py-3">
        <h3 className="text-sm font-semibold text-gray-800">Ask DevLens</h3>
        <p className="text-xs text-gray-400">
          Ask about PRs, workload, estimation, deep work, or sprint health
        </p>
      </div>

      {/* Message list */}
      <div className="flex-1 space-y-3 overflow-y-auto p-4" style={{ maxHeight: "420px" }}>
        {messages.length === 0 && (
          <div className="py-8 text-center">
            <p className="text-sm text-gray-400">No messages yet.</p>
            <p className="mt-1 text-xs text-gray-300">
              Try: &ldquo;Who is most overloaded right now?&rdquo;
            </p>
          </div>
        )}

        {messages.map((m, i) => {
          if (m.role === "user") {
            return (
              <div key={i} className="flex justify-end">
                <div className="max-w-[80%] rounded-2xl rounded-tr-sm bg-blue-600 px-4 py-2.5 text-sm text-white">
                  {m.text}
                </div>
              </div>
            );
          }

          if (m.type === "tool_call") {
            return (
              <div key={i} className="flex justify-start">
                <div className="flex items-center gap-1.5 rounded-full border border-indigo-100 bg-indigo-50 px-3 py-1 text-xs text-indigo-500">
                  <span className="font-mono">⚙ {m.text}</span>
                </div>
              </div>
            );
          }

          if (m.type === "thinking") {
            return (
              <div key={i} className="flex justify-start">
                <div className="max-w-[85%] rounded-xl border border-dashed border-gray-200 bg-gray-50 px-3 py-2 text-xs italic text-gray-400">
                  {m.text}
                </div>
              </div>
            );
          }

          if (m.type === "tool_result") {
            return (
              <div key={i} className="flex justify-start">
                <div className="max-w-[85%] rounded-xl border border-emerald-100 bg-emerald-50 px-3 py-2 font-mono text-xs text-emerald-700">
                  {m.text}
                </div>
              </div>
            );
          }

          // Main agent message — render as markdown
          return (
            <div key={i} className="flex justify-start">
              <div className="max-w-[85%] rounded-2xl rounded-tl-sm border border-gray-100 bg-white px-4 py-3 text-sm text-gray-800 shadow-sm">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    p: ({ children }) => <p className="mb-2 last:mb-0 leading-relaxed">{children}</p>,
                    strong: ({ children }) => <strong className="font-semibold text-gray-900">{children}</strong>,
                    ul: ({ children }) => <ul className="mb-2 ml-4 list-disc space-y-1">{children}</ul>,
                    ol: ({ children }) => <ol className="mb-2 ml-4 list-decimal space-y-1">{children}</ol>,
                    li: ({ children }) => <li className="leading-relaxed">{children}</li>,
                    code: ({ children }) => (
                      <code className="rounded bg-gray-100 px-1.5 py-0.5 font-mono text-xs text-gray-700">
                        {children}
                      </code>
                    ),
                    h1: ({ children }) => <h1 className="mb-2 text-base font-bold text-gray-900">{children}</h1>,
                    h2: ({ children }) => <h2 className="mb-1.5 text-sm font-bold text-gray-900">{children}</h2>,
                    h3: ({ children }) => <h3 className="mb-1 text-sm font-semibold text-gray-800">{children}</h3>,
                  }}
                >
                  {m.text}
                </ReactMarkdown>
              </div>
            </div>
          );
        })}

        {loading && (
          <div className="flex justify-start">
            <div className="flex items-center gap-2 rounded-2xl border border-gray-100 bg-white px-4 py-3 shadow-sm">
              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-gray-400" style={{ animationDelay: "0ms" }} />
              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-gray-400" style={{ animationDelay: "150ms" }} />
              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-gray-400" style={{ animationDelay: "300ms" }} />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-100 p-3 space-y-2">
        <div className="flex gap-2">
          <input
            className="flex-1 rounded-xl border border-gray-200 px-3 py-2 text-sm text-gray-800 placeholder-gray-400 focus:border-blue-400 focus:outline-none focus:ring-1 focus:ring-blue-100"
            placeholder="Ask about PR lag, team load, deep work, estimation…"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && send()}
            disabled={loading}
          />
          <button
            onClick={send}
            disabled={loading || !input.trim()}
            className="rounded-xl bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-40"
          >
            Send
          </button>
        </div>
        {/* Suggestion chips — hidden once conversation starts */}
        {messages.length === 0 && (
          <div className="flex flex-wrap gap-1.5">
            {[
              "Who's the bottleneck this sprint?",
              "Who has capacity for a new ticket?",
              "How much deep work time is the team getting?",
              "Show me sprint completion reliability",
            ].map((q) => (
              <button
                key={q}
                onClick={() => { setInput(q); }}
                disabled={loading}
                className="rounded-full border border-gray-200 bg-gray-50 px-3 py-1 text-xs text-gray-600 transition-colors hover:border-blue-300 hover:bg-blue-50 hover:text-blue-700 disabled:opacity-40"
              >
                {q}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
