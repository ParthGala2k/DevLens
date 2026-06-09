"use client";

import { useState } from "react";
import { apiPost } from "@/lib/api-client";

interface Proposal {
  id: string;
  status: string;
  source: string;
  source_ref: string;
  title: string;
  description: string;
  labels: string[];
  suggested_assignee: string | null;
  confidence: number;
  github_issue_url: string | null;
  created_at: string;
}

export function ProposalCard({
  proposal,
  onUpdate,
}: {
  proposal: Proposal;
  onUpdate: (updated: Proposal) => void;
}) {
  const [loading, setLoading] = useState<"approve" | "reject" | null>(null);
  const [editTitle, setEditTitle] = useState(proposal.title);
  const [editAssignee, setEditAssignee] = useState(proposal.suggested_assignee ?? "");
  const [expanded, setExpanded] = useState(false);

  async function approve() {
    setLoading("approve");
    try {
      const updated = await apiPost<Proposal>(
        `/api/bridge/proposals/${proposal.id}/approve`,
        { title: editTitle, suggested_assignee: editAssignee || undefined }
      );
      onUpdate(updated);
    } catch {
      // ignore
    } finally {
      setLoading(null);
    }
  }

  async function reject() {
    setLoading("reject");
    try {
      const updated = await apiPost<Proposal>(`/api/bridge/proposals/${proposal.id}/reject`);
      onUpdate(updated);
    } finally {
      setLoading(null);
    }
  }

  const statusStyles: Record<string, string> = {
    pending: "border-l-4 border-blue-400",
    filed: "border-l-4 border-green-500 opacity-70",
    dismissed: "border-l-4 border-gray-300 opacity-50",
  };

  return (
    <div className={`rounded bg-white p-3 shadow-sm ${statusStyles[proposal.status] ?? ""}`}>
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1">
          <span className="text-xs text-gray-400 uppercase">{proposal.source} · {proposal.source_ref}</span>
          {proposal.status === "pending" ? (
            <input
              className="mt-0.5 block w-full rounded border px-1.5 py-0.5 text-sm font-medium focus:outline-none focus:ring-1"
              value={editTitle}
              onChange={(e) => setEditTitle(e.target.value)}
            />
          ) : (
            <p className="text-sm font-medium">{proposal.title}</p>
          )}
        </div>
        <span className="text-xs font-semibold text-blue-600">
          {(proposal.confidence * 100).toFixed(0)}%
        </span>
      </div>

      {proposal.labels.length > 0 && (
        <div className="mt-1 flex gap-1 flex-wrap">
          {proposal.labels.map((l) => (
            <span key={l} className="rounded bg-gray-100 px-1.5 py-0.5 text-xs text-gray-600">{l}</span>
          ))}
        </div>
      )}

      {proposal.suggested_assignee && proposal.status === "pending" && (
        <div className="mt-1 flex items-center gap-1 text-xs text-gray-500">
          Assignee:
          <input
            className="ml-1 rounded border px-1 py-0.5 text-xs w-24"
            value={editAssignee}
            onChange={(e) => setEditAssignee(e.target.value)}
          />
        </div>
      )}

      <button
        onClick={() => setExpanded((e) => !e)}
        className="mt-1 text-xs text-blue-500 hover:underline"
      >
        {expanded ? "Hide description" : "Show description"}
      </button>
      {expanded && (
        <pre className="mt-1 whitespace-pre-wrap rounded bg-gray-50 p-2 text-xs text-gray-700">
          {proposal.description}
        </pre>
      )}

      {proposal.status === "pending" && (
        <div className="mt-2 flex gap-2">
          <button
            onClick={approve}
            disabled={loading !== null}
            className="rounded bg-green-600 px-3 py-1 text-xs text-white hover:bg-green-700 disabled:opacity-50"
          >
            {loading === "approve" ? "Filing…" : "Approve & File"}
          </button>
          <button
            onClick={reject}
            disabled={loading !== null}
            className="rounded bg-gray-200 px-3 py-1 text-xs text-gray-700 hover:bg-gray-300 disabled:opacity-50"
          >
            {loading === "reject" ? "Rejecting…" : "Reject"}
          </button>
        </div>
      )}

      {proposal.status === "filed" && proposal.github_issue_url && (
        <a
          href={proposal.github_issue_url}
          target="_blank"
          rel="noreferrer"
          className="mt-2 block text-xs text-green-700 hover:underline"
        >
          Filed: {proposal.github_issue_url}
        </a>
      )}
    </div>
  );
}
