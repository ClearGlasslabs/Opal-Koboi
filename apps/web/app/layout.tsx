import type { Metadata } from "next";
import "./styles.css";
import { LivePageShell } from "./components/live/LivePageShell";
import { getPublicSnapshot } from "../lib/live/snapshot";

export const metadata: Metadata = {
  metadataBase: new URL("https://clearglasslabs.github.io/Opal-Koboi/"),
  title: "Business Productivity Plans | ClearGlassInc Artemis",
  description:
    "Flexible CAD business productivity plans with secure collaboration, per-user pricing, and a free 14-day trial.",
  keywords: [
    "business productivity plans",
    "cloud collaboration",
    "business subscriptions",
    "ClearGlassInc Artemis",
  ],
  alternates: { canonical: "/" },
  openGraph: {
    title: "Flexible business productivity plans | ClearGlassInc Artemis",
    description:
      "Secure cloud productivity and business-grade tools that scale with your team.",
    type: "website",
    url: "/",
  },
  twitter: {
    card: "summary_large_image",
    title: "ClearGlassInc Artemis Business Plans",
    description: "Flexible productivity plans that scale with your team.",
  },
  other: {
    "dcterms.rightsHolder": "ClearGlassInc Artemis",
    "dcterms.license": "https://clearglasslabs.github.io/Opal-Koboi/legal",
    "content-origin": "ClearGlassInc Artemis",
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
