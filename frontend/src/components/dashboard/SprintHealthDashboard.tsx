"use client";

import { useEffect, useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  CartesianGrid, ReferenceLine, Legend, LabelList, Cell,
} from "recharts";
import { apiGet } from "@/lib/api-client";
import { useSelectedSprint } from "@/lib/sprint-context";

interface PrLagRow {
  pr_number: number;
  title: string;
  author: string;
  sprint?: string;
  days_open: number;
}

interface DeepWorkRow {
  day: string;
  developer: string;
  deep_work_hours: number;
  meeting_hours: number;
}

interface EstimationRow {
  sprint: string;
  developer: string;
  estimated_points: number;
  completed_points: number;
  accuracy_ratio: number;
}

// Colours for sprints in the estimation chart.
const SPRINT_COLORS = ["#6366f1", "#f59e0b", "#10b981", "#ef4444"];

export function SprintHealthDashboard() {
  const [lag, setLag] = useState<PrLagRow[]>([]);
  const [deepWork, setDeepWork] = useState<DeepWorkRow[]>([]);
  const [estimation, setEstimation] = useState<EstimationRow[]>([]);
  const { selectedSprint } = useSelectedSprint();

  useEffect(() => {
    apiGet<PrLagRow[]>("/api/dashboard/pr-review-lag").then(setLag).catch(() => {});
    apiGet<DeepWorkRow[]>("/api/dashboard/deep-work").then(setDeepWork).catch(() => {});
    apiGet<EstimationRow[]>("/api/dashboard/estimation-accuracy").then(setEstimation).catch(() => {});
  }, []);

  // Canonical team roster — developers without calendar data show 8h focus / 0 meetings.
  const TEAM = ["Arjun", "James", "Priya", "Riya"];

  // ── Sprint-based date filtering ───────────────────────────────────────────
  const sprintStart = selectedSprint?.start_date ?? null;
  const sprintEnd = selectedSprint?.end_date ?? null;

  const deepWorkFiltered = deepWork.filter((r) => {
    if (!sprintStart || !sprintEnd) return true;
    const day = typeof r.day === "string" ? r.day : String(r.day);
    return day >= sprintStart.slice(0, 10) && day <= sprintEnd.slice(0, 10);
  });

  // Derive sprint label used in estimation rows (e.g. "SLS Sprint 1") by matching sprint number
  const selectedSprintNum = selectedSprint?.name.match(/\d+/)?.[0] ?? null;
  const sprintLabel = selectedSprintNum
    ? estimation.find((r) => r.sprint.match(/\d+/)?.[0] === selectedSprintNum)?.sprint ?? null
    : null;

  const estimationFiltered = sprintLabel
    ? estimation.filter((r) => r.sprint === sprintLabel)
    : estimation;

  // ── Deep work: average per developer across all dates ─────────────────────
  const dwAgg = deepWorkFiltered.reduce<
    Record<string, { developer: string; deep_work_hours: number; meeting_hours: number; days: number }>
  >((acc, r) => {
    if (!acc[r.developer]) {
      acc[r.developer] = { developer: r.developer, deep_work_hours: 0, meeting_hours: 0, days: 0 };
    }
    acc[r.developer].deep_work_hours += r.deep_work_hours;
    acc[r.developer].meeting_hours += r.meeting_hours;
    acc[r.developer].days += 1;
    return acc;
  }, {});

  const dwByDev = TEAM.map((name) => {
    const d = dwAgg[name];
    if (d && d.days > 0) {
      return {
        developer: name,
        "Deep work": parseFloat((d.deep_work_hours / d.days).toFixed(1)),
        "Meetings": parseFloat((d.meeting_hours / d.days).toFixed(1)),
      };
    }
    // No calendar data — show full focus day as baseline
    return { developer: name, "Deep work": 8.0, "Meetings": 0.0 };
  });

  // ── Estimation: pivot to one row per developer, one column per sprint ─────
  const sprints = Array.from(new Set(estimationFiltered.map((r) => r.sprint))).sort();
  const devs = Array.from(new Set(estimationFiltered.map((r) => r.developer)));
  const estByDev = devs.map((dev) => {
    const row: Record<string, unknown> = { developer: dev };
    sprints.forEach((s) => {
      const match = estimationFiltered.find((r) => r.developer === dev && r.sprint === s);
      row[s] = match ? parseFloat(match.accuracy_ratio.toFixed(2)) : null;
    });
    return row;
  });

  // ── PR lag: shape data for horizontal bar chart ───────────────────────────
  const lagChartData = lag.slice(0, 6).map((r) => ({
    label: `#${r.pr_number} ${r.title.replace(/^\[.*?\]\s*/, "").slice(0, 28)}${r.title.length > 28 ? "…" : ""}`,
    days: parseFloat(r.days_open.toFixed(1)),
    author: r.author,
    full_title: r.title,
    color: r.days_open >= 5 ? "#ef4444" : r.days_open >= 2 ? "#f59e0b" : "#22c55e",
  }));
  const lagMax = Math.max(...lagChartData.map((r) => r.days), 1);

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-3">

      {/* ── PR Review Lag ──────────────────────────────────────────── */}
      <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
        <h3 className="mb-1 text-sm font-semibold text-gray-800">PR Review Lag</h3>
        <p className="mb-3 text-xs text-gray-400">
          Days each open PR has been waiting for a reviewer.
          Green &lt; 2 d · Amber 2–5 d · Red &gt; 5 d
        </p>
        {lagChartData.length > 0 ? (
          <ResponsiveContainer width="100%" height={lagChartData.length * 44 + 16}>
            <BarChart
              data={lagChartData}
              layout="vertical"
              margin={{ top: 0, right: 40, left: 0, bottom: 0 }}
              barSize={16}
            >
              <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f0f0f0" />
              <XAxis
                type="number"
                domain={[0, lagMax + 0.5]}
                tick={{ fontSize: 10, fill: "#9ca3af" }}
                axisLine={false}
                tickLine={false}
                tickFormatter={(v) => `${v}d`}
              />
              <YAxis
                type="category"
                dataKey="label"
                width={130}
                tick={{ fontSize: 10, fill: "#6b7280" }}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip
                cursor={{ fill: "#f9fafb" }}
                content={({ active, payload }) => {
                  if (!active || !payload?.length) return null;
                  const d = payload[0].payload;
                  return (
                    <div className="rounded-lg border border-gray-200 bg-white p-2 text-xs shadow-lg">
                      <p className="font-semibold text-gray-800">{d.full_title}</p>
                      <p className="text-gray-500">by {d.author}</p>
                      <p className="mt-1 font-bold" style={{ color: d.color }}>{d.days}d waiting</p>
                    </div>
                  );
                }}
              />
              <Bar dataKey="days" radius={[0, 4, 4, 0]}>
                {lagChartData.map((entry, i) => (
                  <Cell key={i} fill={entry.color} />
                ))}
                <LabelList
                  dataKey="days"
                  position="right"
                  formatter={(v: number) => `${v}d`}
                  style={{ fontSize: 10, fill: "#6b7280", fontWeight: 600 }}
                />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <p className="text-sm text-gray-400">No open PRs awaiting review</p>
        )}
      </div>

      {/* ── Deep Work vs Meetings ───────────────────────────────────── */}
      <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
        <h3 className="mb-1 text-sm font-semibold text-gray-800">Deep Work vs Meetings</h3>
        <p className="mb-3 text-xs text-gray-400">
          Average hours/day spent in uninterrupted coding vs in meetings.
          More "deep work" = more focus time to ship.
        </p>
        {dwByDev.length > 0 ? (
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={dwByDev} margin={{ top: 4, right: 8, left: -8, bottom: 0 }} barGap={2}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
              <XAxis
                dataKey="developer"
                tick={{ fontSize: 11, fill: "#6b7280" }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                tick={{ fontSize: 11, fill: "#6b7280" }}
                axisLine={false}
                tickLine={false}
                label={{ value: "hrs/day", angle: -90, position: "insideLeft", offset: 14, style: { fontSize: 10, fill: "#9ca3af" } }}
              />
              <Tooltip
                formatter={(v: number, name: string) => [`${v}h`, name]}
                contentStyle={{ fontSize: 12, borderRadius: 8, border: "1px solid #e5e7eb" }}
              />
              <Legend wrapperStyle={{ fontSize: 11 }} />
              <Bar dataKey="Deep work" fill="#3b82f6" radius={[3, 3, 0, 0]} maxBarSize={28} />
              <Bar dataKey="Meetings" fill="#f59e0b" radius={[3, 3, 0, 0]} maxBarSize={28} />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <p className="text-sm text-gray-400">No data</p>
        )}
      </div>

      {/* ── Estimation Accuracy ─────────────────────────────────────── */}
      <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
        <h3 className="mb-1 text-sm font-semibold text-gray-800">Estimation Accuracy</h3>
        <p className="mb-3 text-xs text-gray-400">
          Ratio of points completed ÷ points estimated per sprint.
          <strong className="text-gray-600"> 1.0 = perfect</strong>,{" "}
          {"<"}1.0 = under-delivered, {">"}1.0 = over-delivered.
          Grouped by sprint.
        </p>
        {estByDev.length > 0 ? (
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={estByDev} margin={{ top: 4, right: 8, left: -8, bottom: 0 }} barGap={2}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
              <XAxis
                dataKey="developer"
                tick={{ fontSize: 11, fill: "#6b7280" }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                domain={[0, 1.5]}
                tick={{ fontSize: 11, fill: "#6b7280" }}
                axisLine={false}
                tickLine={false}
                label={{ value: "ratio", angle: -90, position: "insideLeft", offset: 14, style: { fontSize: 10, fill: "#9ca3af" } }}
              />
              <Tooltip
                formatter={(v: number, name: string) => [
                  v != null ? `${(v * 100).toFixed(0)}%` : "—",
                  name.replace("SLS Sprint ", "Sprint "),
                ]}
                contentStyle={{ fontSize: 12, borderRadius: 8, border: "1px solid #e5e7eb" }}
              />
              <Legend
                formatter={(v) => v.replace("SLS Sprint ", "Sprint ")}
                wrapperStyle={{ fontSize: 11 }}
              />
              {/* Green dashed reference line at 1.0 = "on target" */}
              <ReferenceLine y={1} stroke="#10b981" strokeDasharray="4 2" label={{ value: "target", position: "right", fontSize: 10, fill: "#10b981" }} />
              {sprints.map((s, i) => (
                <Bar
                  key={s}
                  dataKey={s}
                  name={s}
                  fill={SPRINT_COLORS[i % SPRINT_COLORS.length]}
                  radius={[3, 3, 0, 0]}
                  maxBarSize={22}
                />
              ))}
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <p className="text-sm text-gray-400">No data</p>
        )}
      </div>

    </div>
  );
}
