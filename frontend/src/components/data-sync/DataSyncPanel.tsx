"use client";

import { useEffect, useState } from "react";
import { apiGet, apiPost } from "@/lib/api-client";

interface ConnectorRow {
  id: string;
  status: string;
  last_sync_at: string | null;
}

interface SyncResult {
  connector: string;
  fivetran_id?: string;
  status: string;
  note?: string;
  error?: string;
}

const SOURCE_LABELS: Record<string, string> = {
  github:   "GitHub",
  jira:     "Jira",
  calendar: "Google Calendar",
};

const SOURCE_ICONS: Record<string, string> = {
  github:   "⑂",
  jira:     "◈",
  calendar: "◷",
};

const STATUS_BADGE: Record<string, string> = {
  connected: "bg-green-100 text-green-700 border border-green-200",
  idle:      "bg-green-100 text-green-700 border border-green-200",
  syncing:   "bg-blue-100 text-blue-700 border border-blue-200",
  error:     "bg-red-100 text-red-700 border border-red-200",
  unknown:   "bg-gray-100 text-gray-500 border border-gray-200",
};

const STATUS_LABEL: Record<string, string> = {
  connected: "Synced",
  idle:      "Synced",
  syncing:   "Syncing…",
  error:     "Error",
  unknown:   "Unknown",
};

export function DataSyncPanel() {
  const [connectors, setConnectors] = useState<ConnectorRow[]>([]);
  const [syncing, setSyncing] = useState<Record<string, boolean>>({});
  const [notes, setNotes] = useState<Record<string, string>>({});

  useEffect(() => {
    apiGet<ConnectorRow[]>("/api/connectors").then(setConnectors).catch(() => {});
  }, []);

  async function syncNow(id: string) {
    setSyncing((s) => ({ ...s, [id]: true }));
    setNotes((n) => ({ ...n, [id]: "" }));
    try {
      const result = await apiPost<SyncResult>(`/api/connectors/${id}/sync`);
      const newStatus = result?.status ?? "syncing";
      const note = result?.note ?? result?.error ?? "";
      setConnectors((prev) =>
        prev.map((c) =>
          c.id === id ? { ...c, status: newStatus, last_sync_at: new Date().toISOString() } : c
        )
      );
      if (note) setNotes((n) => ({ ...n, [id]: note }));
    } catch {
      setConnectors((prev) =>
        prev.map((c) => (c.id === id ? { ...c, status: "error" } : c))
      );
    } finally {
      setSyncing((s) => ({ ...s, [id]: false }));
    }
  }

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
      <div className="mb-3">
        <h3 className="text-sm font-semibold text-gray-800">Data Sources (Fivetran)</h3>
        <p className="text-xs text-gray-400">
          Fivetran syncs GitHub, Jira, and Google Calendar data into BigQuery every 6 hours.
          "Sync Now" triggers an immediate refresh for GitHub or confirms data is current for others.
        </p>
      </div>
      <div className="divide-y divide-gray-100">
        {connectors.map((c) => (
          <div key={c.id} className="py-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="text-base text-gray-400">{SOURCE_ICONS[c.id] ?? "⬡"}</span>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-gray-800">
                      {SOURCE_LABELS[c.id] ?? c.id}
                    </span>
                    <span className={`rounded px-1.5 py-0.5 text-xs font-medium ${STATUS_BADGE[c.status] ?? STATUS_BADGE.unknown}`}>
                      {STATUS_LABEL[c.status] ?? c.status}
                    </span>
                  </div>
                  {c.last_sync_at && (
                    <p className="text-xs text-gray-400">
                      Last sync: {new Date(c.last_sync_at).toLocaleString()}
                    </p>
                  )}
                  {notes[c.id] && (
                    <p className="mt-0.5 text-xs text-gray-400 italic">{notes[c.id]}</p>
                  )}
                </div>
              </div>
              <button
                onClick={() => syncNow(c.id)}
                disabled={syncing[c.id]}
                className="rounded-lg border border-gray-200 bg-gray-50 px-3 py-1.5 text-xs font-medium text-gray-600 hover:bg-gray-100 disabled:opacity-40 transition-colors"
              >
                {syncing[c.id] ? "Syncing…" : "Sync Now"}
              </button>
            </div>
          </div>
        ))}
        {connectors.length === 0 && (
          <p className="py-4 text-center text-sm text-gray-400">Loading connectors…</p>
        )}
      </div>
    </div>
  );
}
