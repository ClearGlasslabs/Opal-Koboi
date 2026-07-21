import type { Metadata } from 'next'
import './styles.css'

export const metadata: Metadata = {
  title: 'ClearGlassInc Artemis Browser Intelligence Assistant',
  description: 'Local-first AI research automation for browser security, OSINT source tracking, and cybersecurity workflow automation.',
  keywords: ['browser security', 'AI research automation', 'cybersecurity workflow automation', 'OSINT', 'defensive intelligence'],
  openGraph: { title: 'ClearGlassInc Artemis', description: 'Defensive browser intelligence with citations, audit logs, and encrypted local-first workflows.', type: 'website' }
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="en"><body>{children}</body></html>
}
