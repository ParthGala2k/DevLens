"use client";

import { useEffect, useState } from "react";
import { apiGet } from "@/lib/api-client";
import { subscribe } from "@/lib/sse";
import { ProposalCard } from "./ProposalCard";

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

export function ProposalQueue() {
  const [proposals, setProposals] = useState<Proposal[]>([]);

  function upsert(p: Proposal) {
    setProposals((prev) => {
      const idx = prev.findIndex((x) => x.id === p.id);
      if (idx >= 0) {
        const next = [...prev];
        next[idx] = p;
        return next;
      }
      return [p, ...prev];
    });
  }

  useEffect(() => {
    apiGet<Proposal[]>("/api/bridge/proposals").then((ps) => ps.forEach(upsert)).catch(() => {});
    const unsub = subscribe<{ type: string; proposal: Proposal }>(
      "/api/bridge/proposals/stream",
      (event) => {
        if (event.proposal) upsert(event.proposal);
      }
    );
    return unsub;
  }, []);

  const pending = proposals.filter((p) => p.status === "pending");
  const done = proposals.filter((p) => p.status !== "pending");

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
      <div className="mb-3">
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-semibold text-gray-800">Issue Proposals</h3>
          {pending.length > 0 && (
            <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-700">
              {pending.length} pending approval
            </span>
          )}
        </div>
        <p className="mt-0.5 text-xs text-gray-400">
          The agent detected these Jira threads that likely need a GitHub issue.
          Review and approve — filing happens via GitHub MCP only after you confirm.
        </p>
      </div>
      <div className="max-h-[480px] space-y-3 overflow-y-auto">
        {pending.map((p) => (
          <ProposalCard key={p.id} proposal={p} onUpdate={upsert} />
        ))}
        {done.slice(0, 3).map((p) => (
          <ProposalCard key={p.id} proposal={p} onUpdate={upsert} />
        ))}
        {proposals.length === 0 && (
          <p className="py-6 text-center text-sm text-gray-400">No proposals yet</p>
        )}
      </div>
    </div>
  );
}
