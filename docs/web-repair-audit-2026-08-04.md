# Artemis web repair audit — 2026-08-04

## Scope and severity-ranked findings

1. **High — approval dialog was not keyboard-safe.** Focus could leave the modal, Escape did not close it, background scrolling remained active, and focus was not restored. The dialog now traps focus, supports Escape and backdrop dismissal, locks background scrolling, restores focus, and exposes its title and description to assistive technology.
2. **High — consequential approval accepted an empty rationale.** The interface described rationale as required but every action silently closed the dialog. Approval now uses a form, validates non-whitespace input, focuses and announces the inline error, and reports completed decisions through a polite live region. Rejection remains available without fabricating an approval.
3. **Medium — command navigation and signal filtering were inert.** Rail controls were unlabeled-action buttons with no behavior and FILTER did nothing. The rail is now a set of named in-page links to real sections; the filter is a stateful, keyboard-operable critical-signal toggle that preserves the selected signal state.
4. **Medium — narrow screens could clip modal actions and graph content.** Fixed graph geometry, absolute metric deltas, and an unconstrained modal produced overflow at phone sizes. Mobile rules now constrain the graph, make metric deltas participate in layout, allow modal scrolling, and stack the approval controls.
5. **Medium — linting was non-deterministic.** `next lint` opened an interactive setup prompt because no configuration existed. The project now has a committed ESLint flat configuration, an ESLint CLI script, and a separate TypeScript check.
6. **Low — the relationship visualization lacked usable semantics and focus states were inconsistent.** The graph now has a concise image alternative while its SVG is decorative, controls have visible focus indicators, and reduced-motion mode disables smooth scrolling.
7. **Low — the operator avatar falsely presented an unavailable profile action.** No profile view, route, or handler exists, so the inert button is now a non-interactive avatar without changing its appearance or content.
8. **Low — the legal route used a raw internal anchor.** It now uses Next.js client routing to avoid a document reload.
9. **Low — no production start command existed.** A standalone-server start script now matches the deployment output, and the build stages Next.js static assets beside that server.

## Verification and deployment status

The production build, ESLint, TypeScript, and all Python tests pass. The built server returned HTTP 200 for `/` and `/legal`, with the expected page content and security headers. Automated Chromium, Edge, Firefox, and WebKit binaries are not installed in this environment, and package installation is blocked by registry policy, so cross-browser interaction and screenshot capture remain an environment blocker rather than a claimed verification. Deployment was not performed; the repository is production-build-ready only.
