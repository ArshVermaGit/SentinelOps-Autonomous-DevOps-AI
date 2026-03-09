import "./globals.css"
import type { Metadata } from "next"
import LayoutWrapper from "@/components/layout/LayoutWrapper"

export const metadata: Metadata = {
  title: "SentinelOps | DevOps AI Co-Pilot by Arsh Verma",
  description: "Autonomous Engineering Decision Intelligence",
  icons: {
    icon: "/favicon.ico",
  },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <head>
        <link rel="icon" href="/logo.png" />
      </head>
      <body className={`font-sans bg-[#0a0f1e] text-white min-h-screen`}>
        <LayoutWrapper>{children}</LayoutWrapper>
      </body>
    </html>
  )
}
