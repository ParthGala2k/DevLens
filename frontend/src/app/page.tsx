/**
 * Dashboard home — composes the four panels + the live MCP activity log.
 * TODO: replace placeholders with the real components from src/components/*.
 */
export default function DashboardPage() {
  return (
    <main className="min-h-screen p-6">
      <h1 className="text-2xl font-semibold">Sprint Mirror / DevLens</h1>
      <p className="text-sm text-gray-500">Developer Productivity Blind Spot Agent</p>

      <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-3">
        <section className="lg:col-span-2 space-y-6">
          {/* <DataSyncPanel /> */}
          {/* <SprintHealthDashboard /> */}
          {/* <AlertFeed /> */}
          <div className="rounded border border-dashed p-8 text-center text-gray-400">
            Data Sync + Sprint Health + Alert Feed go here
          </div>
        </section>
        <aside>
          {/* <McpActivityLog />  — judge-visible live MCP calls */}
          <div className="rounded border border-dashed p-8 text-center text-gray-400">
            MCP Activity Log
          </div>
        </aside>
      </div>
    </main>
  );
}
