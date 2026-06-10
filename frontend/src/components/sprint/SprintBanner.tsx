"use client";

import { useEffect, useState } from "react";
import { apiGet } from "@/lib/api-client";
import { useSelectedSprint, SprintInfo } from "@/lib/sprint-context";

function fmt(dateStr: string | null): string {
  if (!dateStr) return "—";
  const d = new Date(dateStr);
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

const STATE_STYLES = {
  closed: {
    dot: "bg-gray-300",
    dotSelected: "bg-gray-500 ring-4 ring-gray-200",
    connector: "bg-gray-200",
    name: "text-gray-500",
    dates: "text-gray-400",
    badge: "bg-gray-100 text-gray-500 border border-gray-200",
    badgeText: "✓ Done",
  },
  active: {
    dot: "bg-blue-500 ring-4 ring-blue-100",
    dotSelected: "bg-blue-700 ring-4 ring-blue-300",
    connector: "bg-blue-400",
    name: "text-blue-700 font-semibold",
    dates: "text-blue-500",
    badge: "bg-blue-100 text-blue-700 border border-blue-200 font-semibold",
    badgeText: "● Active",
  },
  future: {
    dot: "bg-gray-200 border-2 border-dashed border-gray-300",
    dotSelected: "bg-gray-400 ring-4 ring-gray-200",
    connector: "bg-gray-100 border-t border-dashed border-gray-300",
    name: "text-gray-400",
    dates: "text-gray-300",
    badge: "bg-gray-50 text-gray-400 border border-dashed border-gray-200",
    badgeText: "○ Planned",
  },
};

export function SprintBanner() {
  const [sprints, setSprints] = useState<SprintInfo[]>([]);
  const [loaded, setLoaded] = useState(false);
  const { selectedSprint, setSelectedSprint } = useSelectedSprint();

  useEffect(() => {
    apiGet<SprintInfo[]>("/api/dashboard/sprints")
      .then((data) => {
        setSprints(data);
        setLoaded(true);
        // Default-select the active sprint
        const active = data.find((s) => s.state === "active");
        if (active) setSelectedSprint(active);
      })
      .catch(() => setLoaded(true));
  // eslint-disable-next-line react-hooks/exhaustive-deps
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

  return (
    <div className="rounded-xl border border-gray-200 bg-white px-6 py-4 shadow-sm">
      <div className="mb-4 flex items-center gap-3">
        <span className="text-xs font-semibold uppercase tracking-widest text-gray-400">
          Sprint Timeline
        </span>
        {selectedSprint && (
          <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs font-semibold text-blue-700">
            {selectedSprint.name}
          </span>
        )}
        {selectedSprint?.end_date && (
          <span className="text-xs text-gray-400">
            {selectedSprint.state === "active" ? "ends" : "ended"} {fmt(selectedSprint.end_date)}
          </span>
        )}
        <span className="ml-auto text-xs text-gray-300">Click a sprint to filter the dashboard</span>
      </div>

      <div className="flex items-start">
        {sprints.map((sprint, i) => {
          const cfg = STATE_STYLES[sprint.state] ?? STATE_STYLES.future;
          const isLast = i === sprints.length - 1;
          const isSelected = selectedSprint?.id === sprint.id;
          return (
            <div
              key={sprint.id}
              className="flex flex-1 flex-col items-start cursor-pointer group"
              onClick={() => setSelectedSprint(isSelected ? null : sprint)}
            >
              {/* Timeline track + dot */}
              <div className="flex w-full items-center">
                <div
                  className={`h-3 w-3 shrink-0 rounded-full transition-all ${
                    isSelected ? cfg.dotSelected : cfg.dot
                  } group-hover:scale-125`}
                />
                {!isLast && <div className={`h-0.5 flex-1 ${cfg.connector}`} />}
              </div>
              {/* Labels */}
              <div
                className={`mt-2 pr-3 rounded-lg transition-colors ${
                  isSelected ? "bg-blue-50 px-2 py-1 -mx-2" : ""
                }`}
              >
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
