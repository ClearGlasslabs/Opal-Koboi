'use client'

import { useEffect, useMemo, useState } from 'react'

type Post = {
  id: number
  category: string
  title: string
  excerpt: string
  read: string
  date: string
  score: number
  accent: string
  featured?: boolean
}

const posts: Post[] = [
  { id: 1, category: 'Agentic Systems', title: 'The Human-Governed Path to Self-Improving Intelligence', excerpt: 'A field guide to evaluation loops, signed change proposals, and autonomy that never outruns operator intent.', read: '11 min', date: 'Jul 24', score: 96, accent: 'cyan', featured: true },
  { id: 2, category: 'Ontology', title: 'Why Mission Context Is a First-Class Data Object', excerpt: 'Temporal state, confidence, lineage, and permissions become a shared language for analysts and agents.', read: '7 min', date: 'Jul 18', score: 92, accent: 'violet' },
  { id: 3, category: 'Field Notes', title: 'Designing a Coalition-Aware Intelligence Surface', excerpt: 'How progressive disclosure makes complex operational data legible without flattening security boundaries.', read: '6 min', date: 'Jul 11', score: 89, accent: 'amber' },
  { id: 4, category: 'Engineering', title: 'Sub-Second Retrieval Across a Living Evidence Graph', excerpt: 'Practical indexing patterns for fresh, provenance-rich answers under real mission latency.', read: '9 min', date: 'Jun 28', score: 94, accent: 'green' },
  { id: 5, category: 'Agentic Systems', title: 'Evaluation Is the Product: Building Trustworthy Copilots', excerpt: 'Precision, operator trust, groundedness, and rollback readiness belong in one release gate.', read: '8 min', date: 'Jun 16', score: 91, accent: 'blue' },
  { id: 6, category: 'Engineering', title: 'Apollo Patterns for Calm, Controlled AI Releases', excerpt: 'Canary routing and instant rollback for models, prompts, policies, and workflows.', read: '5 min', date: 'Jun 04', score: 87, accent: 'pink' }
]

const categories = ['All signals', 'Agentic Systems', 'Ontology', 'Engineering', 'Field Notes']

