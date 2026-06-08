"use client";
// A single drafted issue: source thread link, editable title/body/labels, suggested assignee,
// and Approve / Reject actions.
// TODO: POST /api/bridge/proposals/{id}/approve (with optional edits) or .../reject.
import type { IssueProposal } from "@/lib/types";

export function ProposalCard({ proposal }: { proposal: IssueProposal }) {
  // TODO: render proposal fields + edit form + Approve/Reject buttons
  return <div className="rounded border p-3">{proposal.title}</div>;
}
