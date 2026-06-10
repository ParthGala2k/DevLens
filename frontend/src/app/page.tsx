import { InsightCards } from "@/components/alerts/InsightCards";
import { ChatWindow } from "@/components/chat/ChatWindow";
import { DataSyncPanel } from "@/components/data-sync/DataSyncPanel";
import { SprintHealthDashboard } from "@/components/dashboard/SprintHealthDashboard";
import { McpActivityLog } from "@/components/mcp-log/McpActivityLog";
import { ProposalQueue } from "@/components/bridge/ProposalQueue";
import { WorkloadHeatmap } from "@/components/team/WorkloadHeatmap";
import { ReliabilityTable } from "@/components/team/ReliabilityTable";
import { SprintBanner } from "@/components/sprint/SprintBanner";
import { SprintPrediction } from "@/components/sprint/SprintPrediction";
import { McpCounter } from "@/components/mcp-log/McpCounter";

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">

      {/* ── Header ─────────────────────────────────────────────────── */}
      <header className="sticky top-0 z-10 border-b border-gray-200 bg-white px-6 py-3 shadow-sm">
        <div className="mx-auto flex max-w-screen-2xl items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600 text-xs font-bold text-white">
              DL
            </div>
            <div>
              <span className="text-base font-semibold text-gray-900">DevLens</span>
              <span className="ml-2 text-xs text-gray-400">
                Gemini agent · developer productivity
              </span>
            </div>
          </div>
          <div className="flex items-center gap-3 text-xs">
            <span className="flex items-center gap-1.5 text-gray-500">
              <span className="h-2 w-2 rounded-full bg-green-500" />
              GitHub · Jira · Google Calendar
            </span>
            <McpCounter />
            <span className="rounded-md border border-gray-200 bg-gray-50 px-2 py-1 font-mono text-gray-600">
              stealth-labs-platform
            </span>
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-screen-2xl space-y-6 p-6">

        {/* ── Sprint timeline ─────────────────────────────────────── */}
        <SprintBanner />

        {/* ── Sprint completion prediction ─────────────────────────── */}
        <SprintPrediction />

        {/* ── Proactive agent insights ────────────────────────────── */}
        <section>
          <SectionTitle label="Agent Insights" badge="live" />
          <InsightCards />
        </section>

        {/* ── Chat + MCP log ──────────────────────────────────────── */}
        <section className="grid grid-cols-1 gap-4 lg:grid-cols-5">
          <div className="lg:col-span-3">
            <ChatWindow />
          </div>
          <div className="lg:col-span-2">
            <McpActivityLog />
          </div>
        </section>

        {/* ── Sprint health ────────────────────────────────────────── */}
        <section>
          <SectionTitle label="Sprint Health — Sprint 3: Deployment Manager (active)" />
          <SprintHealthDashboard />
        </section>

        {/* ── Team ─────────────────────────────────────────────────── */}
        <section className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <WorkloadHeatmap />
          <ReliabilityTable />
        </section>

        {/* ── Issue proposals ──────────────────────────────────────── */}
        <section>
          <SectionTitle label="Issue Proposals" />
          <ProposalQueue />
        </section>

        {/* ── Data sync ────────────────────────────────────────────── */}
        <section>
          <SectionTitle label="Data Sources (Fivetran)" />
          <DataSyncPanel />
        </section>

      </div>
    </div>
  );
}

function SectionTitle({ label, badge }: { label: string; badge?: string }) {
  return (
    <div className="mb-3 flex items-center gap-2">
      <h2 className="text-xs font-semibold uppercase tracking-widest text-gray-500">{label}</h2>
      {badge && (
        <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-700">
          {badge}
        </span>
      )}
    </div>
  );
}
