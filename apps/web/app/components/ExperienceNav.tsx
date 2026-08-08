const experienceSteps = [
  { label: 'Overview', href: 'https://www.clearglassinc.com/', external: true },
  { label: 'CG-OS', href: 'https://www.clearglassinc.com/CG-os.html', external: true },
  { label: 'Products', href: '/products' },
  { label: 'Mission control', href: '#mission-control', current: true },
]

export function ExperienceNav() {
  return (
    <nav className="experienceNav" aria-label="Artemis experience path">
      <span className="experienceLabel">YOU ARE HERE</span>
      <ol>
        {experienceSteps.map((step, index) => (
          <li key={step.label}>
            {index > 0 && <span aria-hidden="true">/</span>}
            <a
              href={step.href}
              aria-current={step.current ? 'page' : undefined}
              rel={step.external ? 'home' : undefined}
            >
              {step.label}
            </a>
          </li>
        ))}
      </ol>
      <a className="experienceCta" href="https://www.clearglassinc.com/#contact">
        REQUEST BRIEFING <span aria-hidden="true">↗</span>
      </a>
    </nav>
  )
}
