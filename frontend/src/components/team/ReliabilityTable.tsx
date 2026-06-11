"use client";

import { useEffect, useState } from "react";
import { apiGet } from "@/lib/api-client";

interface ReliabilityRow {
  developer: string;
  assigned: number;
  completed: number;
  completion_ratio: number;
  avg_cycle_time_days: number;
  on_time_ratio: number;
  churn: number;
}

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

  useEffect(() => {
    apiGet<ReliabilityRow[]>("/api/team/reliability").then(setRows).catch(() => {});
  }, []);

  const sorted = [...rows].sort((a, b) => b.completion_ratio - a.completion_ratio);

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
      <h3 className="mb-1 text-sm font-semibold text-gray-800">Completion Reliability</h3>
      <p className="mb-3 text-xs text-gray-400">
        Did each developer finish what they committed to this sprint cycle?
        Completion % = tickets done ÷ tickets committed. On-time = resolved before sprint end.
      </p>

      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-100 text-left text-xs text-gray-400">
            <th className="pb-2 font-medium">Developer</th>
            <th className="pb-2 font-medium text-center">Done / Committed</th>
            <th className="pb-2 font-medium text-center">Completion</th>
            <th className="pb-2 font-medium text-center">Avg days/ticket</th>
            <th className="pb-2 font-medium text-center">On time</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-50">
          {sorted.map((r) => (
            <tr key={r.developer} className="hover:bg-gray-50">
              <td className="py-2 font-semibold text-gray-800">{r.developer}</td>
              <td className="py-2 text-center text-gray-600">
                {r.completed}/{r.assigned}
              </td>
              <td className="py-2 text-center">
                <RatioBadge ratio={r.completion_ratio} />
              </td>
              <td className="py-2 text-center text-gray-600">
                {r.avg_cycle_time_days.toFixed(1)}d
              </td>
              <td className="py-2 text-center">
                <RatioBadge ratio={r.on_time_ratio} />
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
  );
}
