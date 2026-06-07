"use client";
// Sprint Health Dashboard: PR review lag, deep work vs meetings, estimation accuracy.
// TODO: three Recharts charts fed by GET /api/dashboard/{pr-review-lag,deep-work,estimation-accuracy}.
import { Card } from "@/components/ui/Card";

export function SprintHealthDashboard() {
  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
      <Card title="PR Review Lag">{/* TODO */}</Card>
      <Card title="Deep Work vs Meetings">{/* TODO */}</Card>
      <Card title="Estimation Accuracy">{/* TODO */}</Card>
    </div>
  );
}
