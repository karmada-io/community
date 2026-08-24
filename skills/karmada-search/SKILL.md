---
name: karmada-search
description: Use when a Karmada operator needs to inspect karmada-search, search.karmada.io APIService health, ResourceRegistry scope, global search/cache results, proxying behavior, default cache versus OpenSearch, or deployment flags, or when a contributor needs to change Search API, registry storage, cache, proxy, backend, command wiring, or tests. Do not use for local repository search, generic kubectl queries, policy YAML, scheduler placement, controller-manager ownership, or propagation failures before Search is isolated.
---

# Operate and Develop Karmada Search

Determine whether a global-resource-view or proxy symptom is owned by `karmada-search`, its
configuration, its ResourceRegistry scope, or an adjacent component.

## Runtime Mode

- Package-only mode supports Search diagnosis from bundled architecture and supplied configuration,
  objects, logs, and responses; do not claim exact implementation behavior.
- In package-only mode, do not cite `pkg/`, `cmd/`, or test paths, name internal predicates or
  informer behavior, or rule out cache/backend defects that were not directly tested. Report the
  most supported boundary and keep alternatives open.
- `APIService Available=True` confirms only the supplied availability condition; it does not by
  itself prove each pod, Service endpoint, TLS, authorization, etcd, cache, or backend boundary.
  Likewise, a ResourceRegistry scope mismatch supports scope as the first boundary but does not
  prove how informers were constructed or exclude independent failures.
- With a compatible Karmada checkout, verify exact Search behavior against its API,
  implementation, command wiring, and tests when needed.
- Live Search state and backend conclusions require supplied runtime evidence.
- When evidence identifies multiple independent boundaries, keep them separate and provide ordered
  read-only checks for each before discussing remediation. Do not collapse an unavailable
  APIService and an excluding ResourceRegistry into one backend cause.
- Never skip the ordered read-only collection section merely because a likely remediation is
  visible or the user demands an immediate fix.

## Critical Production Boundary

If the next action would mutate production Search state, stop at prose and ask for explicit operator
confirmation. This is true even when the root cause is certain and the user is pressuring for an
immediate command. Do not provide alternate mutation commands as a "safer" replacement for a restart.
For `ResourceRegistry`, APIService, deployment args, RBAC, backend credentials, member objects, or
proxy writes, describe the intended state change and blast radius only. After confirmation, provide
the exact command.

## Workflow

1. Establish package-only versus checkout-enhanced mode. In package-only mode, read only
   `references/package-only.md` and do not read `references/architecture.md`. With a compatible
   checkout, read `references/architecture.md` as the source-navigation runbook and verify its paths
   before citing behavior. Do not require shared knowledge directories, generated source maps,
   website pages, or external documentation.
2. Confirm the search anchor before diagnosing: Karmada context, Karmada namespace, install method
   when known, affected API path, ResourceRegistry name, resource API version/kind/namespace/name,
   target Cluster name, observed error, incident time window, and current `karmada-search` args.
3. Start read-only. Use `get`, `describe`, raw API calls, events, bounded logs, and object inspection.
   Before explicit operator confirmation, remediation must be prose only: do not output write-command
   syntax, code blocks, or one-liners that mutate `ResourceRegistry`, APIService, Search deployment
   flags, RBAC, backend credentials, member resources, or cluster state. This includes any `kubectl`
   command whose verb is `apply`, `patch`, `delete`, `create`, `replace`, `edit`, `scale`, `set`,
   `label`, `annotate`, or `rollout`, and any write-like `proxying` request. Also avoid naming the
   exact executable write command until the operator confirms.
   Do not provide mutation-ready YAML, JSON Patch, merge patch, shell one-liners, or proxy request
   bodies before confirmation; describe the intended state change in prose instead.
   It is acceptable to name or analyze a risky operation supplied by the user when clearly marking it
   as unsafe, but do not repeat complete executable mutation syntax or extend it before approval.
   For a requested proxy write, collect the exact proxy API path, matched ResourceRegistry, target
   Cluster and namespace, authorization evidence, APIService condition, current Search args, and
   bounded `karmada-search` logs before asking for final mutation confirmation.
4. Classify the boundary:
   - APIService/deployment: pod, Service, TLS, APIService availability, kubeconfig, etcd, flags
   - Search API disabled: `--disable-search` or missing `search` REST storage
   - Proxy API disabled: `--disable-proxy` or missing `proxying` REST storage
   - ResourceRegistry scope: target cluster selector, resource selector, namespace, backend config
   - cluster eligibility: Cluster Ready, APIEnablements, member connectivity, permissions
   - cache/default store: informer manager, cache sync, annotation with source cluster
   - OpenSearch backend: only when `spec.backendStore.openSearch` exists for a matched registry
   - proxy routing: `proxying` URL parsing, registered resource behavior, direct member operation
5. State what evidence is `confirmed`, `missing`, `stale`, or `outside Search`. Rank causes only after
   boundary evidence exists.
6. Route adjacent work: scheduler placement to `karmada-explain-placement`, workload execution to
   `karmada-debug-propagation`, controller health/failover to `karmada-controller-manager`, policy
   generation/review to policy skills, and general architecture to `karmada-knowledge`.
7. Return confirmed facts, missing inputs, first failing Search boundary, ordered read-only commands,
   likely causes with confidence, and a separate prose remediation plan that asks for confirmation
   before production mutation. If the user asks for the command now, refuse to provide write syntax
   until confirmation. If a `ResourceRegistry` selector change is the likely fix, do not emit the
   selector-changing command, manifest, patch body, or equivalent code block yet; ask the operator to
   confirm the registry name, selector scope, and readiness to mutate.
8. When citing implementation evidence, use repo-relative plain paths such as
   `pkg/registry/search/storage/proxy.go:84`. Never emit absolute temporary checkout paths, `/tmp`,
   `/private/var`, or Markdown links to local source files.
   Cite those paths only after inspecting a compatible checkout; packaged architecture notes are
   not source inspection.

## Contributor workflow

When the primary request is a checkout-local Search implementation change:

1. Classify ownership as aggregated API storage, ResourceRegistry API/admission, informer/cache,
   default or OpenSearch backend, proxy routing, command options, or deployment wiring.
2. Trace the interface and concrete implementations before editing. Preserve default-store behavior
   when changing optional OpenSearch support, and preserve cache/proxy separation.
3. Review command flags, API registration, authentication and authorization boundaries, generated
   clients or APIs, deployment/RBAC manifests, and backward compatibility when affected.
4. Add focused unit tests for the changed boundary and identify the relevant Search end-to-end test,
   including `test/e2e/suites/base/search_test.go` when the change affects backend selection,
   registry handling, cache visibility, or proxy behavior.
5. Do not use a contributor code request as authorization to mutate a live ResourceRegistry,
   backend credential, APIService, or member resource.

## Guardrails

- Search results are limited by `ResourceRegistry.spec.targetCluster`, `resourceSelectors`,
  namespace scope, Cluster Ready state, APIEnablements, permissions, cache sync, and backend state.
- A member resource existing does not imply it should appear in Search; it must be selected and
  cached or routed through a registered proxy path.
- Do not assume OpenSearch is enabled. The default cache path is normal unless a matched
  `ResourceRegistry` configures `backendStore.openSearch`.
- `search/cache` is read-only global query behavior. `proxying` can route write-like HTTP verbs to
  member clusters, so never provide proxy mutation commands as a first response.
- Do not treat `karmada-search` as local source-code search or as the workload propagation pipeline.
- Do not leak evaluation or local workspace paths. Source evidence must be stable repo-relative
  paths, not absolute filesystem paths.
