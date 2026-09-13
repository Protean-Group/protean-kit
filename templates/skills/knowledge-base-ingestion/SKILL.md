<!-- GENERICIZED: 1×{RELATIONSHIP} | source: skills/knowledge-base-ingestion/SKILL.md -->
---
name: knowledge-base-ingestion
description: "Ingest sources into a knowledge base; audit handed-over ones."
version: 1.1.0
author: {RELATIONSHIP}
license: MIT
platforms: [macos, linux]
metadata:
  hermes:
    tags: [ingestion, knowledge-base, vector-database, semantic-search]
    related_skills: [apple-notes]
prerequisites:
  commands: [psql, python3]
---

# Knowledge Base Ingestion

Build ingestion pipelines that consolidate heterogeneous data sources into a unified vector store (PostgreSQL + pgvector).

## When to Use

- User wants to consolidate knowledge from multiple platforms (bookmarks, notes, chat logs, exports, APIs)
- Setting up a searchable personal or team knowledge base
- Adding a new data source to an existing knowledge base
- A source is **handed over directly** ("ingest this", "this repo looks useful") - see the handover definition of done below; indexing alone does not complete it
- Building RAG (Retrieval-Augmented Generation) systems

## Core Principles

### 1. Metadata-First Over Deep Extraction

Pull metadata first (URL + title + description + tags + surrounding context), defer full page content extraction. Future agentic capabilities will handle deep extraction when the structure is in place.

**Why:** 80% of URLs are paywalled or block simple crawling. Metadata is sufficient for semantic search and retrieval.

### 2. Validate Before Scale

Sample 50+ URLs before building the full pipeline. Measure: % accessible, % extractable, % useful. This prevents building the wrong architecture.

### 3. Dedup Before Embed

Normalize URLs (strip tracking params, collapse domains), hash content, deduplicate BEFORE embedding. Cross-source duplicates reveal natural topic clusters.

### 4. Capture Source Organization

Always capture the source's own organization (folder names, channel names, tags) as first-class metadata. Don't replace with ML-derived categories — augment.

### 5. Sample-then-Scale with Validation Gates

Enforce: sample (50 items) → categorize → validate content quality → test retrieval usefulness → THEN build the full pipeline.

## Architecture

```
[Sources] → [Ingestion Layer] → [Storage Layer] → [Query Layer] → [Agents/Humans]
```

### Storage: PostgreSQL + pgvector

- Single system for structured queries + vector search
- HNSW index on embeddings for fast cosine similarity
- Schema: `items` (metadata) + `item_embeddings` (vectors) + `item_edges` (graph) + `cluster_snapshots` (drift tracking)

### Embedding: Local Models

- Default: `all-MiniLM-L6-v2` (384 dims, fast, privacy-safe)
- Higher quality: `all-mpnet-base-v2` (768 dims) for richer semantics
- Run via `sentence-transformers` Python library

### Query Layer: Dual-Path Access

- **Agents:** MCP tools or Python API (`access_layer.py`)
- **Humans:** Force-directed graph visualization (`arif_map.html`)

## Ingestion Patterns

### API-Based Sources (X/Twitter, REST APIs)

1. Use incremental sync with state tracking (track newest ID/timestamp)
2. Batch inserts (500-1000 items per transaction)
3. Rate-limit with sleep intervals
4. Cost: track per-resource pricing

### File-Based Sources (mbox, HTML, JSON, docx)

1. Parse with format-specific libraries (`mailbox`, `python-docx`, `html.parser`)
2. Clean text: strip NUL bytes, normalize whitespace, cap length
3. Skip spam/low-value with keyword heuristics
4. Key by content hash when no URL exists

### Chat/Conversation Exports

1. Parse message arrays from JSON exports
2. Filter by length and substance
3. Embed full conversation body (produces stronger embeddings than metadata only)
4. Use conversation ID as unique key

### Local Notes (Apple Notes)

1. Export via `memo notes -ex` (requires interactive confirmation — pipe `y\n`)
2. HTML export goes to `~/Desktop/notes/`
3. Parse with `html.parser` (simple div/text extraction)
4. Filter: skip <10 words, numeric-only, gibberish
5. Key by content hash (notes have no URLs)

