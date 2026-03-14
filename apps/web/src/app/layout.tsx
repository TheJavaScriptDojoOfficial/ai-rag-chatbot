import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Company RAG Chatbot",
  description: "Local AI RAG chatbot — foundation",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
