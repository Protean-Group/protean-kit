# Handover Capability Audit - record exemplar

**STATUS: ILLUSTRATIVE EXEMPLAR.** This file shows the *shape* of a handover
capability audit record. It is not the record of any specific project: the rows
below are illustrative, and nothing here is a finding or a claim about any named
repository, tool, version, or license.

Companion procedure: `templates/skills/knowledge-base-ingestion/SKILL.md`
(section *Definition of Done - a handover is not complete at indexing*). Trust,
permissions, telemetry, and license-obligation checks belong to the third-party
tool adoption audit; this record carries the usefulness / adoption half.

## 1. Source

| Field | Value |
|---|---|
| Handed over as | candidate tool / reference / unknown |
| Capture | raw bytes stored first; hash recorded in the ledger |
| Ledger path | durable artifact path (never a chat transcript) |
| Retrievable | yes / no - content embedded, not URL-only |

## 2. Surfaces inspected

Record a path per surface, or an explicit `not present`:

- [ ] top-level tree
- [ ] package / lock manifests
- [ ] dependency-wiring module
- [ ] agent-facing skills / plugins / hooks
- [ ] workflows / CI
- [ ] tests
- [ ] operational docs (install, platform, upgrade, failure modes)
- [ ] primary source paths that would be imported or executed

## 3. Capability matrix (illustrative)

| Candidate capability | Existing equivalent | Gap | Action | Owner |
|---|---|---|---|---|
| <capability> | <team skill or rule already covering it> | none | already covered | none |
| <capability> | <partial coverage> | missing case | candidate - proof pending | <owner> |
| <capability> | none | new | defer | <owner> |

Comparison basis: name the live catalog and operating rules consulted, with the
date consulted. "Compared from memory" is not a comparison basis.

## 4. Dispositions

Per row: `adopt now` / `candidate - proof pending` / `defer` / `reject`, each
with its acceptance evidence or its reopening trigger. Nothing is `adopt now`
without named acceptance evidence, and nothing is adopted because an audit
recommended it.

## 5. Unresolved / blocked / dead

| Fact | State | Why it stays open |
|---|---|---|
| <fact> | unresolved / blocked / dead | <the missing evidence, and what would change it> |

An empty table is itself a claim - it asserts nothing was left open. Write it
empty only when that is true.

## 6. Phase, impact class, and propagation

| Phase | State | Evidence |
|---|---|---|
| Ingestion | | |
| Adoption | | |
| Implementation | | |
| QA | | |
| Enforcement | | |

**Impact class** (sets the route and the review weight - pick one):
`reference-only` / `internal-operational` / `kit-candidate` / `website-candidate`
/ `release-impacting`. Implementation routes to the **capability owner**; QA
audits the resulting public change at the batch or release boundary, not per
ingestion.

**Capability delta** (illustrative shape - one per candidate):

| Field | Value |
|---|---|
| source | ledger path + hash of the raw artifact |
| evidence | what was inspected, with paths |
| capability change | what the team can do after this that it could not before |
| canonical home | the one durable home the change belongs in |
| proposed owner | the role the delta is routed to |
| public-safe summary | the delta's text after genericization |
| affected surfaces | every surface the change would touch |
| risk | what breaks if the change is wrong |
| proof status | none / proof pending / proven, with the gate named |
| disposition | adopt now / candidate - proof pending / defer / reject |

**Propagation-journal entry** (one append-only entry per candidate):

| Field | Value |
|---|---|
| status | proposed / accepted / implementing / verified / staged / live / deferred / rejected |
| canonical home | |
| owner | |
| queue or batch id | |
| next gate | |

Affected surfaces, and the gate each one passed:

| Surface | Gate | Result |
|---|---|---|
| source repository | leak / genericization scan | |
| documentation | review gate | |
| skills layer | build + review | |
| site | served-byte check | |

Repository and site must be in **parity**, and the result read back by other
than its producer, before merge or deployment. A local artifact, a green build
log, or a worker's success claim is not live evidence. Naming migrations are
**separate** coordinated release work - no partial renames during ordinary
propagation. A candidate whose proof is pending, or whose status is unresolved,
blocked, or dead, stays in the internal queue with its state named.

## 7. Read-back

- Record read back on: <date / command>
- Read back by: the agent that did **not** write it
- Not verified: <named explicitly, or "none">
