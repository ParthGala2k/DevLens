"use client";

import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { apiGet } from "@/lib/api-client";
import { Card } from "@/components/ui/Card";

interface PrLagRow {
  pr_number: number;
  title: string;
  author: string;
  days_open: number;
}

interface DeepWorkRow {
  date: string;
  developer: string;
  deep_work_hours: number;
  meeting_hours: number;
}

interface EstimationRow {
  sprint: string;
  developer: string;
  accuracy_ratio: number;
}

export function SprintHealthDashboard() {
  const [lag, setLag] = useState<PrLagRow[]>([]);
  const [deepWork, setDeepWork] = useState<DeepWorkRow[]>([]);
  const [estimation, setEstimation] = useState<EstimationRow[]>([]);

  useEffect(() => {
    apiGet<PrLagRow[]>("/api/dashboard/pr-review-lag").then(setLag).catch(() => {});
    apiGet<DeepWorkRow[]>("/api/dashboard/deep-work").then(setDeepWork).catch(() => {});
    apiGet<EstimationRow[]>("/api/dashboard/estimation-accuracy").then(setEstimation).catch(() => {});
  }, []);

  // Aggregate deep-work data by developer for the chart.
  const dwByDev = Object.values(
    deepWork.reduce<Record<string, { developer: string; deep_work_hours: number; meeting_hours: number }>>(
      (acc, r) => {
        if (!acc[r.developer]) acc[r.developer] = { developer: r.developer, deep_work_hours: 0, meeting_hours: 0 };
        acc[r.developer].deep_work_hours += r.deep_work_hours;
        acc[r.developer].meeting_hours += r.meeting_hours;
        return acc;
      },
      {}
    )
  );

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
      <Card title="PR Review Lag">
        <div className="space-y-2">
          {lag.slice(0, 5).map((r) => (
            <div key={r.pr_number} className="flex justify-between text-sm">
              <span className="truncate text-gray-700">
                #{r.pr_number} <span className="text-gray-500">{r.author}</span>
              </span>
              <span
                className={`ml-2 font-medium ${r.days_open >= 5 ? "text-red-600" : "text-yellow-600"}`}
              >
                {r.days_open.toFixed(1)}d
              </span>
            </div>
          ))}
          {lag.length === 0 && <p className="text-sm text-gray-400">No data</p>}
        </div>
      </Card>

      <Card title="Deep Work vs Meetings">
        {dwByDev.length > 0 ? (
          <ResponsiveContainer width="100%" height={160}>
            <BarChart data={dwByDev} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="developer" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="deep_work_hours" name="Deep Work" fill="#3b82f6" stackId="a" />
              <Bar dataKey="meeting_hours" name="Meetings" fill="#f59e0b" stackId="a" />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <p className="text-sm text-gray-400">No data</p>
        )}
      </Card>

      <Card title="Estimation Accuracy">
        {estimation.length > 0 ? (
          <ResponsiveContainer width="100%" height={160}>
            <BarChart data={estimation} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="developer" tick={{ fontSize: 11 }} />
              <YAxis domain={[0, 2]} tick={{ fontSize: 11 }} />
              <Tooltip formatter={(v: number) => v.toFixed(2)} />
              <Bar dataKey="accuracy_ratio" name="Accuracy Ratio" fill="#10b981" />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <p className="text-sm text-gray-400">No data</p>
        )}
      </Card>
    </div>
  );
}