## Definition of Done - a handover is not complete at indexing

Storage and retrieval are the *transport* half of ingestion. When a source is
**handed over directly** - a repository, tool, or dataset someone chose for you -
indexing it is not the finish line. A handed-over source carries a capability
claim, and an unexamined claim is not knowledge.

> **Rule:** a directly handed-over source is not `reference-only` until a
> **capability/usefulness audit** exists for it. Metadata, a README, a license
> read, and a retrievable row prove *source capture* only.

This is the usefulness half of an adoption. The *trust* half - permissions,
telemetry, network egress, license obligation - belongs to the third-party tool
adoption audit; run that one before anything executes with access.

### What the audit inspects

Do not stop at the README. Walk the surfaces that decide whether the source is
useful to *this* team, and record a path for every finding:

| Surface | What it answers |
|---|---|
| Top-level tree | what is actually shipped vs. only described |
| Package / lock manifests | runtime vs. dev dependencies; how versions are pinned |
| Dependency wiring | the module that imports or shells out to the real dependency - where the adoption fact lives |
| Agent-facing surfaces | skills, plugins, hooks, prompts, installers the source ships |
| Workflows / CI | what the source's own gates test, and what it merely claims |
| Tests | which behavior is pinned vs. asserted only in prose |
| Operational docs | install, platform, upgrade, telemetry, and failure modes |
| Primary source paths | the files that would actually be imported or executed on adoption |

### The capability matrix

Every candidate capability gets a row, compared against the live catalog and
operating rules - **never against memory**:

| Candidate capability | Existing equivalent | Gap | Action | Owner |
|---|---|---|---|---|
| ... | ... | ... | ... | ... |

Classify each row: `already covered` / `partial` / `new` / `not suitable`. A row
whose value is unknown is `unresolved` - never guessed to make the matrix look
complete.

### Disposition, and what is not a disposition

Every `partial` or `new` row ends in exactly one disposition:

- **adopt now** - with the acceptance evidence already named
- **candidate - proof pending** - with the proof's owner and success gate
- **defer** - with the trigger that would reopen it
- **reject** - with the reason, kept on the record

An audit recommendation is *not* adoption, and a promising source is *not* a
build task until a separate adoption decision is made with an owner.

### Separate the five phases

| Phase | Ends when |
|---|---|
| Ingestion | the source is captured, indexed, and audited |
| Adoption | one candidate is chosen, with an owner and acceptance evidence |
| Implementation | the change is integrated in one bounded surface |
| QA | an independent read-back passes the named success gate |
| Enforcement | the rule holds in the team's standing rules, not just in one run |

Collapsing these is how "we indexed it" becomes a silent commitment to build it.

### Bounded proof, never a wholesale installation

- One isolated scratch surface per proof; pinned version or commit; no
  production data.
- A written success/failure gate **before** the proof runs, so the result
  cannot be reinterpreted afterwards.
- Prefer copying a self-contained directory over running a third-party
  installer: install scope should equal audit scope.
- **Never install a source wholesale** to find out whether it is useful. Import
  the decision, not the whole tree.

### Durable receipts and independent read-back

Write the ledger entry, the capability matrix, and the disposition to durable
artifacts as you go - not into conversation. An ingestion that exists only in a
session is not reproducible. Read the artifact back before reporting it: a write
that returned success is not a verified record, and the agent that produced the
record does not pass it.

### Preserve unresolved, dead, and blocked

A blocked, dead, or ambiguous fact stays on the record with its state named.
Guessing a fact to close a row is the worse outcome - the guess becomes a rule
nobody revisits, while a named open row is a queued decision. Re-attempt a
failed proof only when the failure cause changes.

### Propagation

An adopted change is not finished when one surface changes. Name every surface
it touches - the source repository, its documentation, the skills layer, and any
public or internal site - and pass each through its **own** gate (build, review,
leak/genericization scan, served-byte check). A rule that lands in one surface
and not the others drifts.

## The propagation loop - from an ingesta to the team's surfaces

