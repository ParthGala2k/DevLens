"use client";

import { useEffect, useRef, useState } from "react";
import { apiGet } from "@/lib/api-client";
import { subscribe } from "@/lib/sse";

interface McpEntry {
  server: "fivetran" | "github";
  connector?: string | null;
  action: string;
  status: "start" | "success" | "error";
  ts: string;
  payload?: Record<string, string>;
}

const SERVER_BADGE = {
  fivetran: "bg-purple-100 text-purple-700 border border-purple-200",
  github:   "bg-gray-100 text-gray-600 border border-gray-200",
};

const STATUS_ICON = { start: "⟳", success: "✓", error: "✗" };
const STATUS_COLOR = { start: "text-blue-500", success: "text-green-600", error: "text-red-500" };

export function McpActivityLog() {
  const [entries, setEntries] = useState<McpEntry[]>([]);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    apiGet<McpEntry[]>("/api/mcp-log").then((items) => setEntries(items)).catch(() => {});
    const unsub = subscribe<McpEntry>("/api/mcp-log/stream", (entry) => {
      setEntries((prev) => [...prev.slice(-99), entry]);
    });
    return unsub;
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [entries]);

  return (
    <div className="flex h-full flex-col rounded-xl border border-gray-200 bg-white shadow-sm">
      {/* Header */}
      <div className="border-b border-gray-100 px-4 py-3">
        <h3 className="text-sm font-semibold text-gray-800">MCP Activity Log</h3>
        <p className="text-xs text-gray-400">
          Live view of every Fivetran and GitHub MCP tool call
        </p>
      </div>

      {/* Log */}
      <div className="flex-1 overflow-y-auto p-3" style={{ maxHeight: "420px" }}>
        {entries.length === 0 ? (
          <div className="py-8 text-center">
            <p className="text-sm text-gray-400">No MCP calls yet.</p>
            <p className="mt-1 text-xs text-gray-300">
              Ask the agent a question or click "Sync Now" to see calls appear here.
            </p>
          </div>
        ) : (
          <div className="space-y-1 font-mono text-xs">
            {entries.map((e, i) => (
              <div
                key={i}
                className={`flex items-center gap-1.5 rounded px-2 py-1 ${
                  e.status === "start" ? "bg-gray-50" :
                  e.status === "error" ? "bg-red-50" :
                  "bg-white"
                }`}
              >
                <span className={`w-3 shrink-0 font-bold ${STATUS_COLOR[e.status]}`}>
                  {STATUS_ICON[e.status]}
                </span>
                <span className={`shrink-0 rounded px-1 py-0.5 text-xs font-semibold ${SERVER_BADGE[e.server] ?? SERVER_BADGE.github}`}>
                  {e.server}
                </span>
                {e.connector && (
                  <span className="text-gray-400">·{e.connector}</span>
                )}
                <span className="text-gray-700">{e.action}</span>
                {e.status === "error" && e.payload?.error && (
                  <span className="truncate text-red-500">{String(e.payload.error).slice(0, 60)}</span>
                )}
                <span className="ml-auto shrink-0 text-gray-300">
                  {new Date(e.ts).toLocaleTimeString()}
                </span>
              </div>
            ))}
          </div>
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
