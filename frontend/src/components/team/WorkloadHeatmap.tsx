"use client";

import { useEffect, useState } from "react";
import { apiGet } from "@/lib/api-client";

interface LoadRow {
  developer: string;
  open_issues: number;
  story_points_in_flight: number;
  prs_awaiting_review: number;
  load_score: number;
}

function LoadBar({ score }: { score: number }) {
  const pct = Math.min(score, 100);
  const color =
    score >= 80 ? "bg-red-500" :
    score >= 60 ? "bg-orange-400" :
    score >= 40 ? "bg-yellow-400" :
    "bg-green-400";
  return (
    <div className="flex items-center gap-2">
      <div className="h-2 flex-1 overflow-hidden rounded-full bg-gray-100">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span
        className={`w-8 rounded px-1 py-0.5 text-center text-xs font-bold ${
          score >= 80 ? "bg-red-100 text-red-700" :
          score >= 60 ? "bg-orange-100 text-orange-700" :
          score >= 40 ? "bg-yellow-100 text-yellow-700" :
          "bg-green-100 text-green-700"
        }`}
      >
        {score.toFixed(0)}
      </span>
    </div>
  );
}

export function WorkloadHeatmap() {
  const [rows, setRows] = useState<LoadRow[]>([]);

  useEffect(() => {
    apiGet<LoadRow[]>("/api/team/workload").then(setRows).catch(() => {});
  }, []);

  const sorted = [...rows].sort((a, b) => b.load_score - a.load_score);

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
      <h3 className="mb-1 text-sm font-semibold text-gray-800">Team Workload</h3>
      <p className="mb-3 text-xs text-gray-400">
        Current load per developer from GitHub and Jira. Score factors in open issues, story points in flight, and PRs to review.
        Red = overloaded, Green = has capacity.
      </p>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-100 text-left text-xs text-gray-400">
              <th className="pb-2 font-medium">Developer</th>
              <th className="pb-2 font-medium text-center">Open issues</th>
              <th className="pb-2 font-medium text-center">Story points</th>
              <th className="pb-2 font-medium text-center">PRs to review</th>
              <th className="pb-2 font-medium min-w-[120px]">Load score</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {sorted.map((r) => (
              <tr key={r.developer} className="hover:bg-gray-50">
                <td className="py-2 font-semibold text-gray-800">{r.developer}</td>
                <td className="py-2 text-center text-gray-600">{r.open_issues}</td>
                <td className="py-2 text-center text-gray-600">{r.story_points_in_flight}</td>
                <td className="py-2 text-center text-gray-600">{r.prs_awaiting_review}</td>
                <td className="py-2">
                  <LoadBar score={r.load_score} />
                </td>
              </tr>
            ))}
            {rows.length === 0 && (
              <tr>
                <td colSpan={5} className="py-6 text-center text-sm text-gray-400">
                  No data yet — waiting for Fivetran sync
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
