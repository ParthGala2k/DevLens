"use client";

import { useEffect, useState } from "react";
import { apiGet } from "@/lib/api-client";

interface Prediction {
  sprint_name: string;
  end_date: string;
  days_remaining: number;
  total_days: number;
  done_pts: number;
  total_pts: number;
  done_count: number;
  total_count: number;
  current_pct: number;
  predicted_pct: number;
  velocity_per_day: number;
}

function fmt(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

export function SprintPrediction() {
  const [data, setData] = useState<Prediction | null>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    apiGet<Prediction>("/api/dashboard/sprint-prediction")
      .then((d) => { setData(Object.keys(d).length ? d : null); setLoaded(true); })
      .catch(() => setLoaded(true));
  }, []);

  if (!loaded) {
    return <div className="h-14 animate-pulse rounded-xl border border-gray-200 bg-gray-100" />;
  }
  if (!data) return null;

  const isActive  = data.days_remaining > 0;
  const pct       = isActive ? data.predicted_pct : data.current_pct;
  const onTrack   = pct >= 80;
  const atRisk    = pct >= 60 && pct < 80;
  // colour scheme
  const barColor  = onTrack ? "bg-green-500" : atRisk ? "bg-amber-400" : "bg-red-500";
  const textColor = onTrack ? "text-green-700" : atRisk ? "text-amber-700" : "text-red-700";
  const bgColor   = onTrack ? "bg-green-50 border-green-200" : atRisk ? "bg-amber-50 border-amber-200" : "bg-red-50 border-red-200";
  const icon      = onTrack ? "✓" : atRisk ? "⚠" : "✗";

  const sentence = isActive
    ? `At current velocity (${data.velocity_per_day} pts/day), ${data.sprint_name} will complete approximately ${pct}% of committed points by ${fmt(data.end_date)}.`
    : `${data.sprint_name} closed with ${pct}% of committed points completed — ${data.done_pts} of ${data.total_pts} story points, ${data.done_count} of ${data.total_count} tickets.`;

  return (
    <div className={`flex items-center gap-4 rounded-xl border px-5 py-3.5 ${bgColor}`}>
      {/* Icon + sentence */}
      <span className={`shrink-0 text-lg font-bold ${textColor}`}>{icon}</span>
      <p className={`flex-1 text-sm font-medium ${textColor}`}>{sentence}</p>

      {/* Progress bar + stats */}
      <div className="hidden shrink-0 flex-col items-end gap-1 sm:flex">
        <div className="flex items-center gap-2">
          <div className="h-2 w-32 overflow-hidden rounded-full bg-white/60">
            <div
              className={`h-full rounded-full transition-all duration-700 ${barColor}`}
              style={{ width: `${pct}%` }}
            />
          </div>
          <span className={`w-10 text-right text-sm font-bold ${textColor}`}>{pct}%</span>
        </div>
        <span className="text-xs text-gray-400">
          {data.done_pts} / {data.total_pts} pts · {data.velocity_per_day} pts/day
        </span>
      </div>
    </div>
  );
}
