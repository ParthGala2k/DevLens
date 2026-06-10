import { ChatWindow } from "@/components/chat/ChatWindow";
import Link from "next/link";

export default function ChatPage() {
  return (
    <main className="min-h-screen bg-gray-50 p-6">
      <div className="mb-4 flex items-center gap-4">
        <Link href="/" className="text-sm text-blue-600 hover:underline">
          ← Dashboard
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Ask DevLens</h1>
          <p className="text-sm text-gray-500">Gemini agent · GitHub · Jira · Google Calendar · Arjun · Priya · James · Riya</p>
        </div>
      </div>
      <div className="max-w-2xl">
        <ChatWindow />
      </div>
    </main>
  );
}