export default function Page() {
  const [category, setCategory] = useState('All signals')
  const [query, setQuery] = useState('')
  const [dark, setDark] = useState(true)
  const [progress, setProgress] = useState(0)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    const update = () => {
      const height = document.documentElement.scrollHeight - window.innerHeight
      setProgress(height > 0 ? Math.min(100, (window.scrollY / height) * 100) : 0)
    }
    update()
    window.addEventListener('scroll', update, { passive: true })
    return () => window.removeEventListener('scroll', update)
  }, [])

  const filtered = useMemo(() => posts.filter(post => {
    const matchesCategory = category === 'All signals' || post.category === category
    const haystack = `${post.title} ${post.excerpt} ${post.category}`.toLowerCase()
    return matchesCategory && haystack.includes(query.toLowerCase())
  }), [category, query])

  return (
    <main className={dark ? 'site dark' : 'site light'}>
      <div className="progress" style={{ transform: `scaleX(${progress / 100})` }} aria-hidden="true" />
      <nav className="nav" aria-label="Primary navigation">
        <a className="brand" href="#top" aria-label="Artemis Journal home"><span className="brandMark">A</span><span>ARTEMIS <em>/ JOURNAL</em></span></a>
        <div className="navLinks"><a href="#latest">Intelligence</a><a href="#briefing">Briefings</a><a href="#footer">About</a></div>
        <div className="navActions">
          <button className="iconButton" onClick={() => setDark(!dark)} aria-label="Toggle color theme">{dark ? '☼' : '◐'}</button>
          <a className="signalButton" href="#latest"><span /> Explore signals</a>
        </div>
      </nav>

      <header id="top" className="hero">
        <div className="heroGlow" aria-hidden="true" />
        <div className="heroMeta"><span className="liveDot" /> ARTEMIS INTELLIGENCE JOURNAL <i>VOL. 04 / 2026</i></div>
        <div className="heroGrid">
          <div className="heroCopy">
            <p className="kicker">FEATURED FIELD NOTE <span>01</span></p>
            <h1>Intelligence,<br /><span>made legible.</span></h1>
            <p className="lede">Ideas from the frontier of human-governed AI, ontology-driven operations, and systems built to earn trust at machine speed.</p>
            <div className="heroByline"><div className="avatar">AK</div><div><strong>Amara Kline</strong><small>Director, Intelligence Systems</small></div><span>11 MIN READ</span></div>
          </div>
          <a className="featurePanel" href="#briefing" aria-label="Read the featured field note">
            <div className="orbit orbitOne" /><div className="orbit orbitTwo" />
            <div className="featureTop"><span>NEW SIGNAL</span><span>96 / 100 RELEVANCE</span></div>
            <div className="featureVisual"><div className="core"><span>AI</span></div><i className="node n1" /><i className="node n2" /><i className="node n3" /><i className="node n4" /></div>
            <div className="featureBottom"><span>READ THE FIELD NOTE</span><b>↗</b></div>
          </a>
        </div>
        <div className="scrollCue"><span /> SCROLL TO DECODE</div>
      </header>

      <section id="briefing" className="briefing reveal">
        <div className="sectionLabel"><span>01</span> THE BRIEFING</div>
        <div className="briefGrid">
          <div><p className="kicker">AI-GENERATED SYNOPSIS <span>VERIFIED</span></p><h2>The system improves.<br />The operator remains in command.</h2></div>
          <div className="summary">
            <p>ClearGlassInc Artemis turns operator corrections and mission outcomes into evaluated improvement proposals—not automatic production changes. Every prompt, model route, and workflow revision is versioned, measurable, and human-approved.</p>
            <div className="takeaways"><span>KEY TAKEAWAYS</span><ul><li>Feedback becomes evidence, never an unchecked objective.</li><li>Every release carries provenance and an instant rollback path.</li><li>Trust is scored alongside precision, recall, and latency.</li></ul></div>
          </div>
          <aside className="readingControls" aria-label="Reading controls"><span>READING MODE</span><button onClick={() => setSaved(!saved)} aria-pressed={saved}>{saved ? '✓ Saved' : '+ Save briefing'}</button><button onClick={() => window.print()}>↗ Export</button></aside>
        </div>
      </section>

      <section id="latest" className="latest reveal">
        <div className="sectionHead"><div><div className="sectionLabel"><span>02</span> SIGNAL ARCHIVE</div><h2>Latest intelligence</h2></div><p>Research, field notes, and operating principles from the teams building secure intelligence systems.</p></div>
        <div className="filterBar">
          <div className="filters" role="group" aria-label="Filter articles by category">{categories.map(item => <button key={item} className={category === item ? 'active' : ''} onClick={() => setCategory(item)}>{item}</button>)}</div>
          <label className="search"><span>⌕</span><input value={query} onChange={event => setQuery(event.target.value)} placeholder="Search the archive" aria-label="Search articles" /></label>
        </div>
        <div className="postGrid" aria-live="polite">
          {filtered.map((post, index) => <article className={`postCard ${post.accent}`} key={post.id}>
            <div className="cardIndex">0{index + 1}</div>
            <div className="cardArt" aria-hidden="true"><div className="artLines" /><span>{post.score}</span><small>SEMANTIC<br />SCORE</small></div>
            <div className="cardBody"><div className="postMeta"><span>{post.category}</span><span>{post.date} · {post.read}</span></div><h3>{post.title}</h3><p>{post.excerpt}</p><div className="bestFor">BEST FOR <b>{post.category === 'Engineering' ? 'PLATFORM TEAMS' : post.category === 'Field Notes' ? 'MISSION LEADS' : 'AI ARCHITECTS'}</b><i>↗</i></div></div>
          </article>)}
          {filtered.length === 0 && <div className="empty"><span>NO SIGNAL FOUND</span><h3>Try a broader search.</h3><button onClick={() => { setQuery(''); setCategory('All signals') }}>Reset archive</button></div>}
        </div>
      </section>

      <section className="personalized reveal">
        <div><p className="kicker">PERSONALIZED FOR YOU <span>BETA</span></p><h2>Your next signal,<br />already in focus.</h2><p>Based on your interest in ontology, governed agents, and resilient deployment.</p></div>
        <div className="relatedStack"><span className="match">94% TOPIC MATCH</span><h3>From Data Fabric to Decision Advantage</h3><p>A practical model for turning governed ontology objects into faster, explainable action.</p><a href="#top">Open recommendation <span>→</span></a></div>
      </section>

      <footer id="footer"><div className="footerBrand"><span className="brandMark">A</span><div><strong>ARTEMIS JOURNAL</strong><small>Clarity at the edge of possibility.</small></div></div><div className="footerLinks"><a href="#top">Principles</a><a href="#latest">Archive</a><a href="#briefing">Intelligence</a></div><p>© 2026 ClearGlassInc Artemis<br />Human-governed intelligence systems.</p></footer>
    </main>
  )
}
