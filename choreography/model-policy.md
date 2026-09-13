# Dynamic model-policy operations

Rate limits belong to a provider/model route, not to an agent profile.
A route is resolved from the canonical provider, model identifier, and API host.
This keeps policy correct when a model moves between profiles, tasks, fallback
chains, or worker processes.

## Policy states

- `enforce`: reserve request and token capacity before sending. Wait only up
to the configured bound, then fail safely without making an unbounded loop.
- `observe`: record headers and 429 responses but never deny a request. Use
this while a provider's limits are unknown or account-specific.
- `unknown`: allow the request and emit telemetry. Do not invent quotas.

## Catalogue rules

1. Prefer an exact provider/model policy over a model-prefix policy.
2. Prefer a model-prefix policy over a provider-wide policy.
3. Use the API host only as a fallback identity; provider labels are not enough
when two providers share a client interface.
4. Keep independent quota domains in separate policy entries, even when they
serve the same model family.
5. Store request and token reserves explicitly. A reserve protects recovery
and review work from normal traffic consuming the entire allowance.
6. Learn from verified response headers and `Retry-After`, but never convert a
single transient response into a permanent quota claim.
7. Re-resolve policy after every provider or model fallback.
8. Counters must be scoped to the quota domain. If workers run in separate
processes, use a shared store or conservative admission at the process
boundary; process-local counters are not a global guarantee.

## Safe update procedure

1. Record the provider documentation URL and the account/tier scope.
2. Add or update one catalogue entry. Do not modify a profile-specific rule.
3. Start in `observe` mode if the evidence is incomplete.
4. Run route-matching, concurrent-admission, header-update, 429-cooldown,
and fallback-isolation tests.
5. Run the repository's public-artifact and leak gates.
6. Promote to `enforce` only after the limit and reset behavior are verified.
7. Record the change, evidence class, and affected surfaces in the project
change log.

The example catalogue is `registry/model-rate-limits.yaml.example`.
