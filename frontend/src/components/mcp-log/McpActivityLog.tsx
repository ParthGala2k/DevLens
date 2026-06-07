"use client";
// MCP Activity Log — the judge-visible live feed of every Fivetran MCP call.
// e.g. "[Fivetran MCP] → sync_connector(github) → success"
// TODO: subscribe("/api/mcp-log/stream"); render each McpEvent as a McpCallEntry row.
import { Card } from "@/components/ui/Card";

export function McpActivityLog() {
  return <Card title="MCP Activity Log">{/* TODO: live MCP call entries */}</Card>;
}
