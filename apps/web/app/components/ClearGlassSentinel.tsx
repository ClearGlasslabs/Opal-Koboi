'use client'

import { FormEvent, KeyboardEvent, useEffect, useId, useRef, useState } from 'react'

type Message = { id: number; role: 'assistant' | 'user'; text: string; source?: string; confidence?: string }

const quickActions = [
  'I need a high-performance website.',
  'I want more qualified leads.',
  'I need AI automation.',
  'I need a secure customer portal.',
  'I need cybersecurity guidance.',
  'I need cloud deployment help.',
  'I want a full digital growth system.',
]

const welcome: Message = {
  id: 1,
  role: 'assistant',
  text: 'Welcome. I’m ClearGlass Sentinel, an AI assistant—not a human. Tell me what you want to build, improve, or protect, and I’ll suggest a transparent next step.',
  source: 'ClearGlass service guide',
  confidence: 'High',
}

function responseFor(input: string): Message {
  const value = input.toLowerCase()
  let text = 'A short discovery is the best next step. What are you trying to build or improve, who are the users, and what business outcome matters most? Please do not share passwords, API keys, payment-card data, or confidential documents.'
  if (value.includes('website')) text = 'A high-performance website pathway usually covers discovery, content and conversion architecture, accessible interface design, Next.js implementation, SEO foundations, analytics, deployment, and measured launch support. What is the main business goal and what does your current site use?'
  if (value.includes('lead') || value.includes('growth')) text = 'For qualified growth, I’d begin with audience and offer clarity, conversion journeys, technical SEO, attribution, and responsible automation. Which audience and conversion—consultation, demo, or purchase—matters most?'
  if (value.includes('ai') || value.includes('automation')) text = 'An AI automation pathway starts with a bounded workflow, approved data, measurable evaluations, privacy controls, and human approval for consequential actions. Which repetitive workflow would you like to improve?'
  if (value.includes('portal')) text = 'A secure portal pathway can include identity and access design, tenant isolation, auditable authorization, privacy review, application engineering, and controlled cloud delivery. Who are the users, and which integrations are required?'
  if (value.includes('cyber') || value.includes('security')) text = 'I can provide defensive, blue-team-aligned guidance for authorized systems: security posture review, alert interpretation, application hardening, incident-readiness, and human-supervised remediation planning. I cannot scan or act on a system here. What authorized environment or concern should a specialist review?'
  if (value.includes('cloud') || value.includes('deploy')) text = 'A cloud delivery pathway can cover architecture, CI/CD, observability, backup and rollback planning, least privilege, and deployment health. Which cloud, runtime, and availability constraints are in scope?'
  if (value.includes('price') || value.includes('cost')) text = 'I don’t have an approved pricing range configured, so I won’t invent one. I can prepare a concise project brief for a human to scope and price after reviewing your goals, timeline, and constraints.'
  if (value.includes('password') || value.includes('api key') || value.includes('secret')) text = 'Please do not send credentials or secrets. If one was exposed, revoke it through the authorized provider, notify your security owner, and use the human support channel. I do not retain or validate credentials here.'
  return { id: Date.now() + 1, role: 'assistant', text, source: 'Approved service & safety guidance', confidence: 'High' }
}

