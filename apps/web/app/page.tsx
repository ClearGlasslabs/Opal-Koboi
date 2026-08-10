'use client'

import { useMemo, useState } from 'react'

type Billing = 'annual' | 'monthly'

const plans = [
  {
    id: 'basic',
    name: 'Business Basic',
    description: 'Everything a growing team needs to work securely from anywhere.',
    annual: 8.10,
    monthly: 9.72,
    features: ['Cloud productivity suite', 'Business email & 1 TB storage', 'Teams and video conferencing', 'Security and admin controls'],
  },
  {
    id: 'basic-no-teams',
    name: 'Business Basic',
    qualifier: 'Without Teams',
    description: 'The productivity essentials, without video conferencing.',
    annual: 6,
    monthly: 7.20,
    features: ['Cloud productivity suite', 'Business email & 1 TB storage', 'Browser and mobile access', 'Security and admin controls'],
  },
  {
    id: 'standard',
    name: 'Business Standard',
    description: 'Powerful desktop tools and priority support for ambitious teams.',
    annual: 17,
    monthly: 20.40,
    popular: true,
    features: ['Everything in Business Basic', 'Desktop Office applications', 'Offline access & advanced tools', 'Priority business support'],
  },
] as const

const comparison = [
  ['Cloud productivity', 'Included', 'Included', 'Included'],
  ['Teams & video', 'Included', '—', 'Included'],
  ['Desktop applications', '—', '—', 'Included'],
  ['Offline access', '—', '—', 'Included'],
  ['Admin controls', 'Basic', 'Basic', 'Advanced'],
  ['Security features', 'Included', 'Included', 'Enhanced'],
  ['Support', 'Standard', 'Standard', 'Priority'],
  ['SSO', 'Optional', 'Optional', 'Optional'],
  ['API & integrations', 'Core', 'Core', 'Advanced'],
]

const money = (value: number) => new Intl.NumberFormat('en-CA', { style: 'currency', currency: 'CAD' }).format(value)

