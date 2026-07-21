const workflows = [
  ['Secure Tabs', 'Mission-scoped tab workspaces preserve source lineage, capture hashes, and note context.'],
  ['Cited AI', 'Summaries require evidence-backed citations for every claim before they can be saved.'],
  ['Local Vault', 'Secrets stay local-first with encrypted envelopes and no import-time side effects.'],
  ['Audit RBAC', 'Viewer, researcher, auditor, and admin roles enforce least privilege with immutable logs.']
]

export default function Page() {
  return <main className="shell">
    <section className="hero glass">
      <p className="eyebrow">Defensive browser intelligence • public sources only</p>
      <h1>ClearGlassInc Artemis turns research tabs into cited, auditable security intelligence.</h1>
      <p className="lede">A production-ready open-source blueprint for browser security teams, AI research automation, and cybersecurity workflow automation—without offensive, deceptive, or unauthorized access functionality.</p>
      <div className="actions"><a href="#architecture">Architecture</a><a href="#threat-model">Threat model</a></div>
    </section>
    <section className="grid" aria-label="Browser workflow capabilities">
      {workflows.map(([title, body]) => <article className="card glass" key={title}><h2>{title}</h2><p>{body}</p></article>)}
    </section>
    <section id="architecture" className="panel glass"><h2>Architecture</h2><p>Next.js premium UI, FastAPI/Python policy services, local encrypted browser storage, public OSINT ingestion adapters, citation-first AI summarization, OpenTelemetry traces, append-only audits, and CI hardening gates.</p></section>
    <section id="threat-model" className="panel glass"><h2>Threat Model</h2><p>Protects secrets, source integrity, analyst notes, and mission context from XSS, supply-chain compromise, prompt injection, over-broad access, and unverifiable AI claims. Human approval gates block consequential actions.</p></section>
  </main>
}
