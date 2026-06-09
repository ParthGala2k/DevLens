// Shared TypeScript types — keep in sync with shared/contracts/*.json and backend pydantic models.

export type AgentEventType = "thinking" | "tool_call" | "tool_result" | "message";

export interface AgentEvent {
  type: AgentEventType;
  data: unknown;
  ts: string;
}

export interface McpEvent {
  server: "fivetran" | "github";
  connector?: "github" | "jira" | "slack" | "calendar" | "pagerduty" | null;
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
  source: "github" | "jira" | "slack" | "calendar" | "pagerduty" | "cross";
  evidence: unknown[];
  createdAt: string;
}

export interface Connector {
  id: "github" | "jira" | "slack" | "calendar" | "pagerduty";
  status: "connected" | "syncing" | "error";
  lastSyncAt: string | null;
}

export interface IssueProposal {
  id: string;
  status: "pending" | "filed" | "dismissed";
  source: "slack" | "jira";
  sourceRef: { id: string; permalink: string };
  title: string;
  description: string;
  labels: string[];
  suggestedAssignee: string | null;
  confidence: number;
  githubIssueUrl: string | null;
  createdAt: string;
}

export interface DeveloperLoad {
  developer: string;
  openIssues: number;
  storyPointsInFlight: number;
  prsAwaitingReview: number;
  onCall: boolean;
  meetingHours: number;
  loadScore: number;
}

export interface DeveloperReliability {
  developer: string;
  sprint: string;
  assigned: number;
  completed: number;
  completionRatio: number;
  avgCycleTimeDays: number;
  onTimeRatio: number;
  churn: number;
}
