"use client";

import { useEffect, useState } from "react";
import { apiGet } from "@/lib/api-client";
import { subscribe } from "@/lib/sse";

interface AlertRow {
  id: string;
  severity: "info" | "warning" | "critical";
  title: string;
  detail: string;
  source: string;
  created_at: string;
}

const CFG = {
  critical: {
    border: "border-red-400",
    badge: "bg-red-100 text-red-700",
    dot: "bg-red-500",
    label: "Needs action",
  },
  warning: {
    border: "border-amber-400",
    badge: "bg-amber-100 text-amber-700",
    dot: "bg-amber-400",
    label: "Watch out",
  },
  info: {
    border: "border-blue-400",
    badge: "bg-blue-100 text-blue-700",
    dot: "bg-blue-400",
    label: "FYI",
  },
};

const SOURCE_ICON: Record<string, string> = {
  github:   "⑂ GitHub",
  jira:     "◈ Jira",
  calendar: "◷ Calendar",
  cross:    "⊕ Cross",
};

export function InsightCards() {
  const [alerts, setAlerts] = useState<AlertRow[]>([]);

  useEffect(() => {
    apiGet<AlertRow[]>("/api/alerts").then(setAlerts).catch(() => {});
    const unsub = subscribe<AlertRow>("/api/alerts/stream", (alert) => {
      setAlerts((prev) => [alert, ...prev.filter((a) => a.id !== alert.id)]);
    });
    return unsub;
  }, []);

  const top3 = alerts.slice(0, 3);

  if (top3.length === 0) {
    return (
      <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-28 animate-pulse rounded-xl border border-gray-200 bg-gray-100" />
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
      {top3.map((a) => {
        const cfg = CFG[a.severity] ?? CFG.info;
        return (
          <div
            key={a.id}
            className={`rounded-xl border-l-4 bg-white px-4 py-3 shadow-sm ${cfg.border}`}
          >
            {/* Severity + source */}
            <div className="mb-2 flex items-center justify-between">
              <span className="flex items-center gap-1.5">
                <span className={`h-2 w-2 rounded-full ${cfg.dot}`} />
                <span className={`rounded px-1.5 py-0.5 text-xs font-semibold ${cfg.badge}`}>
                  {cfg.label}
                </span>
              </span>
              <span className="text-xs text-gray-400">
                {SOURCE_ICON[a.source] ?? a.source}
              </span>
            </div>

            {/* Full headline — no truncation */}
            <p className="text-sm font-semibold leading-snug text-gray-900">
              {a.title}
            </p>

            {/* Full detail — no truncation */}
            <p className="mt-1.5 text-xs leading-relaxed text-gray-500">
              {a.detail}
            </p>
          </div>
        );
      })}
    </div>
  );
}
