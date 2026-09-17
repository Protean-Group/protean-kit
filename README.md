# Protean Kit

Turn one AI agent engine (Hermes, from Nous Research) into a small team of AI agents that work together under clear rules — with a supervisor, a quality checker, and a builder that assembles your own team from ready-made parts.

Canonical site: https://proteus.askaconsult.com/

The canonical site is the public documentation for Protean Kit. For the
service listing, see the canonical site.

## What's new in this release (1.8.0)

### What

Add three choreography rules plus the README, CHANGELOG, and site entries that carry them:

1. **Fresh-branch requirement** (choreography/open-source-contribution.md) — every contribution branch must be created from a fresh fetch of the target repository's default branch.
2. **Commit serialization boundary** (choreography/orchestration.md) — stage and commit must be serialized for a declared file set.
3. **Stale-tree hazard worked example** (choreography/self-improving-flywheel.md) — encodes the same incident as rule 1.
4. **Session-start router** (templates/personas/SOUL.md.tmpl) — at session start, read the orchestration contract once and apply it before the first dispatch.
5. **Mirror forks rule** (choreography/self-improving-flywheel.md) — when one repository has mirror forks, one change must reach every mirror with consistent author identity and file set.
6. **Peer-team cross-review** (choreography/orchestration.md) — a second team may review a staged PR via a written handoff message carried by the operator.

These rules prevent PRs that revert or duplicate existing work due to stale branches, enable multi-mirror consistency, and provide a clean cross-team review procedure. The README, CHANGELOG, and index.html surfaces carry the change.

### Why

During an orchestration test, a stale branch 14 commits behind origin/main was used as a PR base, which would have deleted content already shipped on main. A stale base produces a PR that reverts or duplicates existing work.

### Evidence

[VERIFIED — internal operating record] Grounded in the team's shared doctrine and dated session history.

Source of truth: https://github.com/aska-digital/protean-kit

## What problem does it solve?

One AI agent can lose track, skip steps, or claim work is done when it isn't. Protean Kit sets up several agents with separate jobs — planner, builder, checker — and rules so that:

- Work is checked by a different agent than the one that did it.
- Progress is saved on disk, so a crashed agent can resume where it left off.
- Long tasks pause for review instead of running silently forever.
- Knowledge is stored in small files that load only when needed.

## How you use it

1. Pick a ready-made agent profile from `templates/` (each has a role and rules).
2. Add a settings file from `registry/` with your own values.
3. Run the builder, which checks everything and creates your team folder:

```
python3 build/sweep-gate.py      # check the source files are in order
python3 build/review-gate.py     # check every item has been reviewed
python3 build/generate.py --out my-team [--params my-settings.yaml]
```

You get a folder with your team's agents, ready to run.

## What's in the repo

| Folder | What it is |
|---|---|
| `templates/` | Ready-made agent profiles and generic skills |
| `build/` | The builder scripts (the only way to create a team) |
| `registry/` | Settings files you can customize |
| `choreography/` | How the team works together and the rules it follows |
| `AUDIT/` | Records of where content came from |
| `WHY.md` | Why the system is designed this way |
| `CHANGELOG.md` | What changed in each release |

## Model rate-limit protection

The kit includes a route-based model-policy catalogue. It follows a model by
provider, model identifier, and API host, so the policy remains correct when a
model moves between agents, tasks, fallback chains, or worker processes. Known
limits can be enforced with bounded waiting and protected request/token
reserves. Unknown limits stay observe-only; the kit never invents a quota.

Start with `registry/model-rate-limits.yaml.example` and read
`choreography/model-policy.md` before adding provider values. Keep the policy
catalogue separate from profile names and account credentials.

## I/O delegation contract

The kit also documents a **vendor-neutral I/O delegation contract**: an opt-in
routing pattern that may offload predictable, read-heavy summarization or
pattern-conforming scaffolding to a cheaper worker, while the frontier agent
keeps edits, debugging, architecture, security/safety-critical work, ambiguous
requirements, and final acceptance. It is never automatic just because a file
is large, never transmits sensitive content, and every delegation is recorded
with route and byte/latency telemetry. It is a contract and an example config
— not a runtime, hook, or dependency.

Start with `registry/io-delegation.yaml.example` and read
`choreography/io-delegation.md`. Route identity follows the same
provider/model/API-host rules as `choreography/model-policy.md`, and input must
pass the local privacy/redaction policy (`choreography/local-preprocessing.md`)
first. Thresholds are recommendations, not universal claims.

## Artifact contracts and resume handoffs

