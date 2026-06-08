"use client";
// Developer observability: per-dev load score as a heatmap, to spot who's overloaded.
// TODO: GET /api/team/workload; render a grid colored by loadScore.
import { Card } from "@/components/ui/Card";

export function WorkloadHeatmap() {
  return <Card title="Team Workload">{/* TODO: load heatmap */}</Card>;
}
