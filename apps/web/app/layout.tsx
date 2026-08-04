import type { Metadata } from "next";
import "./styles.css";

export const metadata: Metadata = {
  metadataBase: new URL("https://clearglasslabs.github.io/Opal-Koboi/"),
  title: "ClearGlassInc Artemis — Human-Governed Intelligence",
  description:
    "Fuse every trusted signal into governed action with ClearGlassInc Artemis, the intelligence fabric for mission-critical operations.",
  keywords: [
    "agentic AI",
    "human-governed AI",
    "intelligence systems",
    "ontology",
    "ClearGlassInc Artemis",
  ],
  alternates: { canonical: "/" },
  openGraph: {
    title: "Artemis Journal — Intelligence, made legible.",
    description:
      "Research and field notes from the frontier of governed intelligence systems.",
    type: "website",
    url: "/",
  },
  twitter: {
    card: "summary_large_image",
    title: "Artemis Journal",
    description: "Clarity at the edge of possibility.",
  },
  other: {
    "dcterms.rightsHolder": "ClearGlassInc Artemis",
    "dcterms.license": "https://clearglasslabs.github.io/Opal-Koboi/legal",
    "content-origin": "ClearGlassInc Artemis",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
