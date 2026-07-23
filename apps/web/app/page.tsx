const navigation = ['Vision', 'Services', 'Products ▾', 'Government', 'Insights', 'Contact']

function ClearGlassSeal() {
  return (
    <svg className="seal" viewBox="0 0 200 200" role="img" aria-label="FED SASE silver eagle seal embedded in crystalline glass">
      <defs>
        <radialGradient id="sealCrystal" cx="50%" cy="36%" r="70%">
          <stop offset="0%" stopColor="#ffffff" stopOpacity="0.95" />
          <stop offset="42%" stopColor="#dff8ff" stopOpacity="0.52" />
          <stop offset="76%" stopColor="#8ca5bb" stopOpacity="0.26" />
          <stop offset="100%" stopColor="#ffffff" stopOpacity="0.08" />
        </radialGradient>
        <linearGradient id="sealChrome" x1="18" x2="182" y1="18" y2="182">
          <stop stopColor="#ffffff" />
          <stop offset="0.3" stopColor="#93a8bd" />
          <stop offset="0.55" stopColor="#f7fbff" />
          <stop offset="1" stopColor="#64758e" />
        </linearGradient>
        <filter id="sealDepth" x="-25%" y="-25%" width="150%" height="150%">
          <feDropShadow dx="0" dy="7" stdDeviation="6" floodColor="#020712" floodOpacity="0.38" />
          <feDropShadow dx="0" dy="0" stdDeviation="5" floodColor="#b8f6ff" floodOpacity="0.38" />
        </filter>
        <path id="topArc" d="M 42 104 A 58 58 0 0 1 158 104" />
        <path id="bottomArc" d="M 158 102 A 58 58 0 0 1 42 102" />
      </defs>
      <circle cx="100" cy="100" r="96" fill="rgba(255,255,255,0.08)" stroke="url(#sealChrome)" strokeWidth="4" />
      <circle cx="100" cy="100" r="82" fill="url(#sealCrystal)" stroke="rgba(255,255,255,0.75)" strokeWidth="1.6" filter="url(#sealDepth)" />
      <circle cx="100" cy="100" r="68" fill="rgba(10,26,52,0.1)" stroke="rgba(190,235,255,0.5)" strokeWidth="1" />
      <text className="sealText"><textPath href="#topArc" startOffset="50%" textAnchor="middle">FED SASE</textPath></text>
      <text className="sealText sealTextSmall"><textPath href="#bottomArc" startOffset="50%" textAnchor="middle">SECURE ACCESS</textPath></text>
      {Array.from({ length: 12 }).map((_, i) => {
        const a = (i * 30 - 90) * Math.PI / 180
        const x = 100 + Math.cos(a) * 74
        const y = 100 + Math.sin(a) * 74
        return <path key={i} d={`M ${x} ${y - 4} L ${x + 1.3} ${y - 1.1} L ${x + 4.5} ${y - 1.1} L ${x + 1.8} ${y + .8} L ${x + 2.8} ${y + 4} L ${x} ${y + 2.1} L ${x - 2.8} ${y + 4} L ${x - 1.8} ${y + .8} L ${x - 4.5} ${y - 1.1} L ${x - 1.3} ${y - 1.1} Z`} fill="#f8fdff" opacity="0.86" />
      })}
      <g className="eagle" fill="none" stroke="url(#sealChrome)" strokeLinecap="round" strokeLinejoin="round">
        <path d="M52 91 C70 77 83 77 97 91 C111 77 130 76 149 91 C128 92 116 101 104 114 C91 101 75 92 52 91Z" strokeWidth="5" />
        <path d="M100 72 C107 81 108 94 100 105 C92 94 93 81 100 72Z" strokeWidth="4" fill="rgba(255,255,255,0.18)" />
        <path d="M100 70 L112 58 L107 77" strokeWidth="3.5" />
        <path d="M88 119 L112 119 L108 146 L92 146Z" strokeWidth="4" fill="rgba(8,24,50,0.18)" />
        <path d="M96 122 L96 143 M104 122 L104 143 M90 131 L110 131" strokeWidth="1.8" opacity="0.75" />
        <path d="M76 116 C65 127 61 137 58 149 M124 116 C135 127 139 137 142 149" strokeWidth="3" />
      </g>
      <path d="M45 49 C72 23 128 23 155 49" fill="none" stroke="rgba(255,255,255,0.52)" strokeWidth="2" />
    </svg>
  )
}

export default function Page() {
  return (
    <main className="mockup" aria-label="ClearGlassInc 2040 website header mockup">
      <section className="composition">
        <nav className="commandBar" aria-label="Primary navigation">
          <div className="brandCluster">
            <div className="holoHousing"><ClearGlassSeal /></div>
            <a className="brand" href="#vision" aria-label="ClearGlassInc 2040 home"><span>ClearGlassInc.</span><em>2040</em></a>
          </div>
          <div className="navLinks">
            {navigation.map((item) => <a href={`#${item.toLowerCase().replace(' ▾', '')}`} key={item}>{item}</a>)}
          </div>
          <a className="cta" href="#engagement"><span className="shieldIcon" aria-hidden="true" />Book a Security Engagement</a>
        </nav>
        <section className="cityHero" aria-label="Futuristic enterprise city hero image">
          <div className="skyGrid" />
          <div className="moon" />
          <div className="aerial aerialOne" />
          <div className="aerial aerialTwo" />
          <div className="tower towerOne" /><div className="tower towerTwo" /><div className="tower towerThree" /><div className="tower towerFour" /><div className="tower towerFive" />
          <div className="haze" />
        </section>
      </section>
    </main>
  )
}
