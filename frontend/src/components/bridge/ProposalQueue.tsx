"use client";

import { useEffect, useState } from "react";
import { apiGet } from "@/lib/api-client";
import { subscribe } from "@/lib/sse";
import { Card } from "@/components/ui/Card";
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
    <Card title={`Issue Proposals${pending.length ? ` (${pending.length} pending)` : ""}`}>
      <div className="space-y-3 max-h-96 overflow-y-auto">
        {pending.map((p) => (
          <ProposalCard key={p.id} proposal={p} onUpdate={upsert} />
        ))}
        {done.slice(0, 3).map((p) => (
          <ProposalCard key={p.id} proposal={p} onUpdate={upsert} />
        ))}
        {proposals.length === 0 && (
          <p className="py-4 text-center text-sm text-gray-400">No proposals yet</p>
        )}
      </div>
    </Card>
  );
}