Every stage boundary — producer to verifier, failed run to resumed run —
carries one handoff file: expected artifacts, required sections, size bounds,
tests, evidence refs, runtime state (local/staged/live), failure state, last
stable phase, resume phase, feedback applied, what to regenerate, and what not
to touch. Protean Team Kanban remains the state authority; the contract is the
handoff snapshot written out of it. Read
`choreography/artifact-contract.md`, start from
`templates/contracts/artifact-contract.md.tmpl`, and gate with
`python3 build/check-artifact-contract.py <contract>` (or `--self-test`).
The pattern is a conceptual adoption; no external orchestration code is
included or required.

A finished worker stays reachable. When a one-shot run ends, it leaves its
session saved, so a follow-up can be sent to that same session. The worker
answers that single turn, then stops again.

This lets you add one correction or ask one question after a task is done
without starting a new session or losing the thread. Send a follow-up only
after the worker has fully stopped, and only for a turn that reads state.
Never attach a second live writer to a session that is still running.

## Release gate verification

The kit includes a deterministic release gate runner at `build/verify-all.py`.
It runs all public gates in documented order and fails if any check fails.
GitHub Actions runs this automatically on push and pull requests to ensure
the repository stays in a verified state.

Read `choreography/release-gates.md` for the full gate list and order.
**Fresh-clone contract validator gate.** The kit's validators are now exercised
as part of the fresh-clone test. Run `bash scripts/fresh-clone-test.sh` to
clone HEAD to a temp dir and verify (1) frozen artifacts are present, (2) live
artifacts are absent, (3) the demo reproduces, (4) the audit is honest, and
(5) all contract validators pass their self-tests. The aggregator script
`build/check-contracts.py` runs the artifact-contract, preflight, and report
validators in sequence; it is stdlib-only, requires no network or credentials,
and fails closed on errors.

## Router trust-boundary protection

Model routers and relays can see plaintext requests and responses, and may sit
between a model provider and the tools an agent runs. Read
`choreography/router-security.md` before enabling one. It provides a generic
preflight checklist for endpoint trust, credential minimization, high-risk tool
gates, autonomous execution, metadata-only audit logs, and conditional or
dependency-targeted tampering tests. It is guidance only: it does not install a
router, change provider settings, or claim that a route has end-to-end response
integrity.

## Side-effect and cost preflight

Before running an operation that edits files, contacts external systems, uses
credentials, incurs paid operations, affects public surfaces, or needs
rollback, write one preflight document: what changes, what it contacts, which
credential *names* (never values) it needs, what it may cost, which actions
are conditional, what becomes public, how to recover, who approves, and what
is still unknown. `choreography/side-effect-cost-preflight.md` defines the
contract; `build/preflight/check.py` is a dependency-free validator that fails
closed on missing fields, credential values, unbounded waits, or missing
rollback. It is a Protean Team internal operating pattern for side-effect and cost
preflight. The Protean Team Kanban board remains the authoritative task record.

## OpenShorts route (external, docs only)

Finished short-video production requests — where you explicitly ask for a rendered
short — route to OpenShorts, an external local-first tool Protean Team has studied as a
reference. This is a documentation route only: Protean Kit does not bundle or run
OpenShorts, does not render video by itself, and does not post, publish, or schedule
anything on your behalf. Transcript, summary, and media-research requests stay on the
existing media skills. You install OpenShorts separately and check its current license
and dependency terms before use; the route ends at a local export you review.

Start with `registry/openshorts-route.yaml.example` and read
`choreography/openshorts-route.md`.

## Safe shareable run packet

When a run finishes, the people who need to know about it are usually not at the
terminal that ran it. A run packet is the one artifact that travels: objective,
decisions, verified evidence, unresolved items, changed artifacts, test results,
runtime/live status, next gate, provenance, and redaction status.
`choreography/safe-run-packet.md` defines the contract; `build/report/check.py`
is a dependency-free validator that fails closed on a missing required field,
evidence marked verified without evidence, a live status without target or
evidence, omitted unresolved items, an internal path or profile identity, a
credential-like value, or an off-convention placeholder. It is a conceptual
operating pattern adapted from the general idea of an agency-orchestration run
report — no Agency Orchestrator code is copied — and the Protean Team Kanban board
remains authoritative: the packet is a derived shareable report, not a second
state store.

## Execution evidence

The kit defines a vendor-neutral execution-evidence contract that records what
an agent actually executed, not only that a procedure ran. It specifies evidence
record fields, distinguishes procedure evidence from achieved-state evidence,
and establishes rules for token accounting (innermost spans only), cost honesty
(unknown models remain unknown), run comparison with stable step keys, and
bounded retention with no secrets or raw prompts by default.
Read `choreography/run-evidence.md`.

