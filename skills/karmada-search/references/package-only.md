# Package-Only Search Boundaries

Use this runbook when no compatible Karmada source checkout is available.

## Evidence limits

- `APIService Available=True` proves only the supplied availability condition. It does not prove
  every pod, Service endpoint, TLS, authorization, etcd, cache, or backend boundary.
- A supplied ResourceRegistry selector that excludes the requested namespace or resource supports
  selector scope as the first boundary to investigate.
- Selector mismatch does not prove whether an informer, cache, index, or backend was created, nor
  does it rule out an independent failure.
- Do not cite or paraphrase internal packages, functions, predicates, or source paths.

## Read-only workflow

1. State the supplied condition and selector facts without expanding what they prove.
2. Identify the narrowest supported boundary, usually API availability, ResourceRegistry scope,
   cluster eligibility, response behavior, or external backend evidence.
3. Inspect the complete ResourceRegistry, relevant APIService condition, Cluster status, and the
   exact Search response with read-only commands.
4. Keep untested alternatives open and request logs or backend responses before attributing a
   concrete internal failure.
5. Describe any proposed selector or backend change in prose and request confirmation before
   emitting mutation-ready syntax.

Do not skip step 3 because the likely remediation appears obvious or the user says to fix it. Before
any remediation plan, return ordered read-only checks for every evidenced boundary. For an
unavailable APIService plus a ResourceRegistry scope mismatch, inspect the APIService condition,
backing Service and EndpointSlice or Endpoints, Search pods/logs, then the complete ResourceRegistry
and exact query response. Use placeholders when object names or namespaces were not supplied.

Package-only conclusions must stay at observable API and configuration boundaries. Exact
implementation behavior requires a compatible checkout; live behavior requires supplied runtime
evidence.
