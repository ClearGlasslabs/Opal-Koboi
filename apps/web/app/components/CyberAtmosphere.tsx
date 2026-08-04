/** Additive, non-interactive ambience for the Artemis command surface. */
export function CyberAtmosphere() {
  return (
    <div className="cyberAtmosphere" aria-hidden="true">
      <span className="atmosphereHalo haloCyan" />
      <span className="atmosphereHalo haloMagenta" />
      <span className="atmosphereHalo haloViolet" />
      <span className="scanlineField" />
      <span className="commandNoise" />
      <span className="orbitalTrail trailOne" />
      <span className="orbitalTrail trailTwo" />
    </div>
  )
}
