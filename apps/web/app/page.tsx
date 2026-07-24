const metrics = [
  ['100%', 'cited AI claims'],
  ['0', 'private-source ingestion paths'],
  ['4', 'least-privilege roles'],
  ['<60 ms', 'local evidence search target']
]

const workflow = [
  'Mission-scoped tabs with source ledgers',
  'HTTPS public-source capture with SHA-256 evidence hashes',
  'Encrypted local-first vault envelopes for tokens and notes',
  'Citation-gated AI synthesis with human review queues',
  'Append-only audit events for every consequential action'
]

const architecture = [
  ['Browser Console', 'Tabs, captures, notebook, source cards, and AI review lanes run in a hardened Next.js shell.'],
  ['Local Evidence Store', 'IndexedDB/SQLite-ready schema keeps notes, excerpts, hashes, and encrypted envelopes local by default.'],
  ['Policy Gateway', 'RBAC, mission labels, public-source validation, rate limits, and approval gates protect every workflow.'],
  ['AI Citation Engine', 'Retrieval-first summarization refuses unsupported claims and emits source-level provenance.']
]

const roadmap = ['Browser extension companion', 'OPA/Rego policy packs', 'Offline vector index', 'Signed audit export', 'SSO/SCIM enterprise mode']

export default function Page() {
  return (
    <main className="shell">
      <nav className="nav" aria-label="Primary navigation">
        <a className="brand" href="#top"><span className="orb" />ClearGlassInc Artemis</a>
        <div className="links">
          <a href="#workflow">Workflow</a><a href="#architecture">Architecture</a><a href="#security">Security</a><a href="#roadmap">Roadmap</a>
        </div>
        <a className="navCta" href="#setup">Deploy locally</a>
      </nav>

      <section id="top" className="hero">
        <div className="heroCopy">
          <p className="eyebrow">Open-source defensive browser intelligence</p>
          <h1>Research faster without losing source integrity, auditability, or control.</h1>
          <p className="lede">A production-ready blueprint for lawful OSINT collection, browser-security research, AI summarization with citations, encrypted local-first storage, and role-based governance.</p>
          <div className="actions"><a href="#setup">Start the secure workflow</a><a href="#threat-model">Read threat model</a></div>
        </div>
        <div className="glassPanel" aria-label="Browser intelligence product preview">
          <div className="panelTop"><span /> <strong>Mission: Vendor advisory triage</strong><em>audited</em></div>
          <div className="browserGrid">
            <aside>
              <b>Tabs</b>
              {['CISA KEV', 'Vendor PSIRT', 'NVD CVE', 'Research note'].map((tab, index) => <p key={tab} className={index === 1 ? 'active' : ''}>{tab}</p>)}
            </aside>
            <section>
              <div className="sourceCard"><small>PUBLIC HTTPS SOURCE</small><h3>Vendor confirms patched issue</h3><p>Hash: 2f8c…b91a · Captured 2026-07-24T00:00Z · Citation ready</p></div>
              <div className="summaryCard"><small>AI SUMMARY POLICY</small><p>Every claim below requires a mapped citation before export.</p><ul><li>Patch is available. <sup>[1]</sup></li><li>Impact is limited to affected versions. <sup>[2]</sup></li></ul></div>
            </section>
          </div>
        </div>
      </section>

      <section className="metrics">{metrics.map(([value, label]) => <div key={label}><strong>{value}</strong><span>{label}</span></div>)}</section>

      <section id="workflow" className="section twoCol"><div><p className="eyebrow">Secure browser workflow</p><h2>Tabs, notes, captures, and source tracking built for evidence discipline.</h2><p>Artemis rejects private/local URLs, stores short excerpts and hashes instead of bulk copyrighted copies, and binds notes to mission context and immutable audit events.</p></div><ol className="steps">{workflow.map((item) => <li key={item}>{item}</li>)}</ol></section>

      <section id="architecture" className="section"><p className="eyebrow">Full-stack architecture</p><h2>Next.js UI, Python policy core, retrieval-first AI, and hardened operations.</h2><div className="cards">{architecture.map(([title, body]) => <article key={title}><h3>{title}</h3><p>{body}</p></article>)}</div></section>

      <section id="security" className="section twoCol"><div><p className="eyebrow">Security and governance</p><h2>Defensive use only, with explicit human control.</h2></div><div className="matrix"><p><b>RBAC:</b> viewer, researcher, auditor, admin permissions.</p><p><b>Audit:</b> sealed events for reads, writes, captures, and vault actions.</p><p><b>Secrets:</b> encrypted envelopes with authenticated ciphertext and keychain/KMS upgrade path.</p><p><b>AI safety:</b> citation-per-claim validation, no offensive modules, human approval gates.</p></div></section>

      <section id="threat-model" className="section threat"><h2>Threat model highlights</h2><p>Controls prioritize XSS hardening, source tamper detection, unauthorized note access prevention, hallucination resistance, and non-repudiation for sensitive security research workflows.</p></section>

      <section id="setup" className="section setup"><h2>Local setup</h2><pre><code>{`python -m pip install -e '.[dev]'
pytest tests/test_browser_research_assistant.py

cd apps/web
npm install
npm run build`}</code></pre></section>

      <section id="roadmap" className="section"><p className="eyebrow">Roadmap</p><div className="chips">{roadmap.map((item) => <span key={item}>{item}</span>)}</div></section>
    </main>
  )
}
