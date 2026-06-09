"use client";

import { useEffect, useRef, useState } from "react";
import { apiGet } from "@/lib/api-client";
import { subscribe } from "@/lib/sse";
import { Card } from "@/components/ui/Card";

interface McpEntry {
  server: "fivetran" | "github";
  connector?: string | null;
  action: string;
  status: "start" | "success" | "error";
  ts: string;
  payload?: Record<string, string>;
}

const SERVER_COLORS = {
  fivetran: "bg-purple-100 text-purple-800",
  github: "bg-gray-100 text-gray-800",
};

const STATUS_COLORS = {
  start: "text-blue-400",
  success: "text-green-600",
  error: "text-red-600",
};

const STATUS_ICON = {
  start: "⟳",
  success: "✓",
  error: "✗",
};

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
    <Card title="MCP Activity Log">
      <div className="h-80 overflow-y-auto font-mono text-xs space-y-1">
        {entries.map((e, i) => (
          <div key={i} className="flex items-start gap-1.5">
            <span className={`font-semibold ${STATUS_COLORS[e.status] ?? ""}`}>
              {STATUS_ICON[e.status]}
            </span>
            <span className={`rounded px-1 py-0.5 font-medium ${SERVER_COLORS[e.server] ?? "bg-gray-100"}`}>
              {e.server}
            </span>
            {e.connector && (
              <span className="text-gray-400">·{e.connector}</span>
            )}
            <span className="text-gray-700">{e.action}</span>
            {e.status === "error" && e.payload?.error && (
              <span className="text-red-500 truncate">{String(e.payload.error)}</span>
            )}
            <span className="ml-auto text-gray-300 whitespace-nowrap">
              {new Date(e.ts).toLocaleTimeString()}
            </span>
          </div>
        ))}
        {entries.length === 0 && (
          <p className="text-gray-400 py-2">Waiting for MCP calls…</p>
        )}
        <div ref={bottomRef} />
      </div>
    </Card>
  );
}