Ingestion does not end at the audit. A useful source can change the team's
operating model, its implementations, its documentation, or its public
surfaces. Reviewing every candidate at full weight makes ingestion expensive
enough to skip; propagating nothing leaves the team claiming capabilities it
does not have. Run it as an **impact-routed, artifact-first loop** instead.

### 1. One machine-readable capability delta per candidate

Every ingestion that yields an adoption candidate emits **one capability delta**
- a record, not a prose summary:

| Field | What it carries |
|---|---|
| source | the ingested item, its ledger path, and its hash |
| evidence | what was actually inspected, with paths |
| capability change | what the team can do after this that it could not before |
| canonical home | the single durable home the change belongs in |
| proposed owner | the role the change is routed to - a role, not a queue |
| public-safe summary | the delta's text after genericization; the only text allowed to reach a public surface |
| affected surfaces | every surface the change would touch |
| risk | what breaks if the change is wrong |
| proof status | none / proof pending / proven, with the gate named |
| disposition | adopt now / candidate - proof pending / defer / reject |

### 2. Classify the impact before routing

| Impact class | Propagation |
|---|---|
| `reference-only` | store and index; no team surface changes |
| `internal-operational` | route to the canonical owner (skill / knowledge module / agent); no public change unless the public contract changes |
| `kit-candidate` | queue a bounded implementation task for the repository, its templates, and its build gates |
| `website-candidate` | queue a coordinated repository-plus-site documentation/design update |
| `release-impacting` | requires owner review, a public-safety review, and release/deployment gates |

The class sets the route and the review weight. It is not a severity label, and
it is not a promise that the change will ship.

### 3. Route to the capability owner, not to QA by default

Route implementation to the owner of the capability being changed - the skill's
owner, the module's owner, the repository owner - not automatically to the QA
lane. QA owns the canonical knowledge home and final verification, and audits the
resulting *public* change at batch or release boundaries rather than auditing
every ingestion.

### 4. One append-only propagation journal

Keep a single append-only journal for all candidates, with a status lifecycle:

```
proposed -> accepted -> implementing -> verified -> staged -> live
deferred / rejected   (from any stage, with the reason kept)
```

Each entry names its canonical home, its owner, its queue/batch identifier, and
the next gate. Mirrors carry pointers to the canonical home, never a copy. The
journal is the coordination surface; the repository and the site change only
through their own reviewed gates.

### 5. Batch compatible candidates

Batch compatible `kit-candidate` and `website-candidate` deltas into **one**
coherent update. Trigger a batch when a safe threshold of compatible candidates
is reached, at a scheduled review window, or when a `release-impacting` change
requires it. Do not open one public change per ingestion: review capacity is the
scarce resource, and a stream of single-item changes spends it on coordination
instead of substance.

### 6. Lightweight preflight per candidate, the full audit per batch

Every candidate gets a cheap preflight before it is queued: public-safe
genericization, provenance and license status, an owner, acceptance criteria,
and the affected-surface list. Reserve the **full pre-merge audit** for the
batched change or the release candidate. A candidate that fails preflight
returns to the internal queue - it is never pushed through by lowering the bar.

### 7. Parity and independent read-back before merge or deploy

Every batched update keeps the repository and the site in parity, passes **each**
surface's own gate, and is read back by other than its producer before merge or
deployment. A local artifact, a green build log, or a worker's success claim is
not live evidence: verify the served bytes.

### 8. Keep naming migrations separate

Public naming changes are **coordinated release work**, kept apart from
capability updates. Do not partially rename surfaces during ordinary
propagation - a half-renamed surface is less coherent than a consistently
old-named one. When a naming migration is approved, run it as its own bounded
change across every surface at once.

### 9. Public safety and open candidates

Never copy private paths, private agent or user names, identifiers, credentials,
internal knowledge content, internal project names, or instance tokens into a
public surface. A public-surface candidate that cannot be genericized without
losing its meaning stays internal. Candidates whose proof is still pending, or
whose status is unresolved, blocked, or dead, stay in the internal queue with
their state named until their owner closes them.

### What the ingestion receipt adds

