import type { Metadata } from "next";
import "./styles.css";
import { LivePageShell } from "./components/live/LivePageShell";
import { getPublicSnapshot } from "../lib/live/snapshot";

export const metadata: Metadata = {
  metadataBase: new URL("https://www.clearglassinc.com/"),
  applicationName: "ClearGlass Inc.",
  title: "ClearGlass Inc. | Governed AI Automation & Cybersecurity",
  description:
    "ClearGlass Inc. builds governed AI automation, cybersecurity, agent systems, OSINT workflows, and enterprise technology architectures with human approval and auditability.",
  alternates: { canonical: "/" },
  openGraph: {
    title: "ClearGlass Inc. | Governed AI Automation & Cybersecurity",
    description:
      "Governed AI automation, cybersecurity, agent systems, OSINT workflows, and enterprise technology architecture from ClearGlass Inc.",
    type: "website",
    url: "/",
    siteName: "ClearGlass Inc.",
  },
  twitter: {
    card: "summary_large_image",
    title: "ClearGlass Inc. | Governed AI Automation & Cybersecurity",
    description:
      "Governed AI automation, cybersecurity, agent systems, OSINT workflows, and enterprise technology architecture.",
  },
  robots: {
    index: true,
    follow: true,
  },
  other: {
    "dcterms.rightsHolder": "ClearGlass Inc.",
    "content-origin": "ClearGlass Inc.",
  },
};

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body><LivePageShell initialSnapshot={await getPublicSnapshot()}>{children}</LivePageShell></body>
    </html>
  );
}
