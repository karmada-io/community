# Karmada Search Operational Runbook

Use this runbook for `karmada-search`, `search.karmada.io`, global cache queries, and resource
proxying. It is self-contained for runtime use.

Implementation paths below are citation hints. Diagnose APIService, deployment flags,
ResourceRegistry scope, Cluster eligibility, cache sync, backend, and proxy evidence first. Open
source files only for conflicts, source-level proof requests, or behavior not captured in this
runbook.

## Required Inputs

Ask for missing inputs when they affect the next read-only check:

- Karmada control-plane kube context and namespace.
- Install method: Helm, static manifests, operator, or custom deployment.
- Affected endpoint, for example `/apis/search.karmada.io/v1alpha1/search/cache/...` or
  `/apis/search.karmada.io/v1alpha1/proxying/...`.
- Resource API version, kind, namespace, name, and expected member Cluster.
- Relevant `ResourceRegistry` name or selector intent.
- Error text, HTTP status, incident time window, and recent registry/cluster/search changes.
- Current `karmada-search` container args, especially `--disable-search`, `--disable-proxy`,
  kubeconfig, authn/authz kubeconfig, etcd, TLS, bind address, and QPS/burst settings.

## Read-Only First

Allowed first:

```bash
kubectl --context <karmada-context> -n <karmada-namespace> get deploy,po,svc -l app=karmada-search -o wide
kubectl --context <karmada-context> get apiservice | grep search.karmada.io
kubectl --context <karmada-context> describe apiservice v1alpha1.search.karmada.io
kubectl --context <karmada-context> -n <karmada-namespace> get po -l app=karmada-search -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[0].args}{"\n"}{end}'
kubectl --context <karmada-context> -n <karmada-namespace> logs deploy/karmada-search --since=<duration> --tail=<lines>
kubectl --context <karmada-context> get resourceregistries.search.karmada.io -o yaml
kubectl --context <karmada-context> get cluster <cluster-name> -o yaml
kubectl --context <karmada-context> get --raw '<search-api-path>'
```

Before explicit operator confirmation, remediation must be prose only. Do not output write-command
syntax, code blocks, or one-liners that mutate Search, registry, backend, RBAC, member, or cluster
state. This includes any `kubectl` command whose verb is `apply`, `patch`, `delete`, `create`,
`replace`, `edit`, `scale`, `set`, `label`, `annotate`, or `rollout`, and any write-like request
through `/proxying/`. Also avoid naming the exact write command form, such as "kubectl patch" or
"kubectl apply", until the operator confirms.
Do not provide mutation-ready YAML, JSON Patch, merge patch, shell one-liners, or proxy request
bodies before confirmation; describe the intended state change in prose instead.
It is acceptable to name or analyze a risky operation supplied by the user when clearly marking it as
unsafe, but do not repeat complete executable mutation syntax or extend it before approval.

Do not initially recommend:

- Creating, updating, or deleting `ResourceRegistry`.
- Editing APIService, TLS secrets, kubeconfig secrets, Deployment args, or etcd settings.
- Restarting `karmada-search`, deleting pods, widening RBAC, or changing backend credentials.
- Sending `PUT`, `PATCH`, `POST`, or `DELETE` through `/proxying/` to member clusters.

If mutation is justified, separate it into a prose remediation plan, state blast radius, and ask for
explicit operator confirmation before giving write commands.

Certainty does not waive this boundary. If `ResourceRegistry` scope is clearly wrong, do not provide
the selector-changing command, manifest, patch body, or equivalent code block in the same response.
State the exact intended selector in prose, explain why restart/reindex is not useful, and ask the
operator to confirm the registry name, scope, and readiness to mutate.

## Component And API Boundaries

`karmada-search` starts an aggregated API server. Its Search and Proxy capabilities are optional and
can be disabled independently by flags.

| Boundary | Evidence | Source-backed behavior |
|---|---|---|
| API aggregation | APIService, Service endpoints, pod readiness, TLS/authn/authz config | Search API is served under `search.karmada.io/v1alpha1` |
| Search API disabled | args include `--disable-search=true`; `/search/cache` missing or 404 | `search` REST storage is installed only when the Search controller exists |
| Proxy API disabled | args include `--disable-proxy=true`; `/proxying` missing or 404 | `proxying` REST storage is installed only when the proxy controller exists |
| ResourceRegistry storage | `resourceregistries.search.karmada.io` CRUD/list/watch | ResourceRegistry is cluster-scoped and stored by the aggregated server |
| Search cache query | `/apis/search.karmada.io/v1alpha1/search/cache/<native-path>` | Reads objects from per-cluster informer caches and annotates source cluster |
| Proxy query | `/apis/search.karmada.io/v1alpha1/proxying/<name>/proxy/<native-path>` | Rewrites to a native Kubernetes path and dispatches through Search proxy plugins |
| Default backend | no matched `backendStore.openSearch` | Uses the default cache/event handler path, not an external search engine |
| OpenSearch backend | matched ResourceRegistry has `spec.backendStore.openSearch` | Creates an OpenSearch client, index, and upsert/delete event handler |

Checkout-only implementation paths (navigation hints, not package-only evidence):

- `cmd/karmada-search/app/karmada-search.go`: process startup, post-start hooks, Search/proxy wiring.
- `cmd/karmada-search/app/options/options.go`: `--disable-search`, `--disable-proxy`, kubeconfig,
  authn/authz, etcd, serving, and API QPS flags.
- `pkg/search/apiserver.go`: installs `resourceregistries`, `search`, and `proxying` REST storage.
- `pkg/search/controller.go`: ResourceRegistry and Cluster watchers, per-cluster informer setup,
  Cluster Ready/APIEnablements checks, and backend selection.
