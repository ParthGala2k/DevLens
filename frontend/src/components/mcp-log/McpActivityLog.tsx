"use client";
// MCP Activity Log — the judge-visible live feed of every MCP call (Fivetran + GitLab).
// e.g. "[Fivetran MCP] → sync_connector(gitlab) → success" / "[GitLab MCP] → create_issue → success"
// TODO: subscribe("/api/mcp-log/stream"); render each McpEvent as a McpCallEntry row (color by server).
import { Card } from "@/components/ui/Card";

export function McpActivityLog() {
  return <Card title="MCP Activity Log">{/* TODO: live MCP call entries */}</Card>;
}
