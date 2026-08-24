---
name: karmada-audit-policy
description: Use this skill when the user provides or points to Karmada PropagationPolicy, ClusterPropagationPolicy, OverridePolicy, or ClusterOverridePolicy YAML and wants validation, review, risk analysis, or corrections. Audit schema and admission rules, selector scope, placement and replica semantics, priority and preemption, override patches, and runtime-dependent assumptions with source-backed findings. Do not use it primarily to generate a policy from new intent, explain one observed placement, debug live propagation, or update the skill knowledge base.
---

# Audit Karmada Policy

Review supplied policy objects without claiming more certainty than the available checkout and
runtime evidence support.

## Runtime Mode

- Package-only mode supports known policy findings and review of supplied YAML; distinguish
  unverified exact-version assumptions from confirmed findings.
- In package-only mode, never call an object decoded, valid, admitted, defaulted, or accepted unless
  supplied server evidence proves it. Omitted-field behavior is unverified unless a packaged known
  finding explicitly covers it.
- With a compatible Karmada checkout, verify unknown or version-sensitive findings against its API,
  validation, and tests.
- Live admission, placement, and propagation conclusions require supplied runtime evidence.

## Workflow

1. If no YAML or path is supplied, ask for it. Do not substitute repository examples.
2. Read `references/findings.md`.
3. Parse all supplied documents and build an object inventory.
   If a document is explicitly truncated or incomplete, report its parse status separately and ask
   for the complete document before making semantic findings about omitted fields or defaults.
4. Report decode/schema/admission errors before operational warnings.
5. For accepted broad behavior, report effective scope and blast radius instead of marking it invalid.
6. Separate runtime-dependent checks from deterministic findings.
7. Provide corrected YAML only when requested or when the fix is unambiguous and non-mutating.
8. When citing checkout sources, use repo-relative plain paths such as
   `pkg/apis/policy/v1alpha1/override_types.go:59`. Never emit absolute temporary checkout paths,
   `/tmp`, `/private/var`, or Markdown links to local source files.

## Source-read gate

- First match the supplied YAML against the deterministic finding classes in
  `references/findings.md`. Use those known routes before opening checkout source.
- Do not inspect scheduler, controller, or runtime implementation for static YAML findings. Static
  review should stop at API shape, webhook/admission, shared validation, packaged policy workflow,
  and supplied YAML.
- Open current checkout source only for an unknown field, ambiguous admission rule, version-sensitive
  behavior, or when a correction depends on exact current-checkout semantics.
- When the remaining question is runtime-dependent, stop and ask for the needed Cluster, binding,
  Work, workload, event, feature-gate, or dry-run evidence.

## Guardrails

- YAML parsing alone is not policy validation.
- A syntactically parseable fragment can still be incomplete. Do not interpret absent fields,
  defaults, selector breadth, or admission behavior for a document the user says is truncated.
- Do not treat omitted fields as errors when current admission defaults them.
- Do not call a broad selector invalid when it is accepted; report its effective scope and risk.
- Do not turn package familiarity into an admission result. Say which checks require a compatible
  API/CRD, webhook, or server-side dry-run instead of asserting that they passed.
- When an unknown or disputed field is described without the object, request the exact field path
  and complete policy YAML before issuing findings. A runbook claim and absence from packaged
  guidance are not enough to decide admission.
- Do not predict actual selected clusters without the required runtime objects.
- Do not recommend converting a namespaced policy to `ClusterPropagationPolicy` or
  `ClusterOverridePolicy` merely to bypass namespace validation. Prefer a namespace-local fix, or
  ask for explicit cluster-scoped intent and warn about the wider blast radius.
- Do not use public documentation as stronger evidence than current API, webhook, implementation,
  and tests.
- Never apply, patch, or delete audited resources implicitly.
- Do not apply, patch, delete, restart, or remove finalizers. When the user asks to fix a live
  policy, provide a corrected manifest or patch plan and ask before any mutation.
- In the first audit answer, do not include executable non-dry-run `kubectl apply`, `kubectl patch`,
  `kubectl delete`, or equivalent write commands. Provide corrected YAML and server-side dry-run
  commands only; ask for explicit confirmation before giving live write or cleanup commands.
- Do not leak evaluation or local workspace paths. Source evidence must be stable repo-relative
  paths, not absolute filesystem paths.

## Routing boundaries

Use `karmada-create-policy` when the primary request is to translate new intent into YAML. Use
`karmada-explain-placement` for a concrete scheduler result and `karmada-debug-propagation` when the
question begins with an observed propagation failure.
