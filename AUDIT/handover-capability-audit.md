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

## 6. Phase and propagation

| Phase | State | Evidence |
|---|---|---|
| Ingestion | | |
| Adoption | | |
| Implementation | | |
| QA | | |
| Enforcement | | |

Affected surfaces, and the gate each one passed:

| Surface | Gate | Result |
|---|---|---|
| source repository | leak / genericization scan | |
| documentation | review gate | |
| skills layer | build + review | |
| site | served-byte check | |

## 7. Read-back

- Record read back on: <date / command>
- Read back by: the agent that did **not** write it
- Not verified: <named explicitly, or "none">
