"use client";

import { useEffect, useState } from "react";
import { apiGet } from "@/lib/api-client";
import { subscribe } from "@/lib/sse";
import { Card } from "@/components/ui/Card";

interface AlertRow {
  id: string;
  severity: "info" | "warning" | "critical";
  title: string;
  detail: string;
  source: string;
  created_at: string;
}

const SEVERITY_STYLES = {
  critical: "border-l-4 border-red-500 bg-red-50",
  warning: "border-l-4 border-yellow-400 bg-yellow-50",
  info: "border-l-4 border-blue-400 bg-blue-50",
};

const SEVERITY_BADGE = {
  critical: "bg-red-100 text-red-700",
  warning: "bg-yellow-100 text-yellow-700",
  info: "bg-blue-100 text-blue-700",
};

export function AlertFeed() {
  const [alerts, setAlerts] = useState<AlertRow[]>([]);

  useEffect(() => {
    apiGet<AlertRow[]>("/api/alerts").then(setAlerts).catch(() => {});
    const unsub = subscribe<AlertRow>("/api/alerts/stream", (alert) => {
      setAlerts((prev) => [alert, ...prev.filter((a) => a.id !== alert.id)]);
    });
    return unsub;
  }, []);

  return (
    <Card title="Proactive Alerts">
      <div className="space-y-2 max-h-64 overflow-y-auto">
        {alerts.map((a) => (
          <div
            key={a.id}
            className={`rounded p-2 text-sm ${SEVERITY_STYLES[a.severity] ?? SEVERITY_STYLES.info}`}
          >
            <div className="flex items-start gap-2">
              <span className={`rounded px-1.5 py-0.5 text-xs font-medium ${SEVERITY_BADGE[a.severity]}`}>
                {a.severity}
              </span>
              <div className="flex-1">
                <p className="font-medium text-gray-800">{a.title}</p>
                <p className="text-xs text-gray-600 mt-0.5">{a.detail}</p>
                <p className="text-xs text-gray-400 mt-0.5">{a.source} · {new Date(a.created_at).toLocaleString()}</p>
              </div>
            </div>
          </div>
        ))}
        {alerts.length === 0 && (
          <p className="py-4 text-center text-sm text-gray-400">No alerts yet</p>
        )}
      </div>
    </Card>
  );
}