## The Protean Kit distribution (lock version 1)

This repository is also the composer of the Protean Kit: it pins six standalone
ingredients, and one command installs the whole set.

```
bash install.sh --all --target ./protean-installed
```

Preview the plan first. The composer supports `--dry-run`; it prints the
selection, the resolved install order, the target, the network mode, and the
planned writes, and it writes nothing.

```
bash install.sh --all --target ./protean-installed --dry-run
```

The composer holds the lock, the installer, the documentation, and the gates. It
**contains no ingredient payload and no submodule**: composition is manifest-only.
Each ingredient is fetched from its pinned tag, verified against the tag's peeled
commit SHA and its tree hash, installed, and then read back file by file.

### Ingredients

| slug | one-line contract | requires | recommends | installs to |
|---|---|---|---|---|
| `protean-doctrine` | The operating doctrine: the default pipeline, role delegation map, handoff protocol, QA gates, and external-writing discipline. | none | none | `skills/protean-operating-doctrine`, `skills/external-writing-discipline`, `gates/protean-doctrine` |
| `protean-ops` | The dispatch/rotation/inflight ops kit: append-only record schemas and the deterministic gates that check them. | none | none | `records`, `scripts/protean-ops`, `gates/protean-ops` |
| `protean-sym2p` | SYM-2P: a compact versioned agentic message language - one canonical JSON packet per line over durable text artifacts - with validator, enums, and fixtures. | none | `protean-ops` | `SPEC.md`, `skills/sym2p`, `scripts/protean-sym2p`, `templates/protean-sym2p`, `examples/protean-sym2p`, `AUDIT/protean-sym2p`, `gates/protean-sym2p` |
| `protean-drafts` | The draft-review pipeline: render a draft as a self-contained dark HTML review page through one command that runs the prose, identifier, quote-integrity, and render-fidelity gates. | none | `protean-doctrine` | `skills/draft-review-html`, `scripts/protean-drafts`, `templates/protean-drafts`, `gates/protean-drafts` |
| `protean-github-flow` | The GitHub workflow skill pack: issue triage, issue-to-PR, PR lifecycle, PR audit, and upstream-contribution procedures. | none | `protean-drafts`, `protean-doctrine` | `skills/github-issues`, `skills/github-issue-to-pr`, `skills/github-pr-workflow`, `skills/github-pr-audit`, `skills/upstream-contribution-pr`, `gates/protean-github-flow` |
| `protean-control-plane` | The control-plane skill pack: one canonical procedure home that routes a request to the minimum skill bundle, with the gate table and failure policy. | `protean-doctrine`, `protean-ops` | `protean-drafts`, `protean-github-flow`, `protean-sym2p` | `skills/protean-control-plane`, `gates/protean-control-plane` |

The exact install targets, the pinned SHA, and the tree hash of each ingredient
are recorded in `kit.lock.json`, which is authoritative.

### Dependency behaviour

Two edge kinds exist. `requires` is hard: the closure is fetched and installed.
`recommends` is soft: it is reported and never fetched.

The lock declares the install order in `installOrder`, and the resolver validates
that declaration against the dependency graph before it is used. A declaration
that is not a valid topological order of the selection is reported, and the
resolver's own topological order is used instead. A `requires` cycle is a hard
failure with the cycle path printed, and it is never resolved by dropping an
edge.

Only `protean-control-plane` declares `requires` edges, on `protean-doctrine` and
`protean-ops`. Every other edge in the version 1 set is `recommends`.

```
bash install.sh --ingredient protean-drafts --target ./protean-installed
```

`protean-drafts` has no hard requirements, so exactly one repository is fetched
and written. The full kit is not touched and not fetched.

```
bash install.sh --ingredient protean-control-plane --target ./protean-installed
```

`protean-control-plane` resolves to exactly three repositories: doctrine, ops, and
itself. Its skill cites the record gates, so it declares the dependency instead of
copying the files.

```
bash install.sh --ingredient protean-control-plane --no-deps --target ./protean-installed
```

`--no-deps` is a deliberate degraded mode. It writes exactly one repository and
reports the unresolved requirements as `degraded`, and the control plane reports
its cited gates as `unavailable` instead of failing for it. The control plane is
not fully operational in that mode, and the summary says so.

### Offline and cache

The cache is content-addressed by commit SHA: `<cache>/<slug>/<sha>/`, where the
cache root is `$PROTEAN_CACHE`, else `${XDG_CACHE_HOME:-$HOME/.cache}/protean-kit`.
A cache entry is immutable while it matches its SHA, and the same SHA is never
fetched twice.

