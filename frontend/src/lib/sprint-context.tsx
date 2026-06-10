"use client";

import { createContext, useContext, useState } from "react";

export interface SprintInfo {
  id: string;
  name: string;
  state: "active" | "closed" | "future";
  start_date: string | null;
  end_date: string | null;
}

interface SprintContextValue {
  selectedSprint: SprintInfo | null;
  setSelectedSprint: (s: SprintInfo | null) => void;
}

const SprintContext = createContext<SprintContextValue>({
  selectedSprint: null,
  setSelectedSprint: () => {},
});

export function SprintProvider({ children }: { children: React.ReactNode }) {
  const [selectedSprint, setSelectedSprint] = useState<SprintInfo | null>(null);
  return (
    <SprintContext.Provider value={{ selectedSprint, setSelectedSprint }}>
      {children}
    </SprintContext.Provider>
  );
}

export function useSelectedSprint() {
  return useContext(SprintContext);
}
