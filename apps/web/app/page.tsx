'use client'

import { useState } from 'react'
import { NeonPulse } from './components/NeonPulse'

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

  return <main className="commandShell">
    <header className="commandNav">
      <NeonPulse position="bottom" />
      <div className="commandBrand"><span className="brandMark">A</span><div><b>CLEARGLASSINC</b><small>ARTEMIS / MISSION CONTROL</small></div></div>
      <div className="mission"><span /> OPERATION NIGHTGLASS <em>SECRET // COALITION</em></div>
      <div className="operator">COMMANDER I. VOSS <button aria-label="Open profile">IV</button></div>
    </header>

    <aside className="rail" aria-label="Command navigation">
      {['⌾', '⌁', '◇', '△', '◎', '⚙'].map((icon, i) => <button className={i === 0 ? 'active' : ''} key={icon} aria-label={['Overview','Graph','Signals','Agents','Audit','Settings'][i]}>{icon}</button>)}
      <div className="railStatus"><i /> ZERO TRUST</div>
    </aside>

    <section className="commandMain">
      <div className="topline"><div><p>EXECUTIVE ORCHESTRATION / LIVE</p><h1>Mission intelligence</h1></div><div className="systemHealth"><span>98.7%</span><small>SYSTEM CONFIDENCE</small></div></div>
      <div className="metricRow neon-surface">
        {[['1,284','EVENTS / MIN','+12.4%'],['47','ACTIVE ENTITIES','+6'],['04','AGENTS ONLINE','NOMINAL'],['02','APPROVALS','ACTION REQUIRED']].map((m,i) => <article key={m[1]} className={i===3?'attention':''}><small>{m[1]}</small><strong>{m[0]}</strong><em>{m[2]}</em></article>)}
      </div>

      <div className="commandGrid">
        <section className="graphPanel glass neonSurface">
          <NeonPulse variant="violet" />
          <div className="panelHead"><div><small>LIVE EVIDENCE GRAPH</small><h2>Threat constellation</h2></div><span>47 ENTITIES · 92 EDGES</span></div>
          <div className="orbitalGraph" aria-label="Animated relationship visualization">
            <div className="ring r1"/><div className="ring r2"/><div className="ring r3"/>
            <div className="graphCore"><b>TX-091</b><small>THREAT</small></div>
            {['ASSET-7','IDENTITY','EVENT-31','NODE-14','SOURCE'].map((x,i)=><div key={x} className={`graphNode gn${i+1}`}><i/>{x}</div>)}
            <svg viewBox="0 0 700 410" preserveAspectRatio="none"><path d="M350 205 L130 90 M350 205 L570 75 M350 205 L620 265 M350 205 L190 330 M350 205 L465 350" /></svg>
          </div>
          <div className="graphLegend"><span><i className="threat"/> Threat</span><span><i className="asset"/> Asset</span><span><i className="identity"/> Identity</span><b>PROVENANCE VERIFIED</b></div>
        </section>

        <section className="signalsPanel glass neonSurface">
          <NeonPulse variant="cyan" position="top" />
          <div className="panelHead"><div><small>INTELLIGENCE STREAM</small><h2>Priority signals</h2></div><button>FILTER</button></div>
          <div className="signalList">{signals.map((signal,i)=><button key={signal.time} className={selected===i?'selected':''} onClick={()=>setSelected(i)}>
            <div className="signalTime">{signal.time}<i/></div><div><small>{signal.kind}</small><strong>{signal.title}</strong><p>{signal.detail}</p></div><span className={signal.risk>70?'critical':''}>{signal.risk}</span>
          </button>)}</div>
          <button className="reviewAction neonAction" onClick={()=>setModal(true)}><NeonPulse variant="signal" />REVIEW RECOMMENDATION <span>→</span></button>
        </section>

        <section className="agentsPanel glass neonSurface">
          <NeonPulse variant="cyan" />
          <div className="panelHead"><div><small>AUTONOMOUS EXECUTION</small><h2>Agent registry</h2></div><span>4 / 4 REGISTERED</span></div>
          <div className="agentList">{agents.map((agent,i)=><div key={agent[0]}><span className={`agentOrb a${i}`}>{agent[0][0]}</span><div><strong>{agent[0]}</strong><small>{agent[1]}</small></div><em>{agent[2]}</em><time>{agent[3]}</time></div>)}</div>
        </section>

        <section className="auditPanel glass neonSurface"><NeonPulse variant="magenta" position="bottom" /><small>IMMUTABLE AUDIT</small><h2>Control trace</h2><div className="trace"><span/><p><b>POLICY CHECK PASSED</b><small>AEGIS · action:correlate · 02:14:11</small></p></div><div className="trace"><span/><p><b>HUMAN APPROVAL REQUIRED</b><small>Risk 82 · two-person gate · 02:14:14</small></p></div></section>
      </div>
      <footer className="legalFooter"><span>© 2026 ClearGlassInc Artemis. All rights reserved.</span><a href="/legal">Privacy · Terms · AUP · Copyright</a><span>Public pages cannot prevent screenshots or determined copying.</span></footer>
    </section>

    {modal && <div className="modalBackdrop" role="presentation" onMouseDown={()=>setModal(false)}><section className="secureModal neonSurface" role="dialog" aria-modal="true" aria-labelledby="approval-title" onMouseDown={e=>e.stopPropagation()}><NeonPulse variant="violet" /><div className="modalSeal">◈</div><small>SECURE ACTION / TWO-PERSON CONTROL</small><h2 id="approval-title">Review containment package</h2><p>Artemis recommends isolating <b>ASSET-7</b> from mission network segments. This remains a proposal until separately approved and re-authorized at execution time.</p><div className="riskBar"><span>RISK SCORE</span><b>82 / 100</b></div><ul><li>4 evidence objects with verified provenance</li><li>Rollback plan attached and validated</li><li>Sensitive arguments sanitized from preview</li></ul><label>DECISION RATIONALE<textarea placeholder="Required for approval or rejection" /></label><div className="modalActions"><button onClick={()=>setModal(false)}>CANCEL</button><button className="reject" onClick={()=>setModal(false)}>REJECT</button><button className="approve" onClick={()=>setModal(false)}>REQUEST SECOND APPROVAL</button></div></section></div>}
  </main>
}
