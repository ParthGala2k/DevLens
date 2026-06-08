import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DevLens",
  description: "Developer Productivity Blind Spot Agent",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
