/**
 * Chat page — natural-language questions answered by the agent, with visible tool calls.
 * TODO: render <ChatWindow /> and wire it to the /api/chat SSE stream via lib/sse.ts.
 */
export default function ChatPage() {
  return (
    <main className="min-h-screen p-6">
      <h1 className="text-2xl font-semibold">Ask DevLens</h1>
      {/* <ChatWindow /> */}
      <div className="mt-6 rounded border border-dashed p-8 text-center text-gray-400">
        Chat window goes here
      </div>
    </main>
  );
}
