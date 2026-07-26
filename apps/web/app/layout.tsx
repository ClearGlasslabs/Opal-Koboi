import type { Metadata } from 'next'
import './styles.css'

export const metadata: Metadata = {
  metadataBase: new URL('https://clearglasslabs.github.io/Opal-Koboi/'),
  title: 'Artemis Journal — Human-Governed Intelligence',
  description: 'Field notes on human-governed AI, ontology-driven operations, and secure intelligence systems from ClearGlassInc Artemis.',
  keywords: ['agentic AI', 'human-governed AI', 'intelligence systems', 'ontology', 'ClearGlassInc Artemis'],
  alternates: { canonical: '/' },
  openGraph: { title: 'Artemis Journal — Intelligence, made legible.', description: 'Research and field notes from the frontier of governed intelligence systems.', type: 'website', url: '/' },
  twitter: { card: 'summary_large_image', title: 'Artemis Journal', description: 'Clarity at the edge of possibility.' }
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="en"><body>{children}</body></html>
}
