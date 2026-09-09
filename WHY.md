# Why Team6-kit Exists

> **Short version:** Hermes is the engine. Team6-kit is the operating layer —
> the *crew* and the *playbook* that turn a single agent into a disciplined
> multi-agent team. Different axis, not a feature add-on.

---

## The two-layer mental model

Hermes is what you install. You get profiles, skills, memory, cron, plugins
(kanban, accent, etc.), and `hermes setup` for plumbing. It's an *engine* —
the chassis, the dashboard, the wiring. It is excellent at what it does.

Team6-kit is what you instantiate *on top of* the engine. You get
persona archetypes, orchestration choreography, governance funnels, and a
generator that turns a parameter file into a configured team. It's an
*operating layer* — the crew, the playbook, the runbook.

A plugin (kanban, accent) is a *tool*. The kit is the *crew* that uses the
tools. They are not competitors any more than a steering wheel competes with
a driver. If you want a single agent with a task dashboard, you want
Hermes + kanban. If you want multiple agents working a real workflow with
governance, you want Hermes + Team6-kit.

| | Hermes | Team6-kit |
|---|---|---|
| **What it is** | The engine | The operating layer |
| **What you install** | A binary + profiles | A parameter file + the kit |
| **What you get** | Profiles, skills, plugins, memory, `hermes setup` | Persona archetypes, choreography, governance, generator, identity-onboarding |
| **Unit of work** | One agent in one room | Multiple agents in a workflow, with contracts between them |
| **Question it answers** | "How do I run an agent?" | "How should a team of agents actually work together?" |

---

## What the kit actually provides

Four deliverables, each one a thing Hermes does not ship:

### 1. Designed multi-agent behavior

Six persona archetypes with a tested orchestration contract. Hermes gives
you rooms and profiles; it gives you zero guidance on *choreography* — who
speaks first, who handoffs to whom, what the handoff artifact is, how to
read back completion. We built this from real failures: sequential handoffs
stall, role design alone doesn't change behavior, channel occupancy kills
teams, no one owns drift. That knowledge is packaged in the kit, not
implied by the engine.

### 2. Governance as code

The viability funnel (raw-capture → 13-criterion pass → disposition),
spin-off SoP, structured verdict blocks, read-back receipts, two-tier
intake (raw capture never blocks; promotion runs the pass). Hermes has no
equivalent. Building this from scratch is the work; the kit makes it a
file you commit.

### 3. Instantiation

`generate.py --params` turns a parameter file into a configured team
(identity, skills, choreography, gates). Hermes requires hand-assembling
every profile, every skill, every room. The kit's generator is the only
assembly path — a kit that cannot be built by the generator does not exist.

### 4. Identity-onboarding (the upstream contribution)

The setup agent — a built-in interview/advanced/raw initial config that
captures *who you are, what you do, what you'll use it for* and emits a
parameter file. Hermes ships `hermes setup` for plumbing (keys, providers,
platform). It does not ship identity config — the SOUL.md + profile.yaml
layer that makes a profile actually yours. The setup agent is the flagship
upstream PR, MIT-relensed back to Hermes so every Hermes user benefits.
This is the single biggest gap the kit closes, and it closes it for the
*engine* itself, not just the kit.

---

## Why the operating layer now includes supervision, durable state, provenance, and served-truth

These four additions to the kit (v1.1.0) answer real failure modes the team
kept hitting. Each is a *shape of failure we observed*, turned into a load-bearing
rule — the kit's value is that the version you get has survived these, not that
it is clever.

**Supervision.** A team that recovers from a stalled worker by "try again, harder"
is not supervised — it is hopeful. Erlang/OTP supervision trees give a precise
shape: workers do work, a supervisor restarts them under an explicit budget
(restart type, intensity per period, shutdown policy), and *exhaustion escalates*
rather than retrying forever. We adopt that shape because our own stalled-worker
recovery was unparameterized and ad hoc. `choreography/orchestration.md` §4 makes
supervision an explicit, per-role contract.

**Durable state.** In-context progress is lost the moment a worker restarts or
stalls. If correctness depended on what was in a session's context, every stall
was a silent reset. Ledgers and on-disk artifacts are the team's analogue of
Erlang process state that survives a restart: a respawned worker *resumes from
disk*, never from dead context. This is also what makes the team entropy-proof —
correct after weeks untouched, because correctness derives from what is written
down, not from what was observed (`governance.md` §6).

