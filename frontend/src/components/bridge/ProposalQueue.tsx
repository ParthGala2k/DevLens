"use client";
// Discussion -> Repo bridge: the approval queue.
// Agent-drafted GitLab issues await a human's approve/reject. Approving fires a GitLab MCP call.
// TODO: seed with GET /api/bridge/proposals, live-append via subscribe("/api/bridge/proposals/stream"),
//       render a <ProposalCard /> per item.
import { Card } from "@/components/ui/Card";

export function ProposalQueue() {
  return <Card title="Issue Proposals">{/* TODO: ProposalCard list */}</Card>;
}
