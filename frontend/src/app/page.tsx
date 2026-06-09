import { DataSyncPanel } from "@/components/data-sync/DataSyncPanel";
import { SprintHealthDashboard } from "@/components/dashboard/SprintHealthDashboard";
import { WorkloadHeatmap } from "@/components/team/WorkloadHeatmap";
import { ReliabilityTable } from "@/components/team/ReliabilityTable";
import { ProposalQueue } from "@/components/bridge/ProposalQueue";
import { AlertFeed } from "@/components/alerts/AlertFeed";
import { McpActivityLog } from "@/components/mcp-log/McpActivityLog";
import Link from "next/link";

export default function DashboardPage() {
  return (
    <main className="min-h-screen bg-gray-50 p-6">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">DevLens</h1>
          <p className="text-sm text-gray-500">Developer Productivity Blind Spot Agent · itsRenuka22/stealth-labs-platform</p>
        </div>
        <Link
          href="/chat"
          className="rounded bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700"
        >
          Ask DevLens →
        </Link>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <DataSyncPanel />
          <SprintHealthDashboard />
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <WorkloadHeatmap />
            <ReliabilityTable />
          </div>
          <ProposalQueue />
          <AlertFeed />
        </div>
        <aside className="lg:col-span-1">
          <McpActivityLog />
        </aside>
      </div>
    </main>
  );
}