export default function Page() {
  const [billing, setBilling] = useState<Billing>('annual')
  const [seats, setSeats] = useState(10)
  const prices = useMemo(() => plans.map((plan) => plan[billing]), [billing])

  return <main className="pricingShell">
    <nav className="pricingNav" aria-label="Primary navigation">
      <a className="pricingBrand" href="#top" aria-label="ClearGlassInc Artemis home"><span>CA</span><b>ClearGlassInc <em>Artemis</em></b></a>
      <div><a href="#plans">Plans</a><a href="#compare">Compare</a><a href="#how">How it works</a><a href="#faq">FAQ</a></div>
      <a className="navCta" href="#plans">Start free</a>
    </nav>

    <section className="pricingHero" id="top">
      <div className="heroGlow" aria-hidden="true" />
      <p className="pricingEyebrow"><span /> BUILT FOR MODERN BUSINESS</p>
      <h1>Flexible business productivity plans that <em>scale with your team.</em></h1>
      <p>Secure cloud productivity, collaboration, and business-grade tools that grow with your organization.</p>
      <div className="pricingActions"><a className="solidButton" href="#plans">Start your subscription <span>→</span></a><a className="outlineButton" href="#compare">Compare plans</a></div>
      <div className="trustStrip"><span>14-day free trial</span><span>No credit card required</span><span>Cancel anytime</span></div>
    </section>

    <section className="plansSection" id="plans">
      <div className="sectionIntro"><div><p className="pricingEyebrow">PLANS & PRICING</p><h2>Choose your way to work.</h2></div><div className="billingToggle" aria-label="Billing frequency"><button className={billing === 'monthly' ? 'active' : ''} onClick={() => setBilling('monthly')}>Monthly</button><button className={billing === 'annual' ? 'active' : ''} onClick={() => setBilling('annual')}>Annual <small>SAVE 17%</small></button></div></div>
      <div className="seatControl"><label htmlFor="seats"><b>How many people are on your team?</b><span>See your estimated total instantly.</span></label><div><button onClick={() => setSeats(Math.max(1, seats - 1))} aria-label="Remove one seat">−</button><input id="seats" type="number" min="1" max="999" value={seats} onChange={(event) => setSeats(Math.min(999, Math.max(1, Number(event.target.value) || 1)))} /><button onClick={() => setSeats(Math.min(999, seats + 1))} aria-label="Add one seat">+</button><span>users</span></div></div>

      <div className="pricingGrid">
        {plans.map((plan, index) => {
          const total = prices[index] * seats * (billing === 'annual' ? 12 : 1)
          return <article className={'popular' in plan && plan.popular ? 'planCard popular' : 'planCard'} key={plan.id}>
            {'popular' in plan && plan.popular && <div className="popularBadge">MOST POPULAR</div>}
            <header><div className={`planIcon icon${index}`} aria-hidden="true">{index === 0 ? '◇' : index === 1 ? '○' : '✦'}</div><div><h3>{plan.name}</h3>{'qualifier' in plan && <span>{plan.qualifier}</span>}</div></header>
            <p className="planDescription">{plan.description}</p>
            <div className="price"><strong>{money(prices[index])}</strong><span>CAD<br/>user / month</span></div>
            <p className="billingNote">{billing === 'annual' ? `Billed annually · ${money(prices[index] * 12)} / user` : 'Billed monthly · cancel anytime'}</p>
            <div className="planTotal"><span>{seats} users · {billing === 'annual' ? 'annual total' : 'monthly total'}</span><b>{money(total)}</b></div>
            <a className={'popular' in plan && plan.popular ? 'solidButton' : 'outlineButton'} href={`mailto:sales@clearglassinc.com?subject=${encodeURIComponent(`Start ${plan.name}${'qualifier' in plan ? ` ${plan.qualifier}` : ''}`)}`}>Start 14-day trial <span>→</span></a>
            <ul>{plan.features.map((feature) => <li key={feature}><span>✓</span>{feature}</li>)}</ul>
            <a className="compareLink" href="#compare">View full comparison ↓</a>
          </article>
        })}
      </div>
      <p className="taxNote">All prices shown in CAD, exclusive of applicable taxes. Prices are approximate and may be subject to provider changes.</p>
    </section>

    <section className="compareSection" id="compare">
      <div className="sectionIntro"><div><p className="pricingEyebrow">SIDE-BY-SIDE</p><h2>Compare every capability.</h2></div><p>Find the right fit today. Upgrade whenever your team is ready.</p></div>
      <div className="comparisonWrap"><table><caption className="srOnly">Business productivity plan comparison</caption><thead><tr><th scope="col">Capability</th><th scope="col">Business Basic</th><th scope="col">Basic<br/><small>Without Teams</small></th><th scope="col" className="recommended">Business Standard<br/><small>Recommended</small></th></tr></thead><tbody>{comparison.map((row) => <tr key={row[0]}>{row.map((cell, index) => index === 0 ? <th scope="row" key={cell}>{cell}</th> : <td key={cell + index} className={cell === 'Included' ? 'included' : ''}>{cell === 'Included' ? <><span aria-hidden="true">✓</span><span className="srOnly">Included</span></> : cell}</td>)}</tr>)}</tbody></table></div>
    </section>

    <section className="howSection" id="how"><p className="pricingEyebrow">SIMPLE BY DESIGN</p><h2>From sign-up to productive in minutes.</h2><div>{[['01','Create your account','Start your free 14-day trial. No payment method required.'],['02','Add your team','Choose seats, invite your people, and set permissions.'],['03','Work with confidence','Deploy your tools and manage everything from one place.']].map((step) => <article key={step[0]}><b>{step[0]}</b><div><h3>{step[1]}</h3><p>{step[2]}</p></div></article>)}</div></section>

    <section className="securityBand"><div><p className="pricingEyebrow">SECURITY AT THE CORE</p><h2>Your business stays yours.</h2><p>Enterprise-grade safeguards and transparent controls protect every account, file, and conversation.</p></div><ul><li><span>◈</span><b>PCI-DSS</b>Secure payments via Stripe</li><li><span>⌁</span><b>TLS 1.2+</b>Encrypted in transit</li><li><span>◎</span><b>SSO & SCIM</b>Identity-ready controls</li><li><span>◇</span><b>Audit-ready</b>Traceable administration</li></ul></section>

    <section className="faqSection" id="faq"><div><p className="pricingEyebrow">QUESTIONS, ANSWERED</p><h2>Everything you need to know.</h2></div><div>{[['Can I change plans later?','Yes. Upgrades take effect immediately with prorated billing; downgrades begin at your next renewal.'],['What happens after my trial?','We’ll remind you before your 14-day trial ends. Add a payment method to continue, or your trial simply expires.'],['How are taxes calculated?','Applicable Canadian GST, HST, or PST is calculated securely at checkout using your billing address.'],['Can I cancel at any time?','Yes. Cancel from your account and keep access through the end of your current billing period.']].map((item) => <details key={item[0]}><summary>{item[0]}<span>+</span></summary><p>{item[1]}</p></details>)}</div></section>

    <section className="finalCta"><p className="pricingEyebrow">READY WHEN YOU ARE</p><h2>Give your team room to grow.</h2><p>Start free for 14 days, or talk with our team to design the right setup.</p><div className="pricingActions"><a className="solidButton" href="#plans">Start your subscription →</a><a className="outlineButton" href="mailto:sales@clearglassinc.com">Talk to sales</a></div></section>
    <footer className="pricingFooter"><a className="pricingBrand" href="#top"><span>CA</span><b>ClearGlassInc <em>Artemis</em></b></a><p>Business productivity, made clear.</p><div><a href="/legal">Privacy</a><a href="/legal">Terms</a><a href="mailto:support@clearglassinc.com">Support</a></div><small>© 2026 ClearGlassInc Artemis</small></footer>
  </main>
}
