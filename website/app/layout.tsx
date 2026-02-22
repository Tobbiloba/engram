import type { Metadata } from "next";
import { Geist_Mono } from "next/font/google";
import "./globals.css";

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Engram | Your AI Finally Remembers",
  description: "Persistent context for your codebase. Architecture decisions, recent changes, and project intent—available in every AI conversation.",
  openGraph: {
    title: "Engram | Your AI Finally Remembers",
    description: "Persistent context for your codebase. Architecture decisions, recent changes, and project intent—available in every AI conversation.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${geistMono.variable} antialiased`}>
        {children}
      </body>
    </html>
  );
}
