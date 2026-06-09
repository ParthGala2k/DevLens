"use client";

import { useEffect, useState } from "react";
import { apiGet } from "@/lib/api-client";
import { Card } from "@/components/ui/Card";

interface ReliabilityRow {
  developer: string;
  sprint: string;
  assigned: number;
  completed: number;
  completion_ratio: number;
  avg_cycle_time_days: number;
  on_time_ratio: number;
  churn: number;
}

function ratioColor(r: number): string {
  if (r >= 1.0) return "text-green-600 font-semibold";
  if (r >= 0.75) return "text-yellow-600";
  return "text-red-600 font-semibold";
}

export function ReliabilityTable() {
  const [rows, setRows] = useState<ReliabilityRow[]>([]);
  const [sprint, setSprint] = useState<string>("all");

  useEffect(() => {
    apiGet<ReliabilityRow[]>("/api/team/reliability").then(setRows).catch(() => {});
  }, []);

  const sprints = Array.from(new Set(rows.map((r) => r.sprint)));
  const filtered = sprint === "all" ? rows : rows.filter((r) => r.sprint === sprint);

  return (
    <Card title="Completion Reliability">
      <div className="mb-2 flex gap-2 flex-wrap">
        <button
          onClick={() => setSprint("all")}
          className={`rounded px-2 py-0.5 text-xs ${sprint === "all" ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-600"}`}
        >
          All sprints
        </button>
        {sprints.map((s) => (
          <button
            key={s}
            onClick={() => setSprint(s)}
            className={`rounded px-2 py-0.5 text-xs ${sprint === s ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-600"}`}
          >
            {s}
          </button>
        ))}
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b text-left text-xs text-gray-500">
              <th className="pb-1 font-medium">Developer</th>
              <th className="pb-1 font-medium">Sprint</th>
              <th className="pb-1 font-medium">Done/Assigned</th>
              <th className="pb-1 font-medium">Ratio</th>
              <th className="pb-1 font-medium">Cycle (days)</th>
              <th className="pb-1 font-medium">On-time</th>
              <th className="pb-1 font-medium">Churn</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {filtered.map((r) => (
              <tr key={`${r.developer}-${r.sprint}`}>
                <td className="py-1.5 font-medium">{r.developer}</td>
                <td className="py-1.5 text-gray-500">{r.sprint}</td>
                <td className="py-1.5">{r.completed}/{r.assigned}</td>
                <td className={`py-1.5 ${ratioColor(r.completion_ratio)}`}>{(r.completion_ratio * 100).toFixed(0)}%</td>
                <td className="py-1.5">{r.avg_cycle_time_days.toFixed(1)}</td>
                <td className="py-1.5">{(r.on_time_ratio * 100).toFixed(0)}%</td>
                <td className="py-1.5">{r.churn}</td>
              </tr>
            ))}
            {filtered.length === 0 && (
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
