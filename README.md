# Team6-kit

Turn one AI agent engine (Hermes, from Nous Research) into a small team of AI agents that work together under clear rules — with a supervisor, a quality checker, and a builder that assembles your own team from ready-made parts.

Official site: https://team6.askaconsult.com/
Part of ASKA Digital: https://askaconsult.com/digital/

## What problem does it solve?

One AI agent can lose track, skip steps, or claim work is done when it isn't. Team6-kit sets up several agents with separate jobs — planner, builder, checker — and rules so that:

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

## The main rules

1. **Everything on disk.** Progress is saved to files, so months later you can still pick up where you left off.
2. **Check what is actually live.** Test on a staging copy, get approval, then publish. Never announce "done" from a local test.
3. **The maker never marks their own work.** A different agent checks it and records the result.
4. **Supervised, not autonomous.** Long tasks pause, save progress, and ask for review. Nothing runs forever unattended.

## What's new in this release (1.3.0)

When a source is handed to the team, it now needs a proper review before use: what does it contain, what is it useful for, who owns each part, and proof it works — instead of just indexing the files. See `CHANGELOG.md`.

## License

- **Engine:** Hermes by Nous Research, MIT license. This is not a fork; we build on top of it.
- **This kit (profiles, rules, builder):** Apache-2.0.
- **Vertical packs (paid settings files + service):** not in this repo; proprietary.
- Optional local models used by an adapter have their own separate license.

Full details: `LICENSING.md`.