export function ClearGlassSentinel() {
  const [open, setOpen] = useState(false)
  const [dismissed, setDismissed] = useState(false)
  const [messages, setMessages] = useState<Message[]>([welcome])
  const [draft, setDraft] = useState('')
  const [briefing, setBriefing] = useState(false)
  const [reported, setReported] = useState(false)
  const dialogRef = useRef<HTMLElement>(null)
  const launcherRef = useRef<HTMLButtonElement>(null)
  const titleId = useId()

  useEffect(() => {
    const restoreDismissal = window.setTimeout(() => {
      setDismissed(sessionStorage.getItem('sentinel-dismissed') === 'true')
    }, 0)
    return () => window.clearTimeout(restoreDismissal)
  }, [])
  useEffect(() => {
    if (!open) return
    const prior = document.activeElement as HTMLElement | null
    const launcher = launcherRef.current
    dialogRef.current?.querySelector<HTMLElement>('button, input')?.focus()
    const onKey = (event: globalThis.KeyboardEvent) => {
      if (event.key === 'Escape') setOpen(false)
      if (event.key !== 'Tab') return
      const items = dialogRef.current?.querySelectorAll<HTMLElement>('button:not([disabled]), input:not([disabled])')
      if (!items?.length) return
      const first = items[0], last = items[items.length - 1]
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus() }
      if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus() }
    }
    document.addEventListener('keydown', onKey)
    const overflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    return () => { document.removeEventListener('keydown', onKey); document.body.style.overflow = overflow; (prior ?? launcher)?.focus() }
  }, [open])

  const send = (value: string) => {
    const clean = value.trim().slice(0, 1000)
    if (!clean) return
    setMessages((current) => [...current, { id: Date.now(), role: 'user', text: clean }, responseFor(clean)])
    setDraft('')
  }
  const submit = (event: FormEvent) => { event.preventDefault(); send(draft) }
  const inputKey = (event: KeyboardEvent<HTMLInputElement>) => { if (event.key === 'Escape') setOpen(false) }
  const dismiss = () => { sessionStorage.setItem('sentinel-dismissed', 'true'); setDismissed(true) }

  return <>
    <section className="sentinelHero glass" aria-labelledby="sentinel-hero-title">
      <div className="sentinelKicker"><span aria-hidden="true" /> CLEARGLASS SENTINEL <b>PUBLIC CONCIERGE</b></div>
      <h2 id="sentinel-hero-title">Where should we strengthen your digital system?</h2>
      <p>Security-engineered guidance for growth, web, AI, cloud, and defensive operations—with auditable controls and humans in command.</p>
      <div className="sentinelQuick" aria-label="Common project goals">
        {quickActions.map((action) => <button type="button" key={action} onClick={() => { setOpen(true); send(action) }}>{action}</button>)}
      </div>
      <button className="sentinelOpen" type="button" onClick={() => setOpen(true)}>OPEN SENTINEL <span aria-hidden="true">↗</span></button>
      <small>AI DISCLOSURE · NO SENSITIVE DATA · HUMAN-SUPERVISED</small>
    </section>

    {!dismissed && <aside className="sentinelLauncher" aria-label="ClearGlass Sentinel assistant launcher">
      <button ref={launcherRef} className="launcherMain" type="button" onClick={() => setOpen(true)} aria-haspopup="dialog"><span className="sentinelGlyph" aria-hidden="true">◇</span><span><b>Ask Sentinel</b><small>Explore services or start a project</small></span></button>
      <button className="launcherDismiss" type="button" onClick={dismiss} aria-label="Dismiss Sentinel launcher for this browser session">×</button>
    </aside>}

    {open && <div className="sentinelBackdrop" onMouseDown={() => setOpen(false)}>
      <section ref={dialogRef} className="sentinelPanel" role="dialog" aria-modal="true" aria-labelledby={titleId} onMouseDown={(event) => event.stopPropagation()}>
        <header><div><span className="sentinelGlyph" aria-hidden="true">◇</span><div><p>CLEARGLASS SENTINEL</p><h2 id={titleId}>Growth, Security &amp; Systems Concierge</h2></div></div><button type="button" onClick={() => setOpen(false)} aria-label="Close Sentinel">×</button></header>
        <div className="sentinelTrust"><span>AI ASSISTANT</span><span>PUBLIC CONCIERGE</span><span>PRIVACY-PRESERVING</span><span>HUMAN-SUPERVISED</span></div>
        <div className="sentinelMode" role="group" aria-label="Assistant modes"><button type="button" aria-pressed="true">Public concierge</button><button type="button" disabled title="Authentication required">Customer support · Locked</button><button type="button" disabled title="Operator authorization required">Blue-team ops · Locked</button></div>
        <div className="sentinelHistory" aria-live="polite" aria-label="Conversation history">
          {messages.map((message) => <article className={message.role} key={message.id}><small>{message.role === 'assistant' ? 'SENTINEL · AI' : 'YOU'}</small><p>{message.text}</p>{message.source && <footer><span>SOURCE · {message.source}</span><span>CONFIDENCE · {message.confidence}</span></footer>}</article>)}
        </div>
        <div className="sentinelReplies">{quickActions.slice(0, 4).map((action) => <button type="button" key={action} onClick={() => send(action)}>{action}</button>)}</div>
        {briefing && <div className="briefNotice" role="status"><b>Project brief started.</b> Share only your goal, users, current platform, integrations, timeline, constraints, support needs, and expected security review. Contact details are requested only at confirmed handoff.</div>}
        <form className="sentinelComposer" onSubmit={submit}><label className="srOnly" htmlFor={`${titleId}-input`}>Message ClearGlass Sentinel</label><input id={`${titleId}-input`} value={draft} onChange={(event) => setDraft(event.target.value)} onKeyDown={inputKey} maxLength={1000} autoComplete="off" placeholder="Ask about a service or describe your goal…"/><button type="button" disabled aria-label="Voice input, planned feature" title="Voice input is a future optional feature">◉</button><button type="submit" disabled={!draft.trim()}>SEND</button></form>
        <nav className="sentinelActions" aria-label="Conversation actions"><a href="https://www.clearglassinc.com/#contact">Talk to a human</a><button type="button" onClick={() => setBriefing(true)}>Start a project brief</button><button type="button" onClick={() => setMessages([welcome])}>Clear conversation</button><button type="button" onClick={() => setReported(true)}>{reported ? 'Report noted' : 'Report conversation'}</button></nav>
        <footer className="sentinelPrivacy"><b>Privacy &amp; control</b><span>Messages stay in this browser prototype and are not submitted. Don’t include credentials, payment data, health data, or confidential records. Lead submission always requires explicit confirmation. Security recommendations are hypotheses until a qualified human validates them.</span></footer>
      </section>
    </div>}
  </>
}
