import type { Metadata } from "next";
import { Geist, Merriweather } from "next/font/google";
import "./globals.css";

const geistSans = Geist({ variable: "--font-geist-sans", subsets: ["latin"] });
const merriweather = Merriweather({ variable: "--font-heading", subsets: ["latin"], weight: ["700", "900"] });

export const metadata: Metadata = {
  title: "Jean Tote Inventory",
  description: "Scan-first tote inventory for Jean&apos;s storage boxes.",
  icons: { icon: "/favicon.svg", shortcut: "/favicon.svg" },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${merriweather.variable}`}>{children}</body>
    </html>
  );
}
