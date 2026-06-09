"use client";

import { useEffect, useState } from "react";
import { apiGet, apiPost } from "@/lib/api-client";
import { Card } from "@/components/ui/Card";

interface ConnectorRow {
  id: string;
  status: string;
  last_sync_at: string | null;
}

const SOURCE_LABELS: Record<string, string> = {
  github: "GitHub",
  jira: "Jira",
  slack: "Slack",
  calendar: "Google Calendar",
  pagerduty: "PagerDuty",
};

const STATUS_COLORS: Record<string, string> = {
  connected: "bg-green-100 text-green-800",
  syncing: "bg-yellow-100 text-yellow-800",
  error: "bg-red-100 text-red-800",
  unknown: "bg-gray-100 text-gray-600",
};

export function DataSyncPanel() {
  const [connectors, setConnectors] = useState<ConnectorRow[]>([]);
  const [syncing, setSyncing] = useState<Record<string, boolean>>({});

  useEffect(() => {
    apiGet<ConnectorRow[]>("/api/connectors")
      .then(setConnectors)
      .catch(() => {});
  }, []);

  async function syncNow(id: string) {
    setSyncing((s) => ({ ...s, [id]: true }));
    try {
      await apiPost(`/api/connectors/${id}/sync`);
      setConnectors((prev) =>
        prev.map((c) => (c.id === id ? { ...c, status: "syncing", last_sync_at: new Date().toISOString() } : c))
      );
    } catch {
      // ignore
    } finally {
      setSyncing((s) => ({ ...s, [id]: false }));
    }
  }

  return (
    <Card title="Data Sources (Fivetran)">
      <div className="divide-y">
        {connectors.map((c) => (
          <div key={c.id} className="flex items-center justify-between py-2">
            <div>
              <span className="font-medium text-sm">{SOURCE_LABELS[c.id] ?? c.id}</span>
              <span
                className={`ml-2 rounded px-1.5 py-0.5 text-xs font-medium ${STATUS_COLORS[c.status] ?? STATUS_COLORS.unknown}`}
              >
                {c.status}
              </span>
              {c.last_sync_at && (
                <span className="ml-2 text-xs text-gray-400">
                  {new Date(c.last_sync_at).toLocaleString()}
                </span>
              )}
            </div>
            <button
              onClick={() => syncNow(c.id)}
              disabled={syncing[c.id]}
              className="rounded bg-blue-600 px-2 py-1 text-xs text-white hover:bg-blue-700 disabled:opacity-50"
            >
              {syncing[c.id] ? "Syncing…" : "Sync Now"}
            </button>
          </div>
        ))}
        {connectors.length === 0 && (
          <p className="py-4 text-center text-sm text-gray-400">Loading connectors…</p>
        )}
      </div>
    </Card>
  );
}
