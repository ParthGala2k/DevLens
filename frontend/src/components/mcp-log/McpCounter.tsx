"use client";

import { useEffect, useRef, useState } from "react";
import { apiGet } from "@/lib/api-client";
import { subscribe } from "@/lib/sse";

export function McpCounter() {
  const [count, setCount] = useState<number | null>(null);
  // Timestamp of when the initial REST count was fetched.
  // Ring-buffer replay events predate this, so we skip them to avoid double-counting.
  const fetchedAt = useRef<string>("");

  useEffect(() => {
    apiGet<{ count: number }>("/api/mcp-log/count")
      .then((d) => {
        fetchedAt.current = new Date().toISOString();
        setCount(d.count);
      })
      .catch(() => {});

    const unsub = subscribe<{ status: string; ts?: string }>("/api/mcp-log/stream", (event) => {
      if (event.status !== "success" && event.status !== "error") return;
      // Only count events that arrived after the initial REST snapshot.
      if (fetchedAt.current && (event.ts ?? "") <= fetchedAt.current) return;
      setCount((n) => (n ?? 0) + 1);
    });
    return unsub;
  }, []);

  if (count === null) return null;

  return (
    <span className="flex items-center gap-1.5 rounded-full border border-blue-200 bg-blue-50 px-2.5 py-1 text-xs font-medium text-blue-700">
      <span className="relative flex h-1.5 w-1.5">
        <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-blue-400 opacity-75" />
        <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-blue-500" />
      </span>
      {count} MCP call{count !== 1 ? "s" : ""} today
    </span>
  );
}