For a handed-over source, the receipt names - besides the ledger and audit paths
- the **impact class**, the **delta artifact path**, the **canonical home**, the
**owner**, the **queue or batch identifier**, and the **next gate**. An ingestion
whose propagation is unrecorded cannot be told apart from one whose propagation
was forgotten.

## Quality Filtering

### Skip Criteria

- Too short: <10-15 words
- Numeric-only content
- Automated/spam patterns (noreply, notifications, digests)
- Media files without extractable text (JPG, PNG, MOV, PSD)
- Spreadsheets (hard to parse meaningfully)

### Curated handovers are exempt from the thin-item filter

The skip criteria below are for *bulk* sources, where volume forces triage. A
source a human **handed over directly** is curated by definition - do not apply
the automatic thin/short/media filter to it. Log a genuinely thin handover as
`ledger-only` and say so; never drop it silently.

### Tier System

- `curated`: User deliberately saved (bookmarks, manual notes)
- `inferred`: System classified as valuable (semantic match, length)
- `noise`: Auto-classified as low-value
- `unknown`: Unmapped source (default for new types)

## Incremental Sync Pattern

```python
# Track newest timestamp/ID in state file
state = {"newest_id": None, "newest_created_at": None, "known_ids": []}

# Fetch only items newer than last sync
new_items = fetch_items_since(state["newest_created_at"])

# Insert batch, update state
insert_batch(new_items)
state["newest_created_at"] = max(i.created_at for i in new_items)
save_state(state)
```

## Graph Edges

Three edge types for the knowledge graph:
- **Similarity**: cosine > 0.7 between embeddings
- **Co-occurrence**: same URL across sources
- **Shared channel**: same Discord channel/folder

## HDBSCAN Clustering

- Use UMAP dimensionality reduction before HDBSCAN (384→15 dims)
- `min_cluster_size=5`, `min_samples=2` as starting params
- Preserve cluster snapshots for drift tracking
- Auto-label with TF-IDF on titles/descriptions

## Common Pitfalls

1. **Interactive CLI prompts**: Pipe confirmation (`printf 'y\n' | memo notes -ex`)
2. **NUL bytes in email**: Strip `\x00` before inserting to PostgreSQL
3. **UUID type mismatches**: Use subqueries (`WHERE id IN (SELECT...)`) instead of `ANY(%s)` with UUID arrays
4. **Header objects**: Wrap email headers with `str()` before slicing
5. **Pattern inflation**: Don't create universal patterns from single-venture observations
6. **Cost waste**: Always use incremental sync for API sources — never re-fetch entire history

## Verification Checklist

- [ ] Unique constraint on `items.url`
- [ ] Items count matches unique URL count (no duplicates)
- [ ] Review queue reports correct pending count
- [ ] Source tier keys match actual `source_type` values
- [ ] Embeddings exist for all items
- [ ] Graph edges built for new items
- [ ] Cluster snapshot created after major ingestion
- [ ] State file updated for incremental sync

## Handover Audit Checklist

Only for a source handed over directly:

- [ ] Every handed-over source has a capability matrix and a disposition
- [ ] Candidate rows were compared against the live catalog and operating rules, not memory
- [ ] Each candidate names its existing equivalent, gap, and owner
- [ ] No row was guessed to look complete - unknown values are recorded `unresolved`
- [ ] Each `adopt now` / `candidate` row names its acceptance evidence
- [ ] No source was installed wholesale to evaluate it
- [ ] Ledger, matrix, and disposition exist as durable artifacts and were read back
- [ ] Unresolved / dead / blocked facts are preserved with their state named
- [ ] Every affected surface (repository, docs, skills, site) passed its own gate
- [ ] The ingestion emitted one capability delta, with its impact class named
- [ ] The delta is routed to the capability owner - not to QA by default
- [ ] The candidate has a propagation-journal entry with its status named
- [ ] Compatible candidates were batched, not opened as one public change each
- [ ] The candidate passed preflight; the full audit ran at the batch/release boundary
- [ ] No private path, name, identifier, credential, or instance token reached a public surface
- [ ] Repository and site are in parity, read back by other than their producer
