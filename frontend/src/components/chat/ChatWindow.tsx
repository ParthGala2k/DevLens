"use client";
// Chat interface: ask questions, see the agent's reasoning + tool calls stream in.
// TODO: POST /api/chat to start a run, then subscribe("/api/chat/{sessionId}/stream")
//       rendering thinking/tool_call/tool_result/message events inline.
import { Card } from "@/components/ui/Card";

export function ChatWindow() {
  return <Card title="Ask DevLens">{/* TODO: messages + input + tool-call rendering */}</Card>;
}
