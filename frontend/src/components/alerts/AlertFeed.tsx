"use client";
// Proactive Alert Feed: agent-generated warnings that appear without being asked.
// TODO: seed with GET /api/alerts, then live-append via subscribe("/api/alerts/stream").
import { Card } from "@/components/ui/Card";

export function AlertFeed() {
  return <Card title="Proactive Alerts">{/* TODO: AlertCard list */}</Card>;
}
