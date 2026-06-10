"use client";

import { useEffect, useState } from "react";
import { apiGet } from "@/lib/api-client";

interface Sprint {
  id: string;
  name: string;
  state: "active" | "closed" | "future";
  start_date: string | null;
  end_date: string | null;
}

function fmt(dateStr: string | null): string {
  if (!dateStr) return "—";
  const d = new Date(dateStr);
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

const STATE_STYLES = {
  closed: {
    dot: "bg-gray-300",
    connector: "bg-gray-200",
    name: "text-gray-500",
    dates: "text-gray-400",
    badge: "bg-gray-100 text-gray-500 border border-gray-200",
    badgeText: "✓ Done",
  },
  active: {
    dot: "bg-blue-500 ring-4 ring-blue-100",
    connector: "bg-blue-400",
    name: "text-blue-700 font-semibold",
    dates: "text-blue-500",
    badge: "bg-blue-100 text-blue-700 border border-blue-200 font-semibold",
    badgeText: "● Active",
  },
  future: {
    dot: "bg-gray-200 border-2 border-dashed border-gray-300",
    connector: "bg-gray-100 border-t border-dashed border-gray-300",
    name: "text-gray-400",
    dates: "text-gray-300",
    badge: "bg-gray-50 text-gray-400 border border-dashed border-gray-200",
    badgeText: "○ Planned",
  },
};

export function SprintBanner() {
  const [sprints, setSprints] = useState<Sprint[]>([]);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    apiGet<Sprint[]>("/api/dashboard/sprints")
      .then((data) => { setSprints(data); setLoaded(true); })
      .catch(() => setLoaded(true));
  }, []);

  if (!loaded) {
    return <div className="h-20 animate-pulse rounded-xl border border-gray-200 bg-gray-100" />;
  }

  if (sprints.length === 0) {
    return (
      <div className="rounded-xl border border-gray-200 bg-white px-6 py-4 shadow-sm text-sm text-gray-400">
        Sprint timeline — no Jira sprint data yet
      </div>
    );
  }

  const activeSprint = sprints.find((s) => s.state === "active");

  return (
    <div className="rounded-xl border border-gray-200 bg-white px-6 py-4 shadow-sm">
      <div className="mb-4 flex items-center gap-3">
        <span className="text-xs font-semibold uppercase tracking-widest text-gray-400">
          Sprint Timeline
        </span>
        {activeSprint && (
          <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs font-semibold text-blue-700">
            {activeSprint.name} active
          </span>
        )}
        {activeSprint?.end_date && (
          <span className="text-xs text-gray-400">
            ends {fmt(activeSprint.end_date)}
          </span>
        )}
      </div>

      <div className="flex items-start">
        {sprints.map((sprint, i) => {
          const cfg = STATE_STYLES[sprint.state] ?? STATE_STYLES.future;
          const isLast = i === sprints.length - 1;
          return (
            <div key={sprint.id} className="flex flex-1 flex-col items-start">
              {/* Timeline track + dot */}
              <div className="flex w-full items-center">
                <div className={`h-3 w-3 shrink-0 rounded-full ${cfg.dot}`} />
                {!isLast && <div className={`h-0.5 flex-1 ${cfg.connector}`} />}
              </div>
              {/* Labels */}
              <div className="mt-2 pr-3">
                <p className={`text-xs font-medium ${cfg.name}`}>{sprint.name}</p>
                {sprint.start_date && sprint.end_date && (
                  <p className={`text-xs ${cfg.dates}`}>
                    {fmt(sprint.start_date)} – {fmt(sprint.end_date)}
                  </p>
                )}
                <span className={`mt-1 inline-block rounded px-1.5 py-0.5 text-xs ${cfg.badge}`}>
                  {cfg.badgeText}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