- `pkg/registry/search/storage/cache.go`: `search/cache` response from informer caches.
- `pkg/search/backendstore`: default and OpenSearch backend event handlers.
- `pkg/search/proxy/controller.go` and `pkg/registry/search/storage/proxy.go`: proxy cache and
  request routing.

When using these as final-answer evidence, keep them as repo-relative plain text. Do not turn them
into Markdown links and do not include absolute checkout paths, `/tmp`, `/private/var`, or evaluation
workspace directories.

## ResourceRegistry Scope

Search never promises universal visibility. Confirm all of these before blaming storage:

1. A `ResourceRegistry` exists.
2. `spec.targetCluster` matches the expected Cluster by name or label selector.
3. `spec.resourceSelectors` includes the resource `apiVersion`, `kind`, and optional namespace.
4. The Cluster is Ready and not being deleted.
5. The Cluster reports the resource API as enabled; disabled APIs are skipped.
6. `karmada-search` can build a member dynamic client from the Cluster secret and can list/watch the
   selected resource.
7. The cache has had time to start and sync after registry or cluster changes.

Read-only checks:

```bash
kubectl --context <karmada-context> get resourceregistries.search.karmada.io <registry-name> -o yaml
kubectl --context <karmada-context> get cluster <cluster-name> --show-labels
kubectl --context <karmada-context> get cluster <cluster-name> -o jsonpath='{.status.conditions}{"\n"}{.status.apiEnablements}{"\n"}'
kubectl --context <karmada-context> -n <karmada-namespace> logs deploy/karmada-search --since=<duration> --tail=<lines> | grep -E 'ResourceRegistry|registries|Add informer|Start informer|notReady|not enabled|Failed to get gvr|cache member cluster|<cluster-name>|<kind>'
```

Common outcomes:

- No `ResourceRegistry`: the object should not be searchable yet.
- Target cluster selector does not match: Search is behaving as configured.
- Namespace selector is narrower than the query: adjust the diagnostic expectation before proposing
  registry changes.
- Cluster not Ready or API disabled: Search will skip or stop caching that cluster/resource.
- `Failed to get gvr`: verify the resource API/version/kind and discovery in the Karmada control
  plane before blaming backend storage.

## Search Cache Path

Use this for read-only global queries:

```bash
kubectl --context <karmada-context> get --raw '/apis/search.karmada.io/v1alpha1/search/cache/apis/apps/v1/deployments'
kubectl --context <karmada-context> get --raw '/apis/search.karmada.io/v1alpha1/search/cache/apis/apps/v1/namespaces/<namespace>/deployments'
kubectl --context <karmada-context> get --raw '/apis/search.karmada.io/v1alpha1/search/cache/api/v1/pods'
```

Expected evidence:

- Returned objects should carry the source-cluster annotation added by Search cache handling.
- Empty results are not enough to prove a failure; compare with registry scope, Cluster Ready, API
  enablement, and logs.
- If `/search/cache` itself is unavailable, investigate APIService/deployment/`--disable-search`
  before ResourceRegistry matching.

## OpenSearch Path

Only investigate OpenSearch when a matched `ResourceRegistry` has:

```yaml
spec:
  backendStore:
    openSearch:
      addresses:
      - <endpoint>
      secretRef:
        namespace: <namespace>
        name: <secret>
```

Read-only checks:

```bash
kubectl --context <karmada-context> get resourceregistries.search.karmada.io -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.backendStore.openSearch}{"\n"}{end}'
kubectl --context <karmada-context> -n <secret-namespace> get secret <secret-name> -o jsonpath='{.metadata.name}{"\n"}'
kubectl --context <karmada-context> -n <karmada-namespace> logs deploy/karmada-search --since=<duration> --tail=<lines> | grep -E 'opensearch|OpenSearch|create index|Cannot upsert|cannot init client|cannot create backend'
```

If `backendStore.openSearch` is absent, say OpenSearch is not in the current Search path. Do not ask
operators to inspect OpenSearch credentials or indices.

## Proxy Path

Proxying is different from cache search. It can handle read and write-like HTTP verbs, and write-like
operations may be routed to member clusters. Treat it as production-impacting.

Read-only proxy checks:

```bash
kubectl --context <karmada-context> get --raw '/apis/search.karmada.io/v1alpha1/proxying/<name>/proxy/api/v1/nodes'
kubectl --context <karmada-context> -n <karmada-namespace> logs deploy/karmada-search --since=<duration> --tail=<lines> | grep -E 'proxy|ProxyingREST|proxy-controller|Readiness|<cluster-name>|<resource>'
```

Do not provide `PUT`, `PATCH`, `POST`, or `DELETE` proxy commands without explicit confirmation.

## Routing Boundaries

- Workload not propagated, `Work` conditions, member object absent after scheduling:
  `karmada-debug-propagation`.
- Why a cluster was selected or skipped by scheduler: `karmada-explain-placement`.
- Controller-manager process, cluster status, binding generation, Push execution/status, failover:
  `karmada-controller-manager`.
- Policy YAML creation or static review: `karmada-create-policy` or `karmada-audit-policy`.
- Generic architecture without an operational Search symptom: `karmada-knowledge`.

## Response Shape

Use this structure:

```markdown
Confirmed Search facts:
Missing inputs:
Boundary classification:
Read-only checks:
Likely causes, ranked:
Outside Search:
Remediation plan requiring confirmation:
```
## Test coverage

- Focused Search end-to-end coverage: `test/e2e/suites/base/search_test.go`
- Coverage notes: `test/e2e/suites/base/coverage_docs/search_test.md`
