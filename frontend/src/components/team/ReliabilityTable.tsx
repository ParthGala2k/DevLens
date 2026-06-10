"use client";

import { useEffect, useState } from "react";
import { apiGet } from "@/lib/api-client";

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

// Sprints with no "active" state marker are treated as completed.
const SPRINT_STATUS: Record<string, { label: string; style: string }> = {};

function RatioBadge({ ratio }: { ratio: number }) {
  const pct = (ratio * 100).toFixed(0);
  const cls =
    ratio >= 1.0 ? "bg-green-100 text-green-700" :
    ratio >= 0.75 ? "bg-yellow-100 text-yellow-700" :
    "bg-red-100 text-red-700";
  return (
    <span className={`rounded px-1.5 py-0.5 text-xs font-semibold ${cls}`}>
      {pct}%
    </span>
  );
}

export function ReliabilityTable() {
  const [rows, setRows] = useState<ReliabilityRow[]>([]);
  const [sprint, setSprint] = useState<string>("all");

  useEffect(() => {
    apiGet<ReliabilityRow[]>("/api/team/reliability").then(setRows).catch(() => {});
  }, []);

  const sprints = Array.from(new Set(rows.map((r) => r.sprint))).sort();
  const filtered = sprint === "all" ? rows : rows.filter((r) => r.sprint === sprint);

  // Group filtered rows by sprint for display
  const bySprint: Record<string, ReliabilityRow[]> = {};
  filtered.forEach((r) => {
    if (!bySprint[r.sprint]) bySprint[r.sprint] = [];
    bySprint[r.sprint].push(r);
  });

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
      <h3 className="mb-1 text-sm font-semibold text-gray-800">Completion Reliability</h3>
      <p className="mb-3 text-xs text-gray-400">
        Did each developer finish what they committed to?
        Completion % = tickets done ÷ tickets committed. Churn = tickets added/removed mid-sprint.
      </p>

      {/* Sprint filter tabs */}
      <div className="mb-3 flex gap-2 flex-wrap">
        <button
          onClick={() => setSprint("all")}
          className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
            sprint === "all"
              ? "bg-blue-600 text-white"
              : "bg-gray-100 text-gray-600 hover:bg-gray-200"
          }`}
        >
          All sprints
        </button>
        {sprints.map((s) => {
          const meta = SPRINT_STATUS[s];
          return (
            <button
              key={s}
              onClick={() => setSprint(s)}
              className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
                sprint === s
                  ? "bg-blue-600 text-white"
                  : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              }`}
            >
              {s.replace("SLS Sprint", "S")}
              {meta && sprint !== s && (
                <span className="ml-1 opacity-60">{meta.label.split(" ")[0]}</span>
              )}
            </button>
          );
        })}
      </div>

      {Object.entries(bySprint)
        .sort(([a], [b]) => a.localeCompare(b))
        .map(([sprintName, sprintRows]) => {
          const meta = SPRINT_STATUS[sprintName];
          return (
            <div key={sprintName} className="mb-4">
              {/* Sprint header */}
              <div className="mb-1.5 flex items-center gap-2">
                <span className="text-xs font-semibold text-gray-600">{sprintName}</span>
                {meta && (
                  <span className={`rounded px-1.5 py-0.5 text-xs ${meta.style}`}>
                    {meta.label}
                  </span>
                )}
              </div>
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-100 text-left text-xs text-gray-400">
                    <th className="pb-1 font-medium">Developer</th>
                    <th className="pb-1 font-medium text-center">Done/Committed</th>
                    <th className="pb-1 font-medium text-center">Completion</th>
                    <th className="pb-1 font-medium text-center">Avg days/ticket</th>
                    <th className="pb-1 font-medium text-center">On time</th>
                    <th className="pb-1 font-medium text-center">Churn</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {sprintRows.map((r) => (
                    <tr key={`${r.developer}-${r.sprint}`} className="hover:bg-gray-50">
                      <td className="py-1.5 font-semibold text-gray-800">{r.developer}</td>
                      <td className="py-1.5 text-center text-gray-600">
                        {r.completed}/{r.assigned}
                      </td>
                      <td className="py-1.5 text-center">
                        <RatioBadge ratio={r.completion_ratio} />
                      </td>
                      <td className="py-1.5 text-center text-gray-600">
                        {r.avg_cycle_time_days.toFixed(1)}d
                      </td>
                      <td className="py-1.5 text-center">
                        <RatioBadge ratio={r.on_time_ratio} />
                      </td>
                      <td className="py-1.5 text-center text-gray-600">{r.churn}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          );
        })}

      {filtered.length === 0 && (
        <p className="py-6 text-center text-sm text-gray-400">
          No data yet — waiting for Fivetran sync
        </p>
      )}
    </div>
  );
}
