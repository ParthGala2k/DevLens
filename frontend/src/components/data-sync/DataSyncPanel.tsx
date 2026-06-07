"use client";
// Data Sync Panel: lists connectors with last-sync + status, and a "Sync Now" button
// that triggers a Fivetran MCP sync (POST /api/connectors/{id}/sync).
// TODO: fetch GET /api/connectors; render ConnectorCard per source; wire SyncNowButton.
import { Card } from "@/components/ui/Card";

export function DataSyncPanel() {
  return <Card title="Data Sources">{/* TODO: connector cards */}</Card>;
}
