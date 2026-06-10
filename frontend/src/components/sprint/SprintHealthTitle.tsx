"use client";

import { useSelectedSprint } from "@/lib/sprint-context";

export function SprintHealthTitle() {
  const { selectedSprint } = useSelectedSprint();
  const label = selectedSprint
    ? `Sprint Health — ${selectedSprint.name}${selectedSprint.state === "active" ? " (active)" : ""}`
    : "Sprint Health";

  return (
    <div className="mb-3 flex items-center gap-2">
      <h2 className="text-xs font-semibold uppercase tracking-widest text-gray-500">{label}</h2>
    </div>
  );
}
