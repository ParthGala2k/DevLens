// EventSource helper for the live SSE streams (chat, alerts, mcp-log).
import { API_BASE } from "./api-client";

export function subscribe<T>(
  path: string,
  onEvent: (data: T) => void,
  onError?: (e: Event) => void,
): () => void {
  const es = new EventSource(`${API_BASE}${path}`);
  es.onmessage = (e) => {
    try {
      onEvent(JSON.parse(e.data) as T);
    } catch {
      // ignore malformed frames
    }
  };
  if (onError) es.onerror = onError;
  return () => es.close();
}
