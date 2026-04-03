import type { Metadata } from "next";
import { GeistSans } from "geist/font/sans";
import { GeistMono } from "geist/font/mono";
import "./globals.css";
import { Navbar } from "@/components/Navbar";

export const metadata: Metadata = {
  title: "SiteWatch AI — Construction Site Safety Monitoring",
  description:
    "AI-powered construction site safety monitoring platform using computer vision",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${GeistSans.variable} ${GeistMono.variable} antialiased min-h-screen bg-gray-950 text-white`}
      >
        <Navbar />
        <main>{children}</main>
      </body>
    </html>
  );
}
