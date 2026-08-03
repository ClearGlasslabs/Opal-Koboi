type NeonPulseProps = {
  variant?: 'cyan' | 'violet' | 'magenta' | 'signal'
  position?: 'top' | 'bottom' | 'frame'
  className?: string
}

/** Decorative, non-interactive edge light shared by Artemis focal surfaces. */
export function NeonPulse({
  variant = 'cyan',
  position = 'frame',
  className = '',
}: NeonPulseProps) {
  return (
    <span
      aria-hidden="true"
      className={`neonPulse neonPulse--${variant} neonPulse--${position} ${className}`.trim()}
    />
  )
}
