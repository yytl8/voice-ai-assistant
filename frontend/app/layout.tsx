import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Voice AI Assistant",
  description: "Real-time Arabic voice AI assistant",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ar" dir="rtl">
      <body>{children}</body>
    </html>
  );
}
