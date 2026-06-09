"use client";

import { useEffect, useState } from "react";
import { apiGet } from "@/lib/api-client";
import { Card } from "@/components/ui/Card";

interface LoadRow {
  developer: string;
  open_issues: number;
  story_points_in_flight: number;
  prs_awaiting_review: number;
  on_call: boolean;
  meeting_hours: number;
  load_score: number;
}

function scoreColor(score: number): string {
  if (score >= 80) return "bg-red-500 text-white";
  if (score >= 60) return "bg-orange-400 text-white";
  if (score >= 40) return "bg-yellow-300 text-gray-900";
  return "bg-green-200 text-gray-900";
}

export function WorkloadHeatmap() {
  const [rows, setRows] = useState<LoadRow[]>([]);

  useEffect(() => {
    apiGet<LoadRow[]>("/api/team/workload").then(setRows).catch(() => {});
  }, []);

  return (
    <Card title="Team Workload">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b text-left text-xs text-gray-500">
              <th className="pb-1 font-medium">Developer</th>
              <th className="pb-1 font-medium">Issues</th>
              <th className="pb-1 font-medium">Points</th>
              <th className="pb-1 font-medium">PRs</th>
              <th className="pb-1 font-medium">Meetings</th>
              <th className="pb-1 font-medium">On-call</th>
              <th className="pb-1 font-medium">Load</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {rows.map((r) => (
              <tr key={r.developer}>
                <td className="py-1.5 font-medium">{r.developer}</td>
                <td className="py-1.5">{r.open_issues}</td>
                <td className="py-1.5">{r.story_points_in_flight}</td>
                <td className="py-1.5">{r.prs_awaiting_review}</td>
                <td className="py-1.5">{r.meeting_hours}h</td>
                <td className="py-1.5">{r.on_call ? "🔴" : "—"}</td>
                <td className="py-1.5">
                  <span className={`rounded px-2 py-0.5 text-xs font-semibold ${scoreColor(r.load_score)}`}>
                    {r.load_score.toFixed(0)}
                  </span>
                </td>
              </tr>
            ))}
            {rows.length === 0 && (
              <tr>
                <td colSpan={7} className="py-4 text-center text-gray-400">Loading…</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </Card>
  );
}
