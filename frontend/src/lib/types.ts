// Shared TypeScript types — keep in sync with shared/contracts/*.json and backend pydantic models.

export type AgentEventType = "thinking" | "tool_call" | "tool_result" | "message";

export interface AgentEvent {
  type: AgentEventType;
  data: unknown;
  ts: string;
}

export interface McpEvent {
  connector?: string;
  action: string;
  status: "start" | "success" | "error";
  ts: string;
  payload?: unknown;
}

export interface Alert {
  id: string;
  severity: "info" | "warning" | "critical";
  title: string;
  detail: string;
  source: "github" | "jira" | "calendar" | "pagerduty" | "cross";
  evidence: unknown[];
  createdAt: string;
}

export interface Connector {
  id: "github" | "jira" | "calendar" | "pagerduty";
  status: "connected" | "syncing" | "error";
  lastSyncAt: string | null;
}