**Provenance.** Once a single unlicensed or unfillably-attributed asset slipped
into a build, every downstream public surface inherited the risk. Licensing is
now a gate, not a hope: verify from the primary source, keep ledger-to-disk
parity, and `ship:false` anything whose attribution can't be filled
(`governance.md` §7, `LICENSING.md`). Provenance also reaches research — every
claim is tagged with its source at retrieval, so the team never "remembers" a
fact it cannot point to.

**Served-truth verification.** "Works on my machine" and mock-only green suites
shipped latent bugs repeatedly. The rule that replaced them: *the producer never
passes the artifact*, and a change is not "live" until the actually-served bytes
prove it — staging first, user approves, then promote (`orchestration.md` §7,
§10). Per-side green suites were never enough; read-back receipts and
live-served verification are the bar.

These are design principles, not features — which is why they live in WHY.md and
the choreography/governance doctrine, and why they apply to *any* team the kit
instantiates, not just the one that built it.

---

## What the kit does NOT provide (honesty section)

- **No core-engine features.** The kit does not make a single agent
  smarter, faster, or more capable in isolation.
- **No plugin competitor.** Kanban, accent, and other plugins are *inside*
  the engine and stay there. We don't fork or replace them.
- **No magic.** A skeptic can hand-build the SOUL.md files themselves.
  The value is *not having to design this from scratch*, and getting it
  instantiated in one command.
- **No proof, yet.** Nothing is demonstrated at the time of this writing
  — no vertical packs shipped, no setup-agent install live, no stranger
  has instantiated a team from the repo. The repo currently *asserts*
  value. The first vertical pack + a working setup-agent install are
  what make these claims true, not the claims themselves.

If you read this and think "I can hand-build the orchestration in a
weekend" — you probably can. The kit's value is that you don't have to,
and that the version you get has survived the design failures we'd hit
again. That's the difference between code and a product.

---

## The service tier — why the paid layer isn't files

Because anyone can copy files, and a copy is the same as the original.
Nobody can copy the *process* of having built and run the orchestration
that survives — the tuning, the vertical-specific configuration, the
setup. So the paid tier is service: a tuned instance generated against
your parameter file, plus the setup time to make it work in your context.
The files you could copy; the *instance* you pay for. This is the same
structure the T-001 viability pass locked, and the same structure
Hermes uses: open-source engine, paid service on top.

---

## Status — v1.1.0 (operating upgrades) on top of v1.0.0

### v1.1.0 — operating upgrades (2026-09-09)

- ✅ Supervision model (Erlang/OTP-style) encoded in `choreography/orchestration.md` §4
- ✅ Supervised autonomous research loops (ledgered, check-pointed) — orchestration §5
- ✅ Phase-gated pipeline + corrected single-pass role sequence (UX no longer duplicated) — orchestration §2–3
- ✅ Producer/verifier separation + read-back receipts — orchestration §7
- ✅ Durable-state & append-only-ledger doctrine — orchestration §6
- ✅ Adversarial QA / simplicity gate + entropy-proof axiom — governance §3, §6
- ✅ License/provenance gate — governance §7, LICENSING.md
- ✅ Live check-ins & stall recovery + served-truth/staging-first — orchestration §8, §10
- ✅ Public docs updated (README, WHY, choreography, CHANGELOG, website)

### v1.0.0 — efficiency update

- ✅ Open core public (Apache-2.0) on GitHub — renamed airefea-kit → Team6-kit
- ✅ Licensing coherent (MIT provenance + Apache-2.0 kits + proprietary-by-contract packs)
- ✅ 8-surface hygiene gate (including S8 network-egress, enforcing no-telemetry by construction)
- ✅ Knowledge router skill (MoE-style activation) — shipped in templates/
- ✅ Zero-context preservation skill (direct-execution pivot) — shipped in templates/
- ✅ Open-core assembly gated (sweep + review + generate) + instantiation proof-point (demo/, examples/)
- 🔲 Setup agent authored and passing the 8-surface gate
- 🔲 Upstream PR for the setup agent
- 🔲 First vertical pack shipped (instance + service)

The efficiency update made the always-on memory footprint lean: knowledge
router + zero-context preservation are the two reusable patterns extracted
from running a real six-agent fleet on bounded-context local models. The
operating-upgrade release encoded the *operating* layer those skills run on:
supervision, durable state, provenance, and served-truth verification — the
shape of failures the team actually hit, turned into rules. The setup-agent
install, the first pack, and the first end-to-end demonstration remain the
proof gates that turn this from a repo into a product.

---

*Authored for the Team6-kit org. Reviewed by the build team. Open to
refinement as the proof points land.*
