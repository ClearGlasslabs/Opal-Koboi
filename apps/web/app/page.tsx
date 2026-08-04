'use client'

import { FormEvent, useEffect, useId, useRef, useState } from 'react'
import { NeonPulse } from './components/NeonPulse'
import { ExperienceNav } from './components/ExperienceNav'

const agents = [
  ['ORION', 'Triage lead', 'ACTIVE', '18ms'],
  ['SPECTRA', 'Fusion analyst', 'ACTIVE', '24ms'],
  ['AEGIS', 'Policy sentinel', 'ACTIVE', '11ms'],
  ['MNEMOSYNE', 'Graph curator', 'DEGRADED', '86ms'],
]

const signals = [
  { time: '02:14:08', kind: 'COALITION FEED', title: 'Infrastructure identity anomaly', detail: '3 sources · 0.86 confidence', risk: 82 },
  { time: '02:13:51', kind: 'ENDPOINT', title: 'Unusual credential sequence', detail: '7 related events · 0.73 confidence', risk: 67 },
  { time: '02:12:19', kind: 'ONTOLOGY', title: 'New asset relationship resolved', detail: 'Evidence chain verified', risk: 34 },
]

export default function Page() {
  const [selected, setSelected] = useState(0)
  const [modal, setModal] = useState(false)
  const [criticalOnly, setCriticalOnly] = useState(false)
  const [decisionError, setDecisionError] = useState('')
  const [notice, setNotice] = useState('')
  const dialogRef = useRef<HTMLElement>(null)
  const reviewButtonRef = useRef<HTMLButtonElement>(null)
  const rationaleId = useId()
  const visibleSignals = criticalOnly ? signals.filter((signal) => signal.risk > 70) : signals

  useEffect(() => {
    if (!modal) return
    const previouslyFocused = document.activeElement as HTMLElement | null
    const reviewButton = reviewButtonRef.current
    const focusable = dialogRef.current?.querySelectorAll<HTMLElement>('button, textarea')
    focusable?.[0]?.focus()
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setModal(false)
      if (event.key !== 'Tab' || !focusable?.length) return
      const first = focusable[0]
      const last = focusable[focusable.length - 1]
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault(); last.focus()
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault(); first.focus()
      }
    }
    document.addEventListener('keydown', handleKeyDown)
    const originalOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    return () => {
      document.removeEventListener('keydown', handleKeyDown)
      document.body.style.overflow = originalOverflow
      ;(previouslyFocused ?? reviewButton)?.focus()
    }
  }, [modal])

  const closeModal = () => { setDecisionError(''); setModal(false) }
  const submitDecision = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!String(new FormData(event.currentTarget).get('rationale') ?? '').trim()) {
      setDecisionError('Enter a decision rationale before requesting approval.')
      dialogRef.current?.querySelector('textarea')?.focus()
      return
    }
    setNotice('Containment package sent for second approval.')
    closeModal()
  }

  return <main className="commandShell">
    <header className="commandNav">
      <NeonPulse position="bottom" />
      <div className="commandBrand"><span className="brandMark">A</span><div><b>CLEARGLASSINC</b><small>ARTEMIS / MISSION CONTROL</small></div></div>
      <div className="mission"><span /> OPERATION NIGHTGLASS <em>SECRET // COALITION</em></div>
      <div className="operator">COMMANDER I. VOSS <span className="operatorAvatar" aria-hidden="true">IV</span></div>
    </header>

    <aside className="rail" aria-label="Command navigation">
      {['⌾', '⌁', '◇', '△', '◎'].map((icon, i) => <a className={i === 0 ? 'active' : ''} key={icon} aria-label={['Overview','Graph','Signals','Agents','Audit'][i]} href={['#mission-control','#threat-graph','#priority-signals','#agent-registry','#control-trace'][i]}>{icon}</a>)}
      <div className="railStatus"><i /> ZERO TRUST</div>
    </aside>

    <section className="commandMain" id="mission-control">
      <ExperienceNav />
      <div className="topline"><div><p>EXECUTIVE ORCHESTRATION / LIVE</p><h1>Mission intelligence</h1></div><div className="systemHealth"><span>98.7%</span><small>SYSTEM CONFIDENCE</small></div></div>
      <div className="metricRow neon-surface">
        {[['1,284','EVENTS / MIN','+12.4%'],['47','ACTIVE ENTITIES','+6'],['04','AGENTS ONLINE','NOMINAL'],['02','APPROVALS','ACTION REQUIRED']].map((m,i) => <article key={m[1]} className={i===3?'attention':''}><small>{m[1]}</small><strong>{m[0]}</strong><em>{m[2]}</em></article>)}
      </div>

      <div className="commandGrid">
        <section className="graphPanel glass neonSurface" id="threat-graph">
          <NeonPulse variant="violet" />
          <div className="panelHead"><div><small>LIVE EVIDENCE GRAPH</small><h2>Threat constellation</h2></div><span>47 ENTITIES · 92 EDGES</span></div>
          <div className="orbitalGraph" role="img" aria-label="Relationship graph with threat TX-091 connected to five entities">
            <div className="ring r1"/><div className="ring r2"/><div className="ring r3"/>
            <div className="graphCore"><b>TX-091</b><small>THREAT</small></div>
            {['ASSET-7','IDENTITY','EVENT-31','NODE-14','SOURCE'].map((x,i)=><div key={x} className={`graphNode gn${i+1}`}><i/>{x}</div>)}
            <svg aria-hidden="true" viewBox="0 0 700 410" preserveAspectRatio="none"><path d="M350 205 L130 90 M350 205 L570 75 M350 205 L620 265 M350 205 L190 330 M350 205 L465 350" /></svg>
          </div>
          <div className="graphLegend"><span><i className="threat"/> Threat</span><span><i className="asset"/> Asset</span><span><i className="identity"/> Identity</span><b>PROVENANCE VERIFIED</b></div>
        </section>

        <section className="signalsPanel glass neonSurface" id="priority-signals">
          <NeonPulse variant="cyan" position="top" />
          <div className="panelHead"><div><small>INTELLIGENCE STREAM</small><h2>Priority signals</h2></div><button type="button" aria-pressed={criticalOnly} onClick={() => setCriticalOnly((value) => !value)}>{criticalOnly ? 'SHOW ALL' : 'CRITICAL ONLY'}</button></div>
          <div className="signalList">{visibleSignals.map((signal)=><button type="button" key={signal.time} className={signals[selected]===signal?'selected':''} aria-pressed={signals[selected]===signal} onClick={()=>setSelected(signals.indexOf(signal))}>
            <div className="signalTime">{signal.time}<i/></div><div><small>{signal.kind}</small><strong>{signal.title}</strong><p>{signal.detail}</p></div><span className={signal.risk>70?'critical':''}>{signal.risk}</span>
          </button>)}</div>
          <button ref={reviewButtonRef} type="button" className="reviewAction neonAction" onClick={()=>setModal(true)}><NeonPulse variant="signal" />REVIEW RECOMMENDATION <span aria-hidden="true">→</span></button>
        </section>

        <section className="agentsPanel glass neonSurface" id="agent-registry">
          <NeonPulse variant="cyan" />
          <div className="panelHead"><div><small>AUTONOMOUS EXECUTION</small><h2>Agent registry</h2></div><span>4 / 4 REGISTERED</span></div>
          <div className="agentList">{agents.map((agent,i)=><div key={agent[0]}><span className={`agentOrb a${i}`}>{agent[0][0]}</span><div><strong>{agent[0]}</strong><small>{agent[1]}</small></div><em>{agent[2]}</em><time>{agent[3]}</time></div>)}</div>
        </section>

        <section className="auditPanel glass neonSurface" id="control-trace"><NeonPulse variant="magenta" position="bottom" /><small>IMMUTABLE AUDIT</small><h2>Control trace</h2><div className="trace"><span/><p><b>POLICY CHECK PASSED</b><small>AEGIS · action:correlate · 02:14:11</small></p></div><div className="trace"><span/><p><b>HUMAN APPROVAL REQUIRED</b><small>Risk 82 · two-person gate · 02:14:14</small></p></div></section>
      </div>
      <footer className="legalFooter"><span>© 2026 ClearGlassInc Artemis. All rights reserved.</span><a href="/legal">Privacy · Terms · AUP · Copyright</a><span>Public pages cannot prevent screenshots or determined copying.</span></footer>
    </section>

    <p className="srOnly" role="status" aria-live="polite">{notice}</p>
    {modal && <div className="modalBackdrop" onMouseDown={closeModal}><section ref={dialogRef} className="secureModal neonSurface" role="dialog" aria-modal="true" aria-labelledby="approval-title" aria-describedby="approval-description" onMouseDown={e=>e.stopPropagation()}><NeonPulse variant="violet" /><form onSubmit={submitDecision}><div className="modalSeal" aria-hidden="true">◈</div><small>SECURE ACTION / TWO-PERSON CONTROL</small><h2 id="approval-title">Review containment package</h2><p id="approval-description">Artemis recommends isolating <b>ASSET-7</b> from mission network segments. This remains a proposal until separately approved and re-authorized at execution time.</p><div className="riskBar"><span>RISK SCORE</span><b>82 / 100</b></div><ul><li>4 evidence objects with verified provenance</li><li>Rollback plan attached and validated</li><li>Sensitive arguments sanitized from preview</li></ul><label htmlFor={rationaleId}>DECISION RATIONALE</label><textarea id={rationaleId} name="rationale" aria-describedby={decisionError ? `${rationaleId}-error` : undefined} aria-invalid={Boolean(decisionError)} placeholder="Required for approval or rejection" />{decisionError && <p className="fieldError" id={`${rationaleId}-error`} role="alert">{decisionError}</p>}<div className="modalActions"><button type="button" onClick={closeModal}>CANCEL</button><button type="button" className="reject" onClick={() => { setNotice('Containment recommendation rejected.'); closeModal() }}>REJECT</button><button type="submit" className="approve">REQUEST SECOND APPROVAL</button></div></form></section></div>}
  </main>
}