```
bash install.sh --all --target ./protean-installed --offline
```

`--offline` makes zero network calls and installs from the cache only. A missing
or mismatched entry fails closed with exit 4, naming the slug. A warm cache run
with `--offline` is the way to prove an install needs no network.

### Target, staging, and read-back

The default target is `$HERMES_TEAM_SKILLS` when that is set, else `./installed`;
public instructions pass `--target` explicitly so the write boundary is visible.
Writes are staged under `<target>/.protean-staging/<slug>/` and promoted only
after that ingredient's own gates pass, so a mid-run failure leaves no half
written ingredient on the target. Every written file is then re-hashed against
its cached blob.

### Troubleshooting

The exit code is the reliable signal for automation. Errors go to stderr, the
summary to stdout.

| Exit | Meaning | Recovery |
|---|---|---|
| `1` | usage or input is invalid | Correct the flag or the slug, and read `--help`. |
| `2` | the kit lock is invalid | Use a valid lock. Do not bypass the allowlist, the tag rule, or the schema check. |
| `3` | dependency resolution failed | Repair the lock, or use `--no-deps` only when degraded operation is acceptable. |
| `4` | integrity check failed | Refresh the cache in online mode from the pinned ref, or restore a matching warm cache. Never substitute another SHA. |
| `5` | install failed | Fix the target permissions or the ingredient defect. The run is not successful. |
| `6` | post-install verification failed | Understand the mismatch, then rerun. The target holds an incomplete install, and the summary reports it. |

A run that installs five of six ingredients exits non-zero. There is no partial
success zero.

### Verify this release

```
python3 build/check-lock.py kit.lock.json --verify
python3 build/check-ingredient-contract.py --lock kit.lock.json --verify
python3 -m unittest tests.test_kit_lock
```

`check-lock.py` validates the lock and, with `--verify`, recomputes every pin's
tag pairing and tree hash. `check-ingredient-contract.py` checks each pinned
ingredient at its pinned commit for `README.md`, a committed `LICENSE`, its
descriptor, its entrypoint, its declared gates, and a non-empty `tests/`. Without
a warm cache or a sibling checkout, both gates report the pins as unverified
rather than inventing a result.

### Limits and open items

- The ingredient repositories ship under the MIT license. Each commits its own
  `LICENSE` file, which is authoritative for that repository.
- The version 1 set pins six ingredients. Whether every one of them belongs in
  version 1 is an open item recorded by the project, not a decision made here.
- The protocol ingredient carries its own open items; the installer reports them
  in its summary and never resolves them.
- The composer's own brand strings and the site registry still name the
  predecessor product; that rename is a user decision, not a packaging change.

## The main rules

1. **Everything on disk.** Progress is saved to files, so months later you can still pick up where you left off.
2. **Check what is actually live.** Test on a staging copy, get approval, then publish. Never announce "done" from a local test.
3. **The maker never marks their own work.** A different agent checks it and records the result.
4. **Supervised, not autonomous.** Long tasks pause, save progress, and ask for review. Nothing runs forever unattended.

For work performed with an AI coding agent, use the compact
`choreography/ai-assisted-development.md` contract. It adds behavior-first
testing, security checks, scope control, and evidence requirements without
replacing the Protean Team ownership and QA gates.

## What's new in this release (1.5.0)

Every stage boundary can now carry one machine-checkable handoff contract: expected artifacts, required sections, size bounds, tests, evidence refs, runtime state (local/staged/live), failure state, resume phase, feedback applied, artifacts to regenerate, and artifacts not to touch. See `choreography/artifact-contract.md` and `build/check-artifact-contract.py`; Protean Team Kanban remains the state authority. The previous release added the route-based model-policy catalogue (`choreography/model-policy.md`). See `CHANGELOG.md`.

## What's new in this release (1.4.1)

The kit now includes a route-based model-policy catalogue for changing provider limits, plus a generic router trust-boundary and tool-execution safety contract. Unknown limits remain observe-only, while verified limits can use bounded admission and protected reserves. See `CHANGELOG.md`, `choreography/model-policy.md`, and `choreography/router-security.md`.

## License

- **Engine:** Hermes by Nous Research, MIT license. This is not a fork; we build on top of it.
- **This kit (profiles, rules, builder):** Apache-2.0.
- **Pinned ingredients (lock version 1):** MIT, each under its own committed `LICENSE` file.
- **Vertical packs (paid settings files + service):** not in this repo; proprietary.
- Optional local models used by an adapter have their own separate license.

Licensing follows the zone model in `LICENSING.md`; the committed `LICENSE` file
in each repository is authoritative for that repository.
