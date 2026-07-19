# Karmada Knowledge Navigation

Use the packaged references in this directory at runtime:

- `source-map.json`: topic-to-source map for checkout inspection.
- `components.md`: component boundaries and diagnostic orientation.
- `concepts.md`: resource template, policy, placement, propagation, and multi-region mental models.
- `user-guide-index.md`: user-facing workflow topic names captured from official documentation.

Do not require website pages or repository authoring paths while using the packaged skill. When the
current checkout and packaged guidance disagree, prefer checkout API, implementation, and tests for
behavioral claims, and call out the mismatch.

## Minimal source sets

- Concept definitions and component boundaries: read `components.md` or `concepts.md`, then stop.
- User workflow terminology: read `user-guide-index.md`, then stop unless the user asks for exact
  current-checkout behavior.
- Source-backed or version-sensitive details: read only the matching topic in `source-map.json`,
  then inspect the narrow API, controller, scheduler, Search, or test path named by that topic.
- Runtime or incident questions: do not continue in this skill; route to the focused operational
  skill and ask for runtime evidence there.
