import nextVitals from 'eslint-config-next/core-web-vitals'
import nextTypeScript from 'eslint-config-next/typescript'

// eslint-plugin-react bundled by Next 16 still calls the pre-ESLint 10 rule
// context API. Keep the remainder of Next's recommended rules active while
// that upstream plugin catches up instead of allowing lint to crash before it
// examines any source files.
const eslint10Compatibility = {
  name: 'clearglass/eslint-10-compatibility',
  rules: Object.fromEntries(
    nextVitals.flatMap((config) => Object.keys(config.rules ?? {}))
      .filter((rule) => rule.startsWith('react/'))
      .map((rule) => [rule, 'off']),
  ),
}

const config = [
  ...nextVitals,
  ...nextTypeScript,
  eslint10Compatibility,
  { ignores: ['.next/**', 'node_modules/**', 'next-env.d.ts'] },
]

export default config
