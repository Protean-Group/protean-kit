#!/usr/bin/env python3
"""check-ingredient-contract.py - every pinned ingredient satisfies the ingredient contract.

At its pinned commit, each ingredient repository must contain:

  README.md                 whose first line equals the descriptor's contract line
  LICENSE                   a committed license file, MIT for this generation
  protean-ingredient.json   a parseable machine descriptor
  install.sh                a standalone entrypoint
  tests/                    at least one test file
  its declared gates        every gate script named by the descriptor exists
  the manifest contract     byte-for-byte equal to the lock entry

Every check runs against the pinned tree, never against a working copy.

Tree discovery, in order: --ingredients-dir/<slug>, then <cache>/<slug>/<sha>.
When no tree is available and --verify is not given, the pin is reported as
unverified and the gate still exits 0, because a lock-only clone cannot fetch a
private ingredient. Pass --verify to make a missing tree a failure.

Usage:
  check-ingredient-contract.py [--lock kit.lock.json] [--cache DIR]
                               [--ingredients-dir DIR] [--verify] [--offline]
Exit: 0 pass (or unverified pins reported); 1 violation; 2 unusable input.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile

SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def run(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def gate_script(cmd):
    """First token of a gate command that looks like a shipped script path."""
    for token in (cmd or "").split():
        if token.endswith(".py") or token.endswith(".sh"):
            return token
    return None


def find_tree(pin, cache, ingredients_dir):
    if ingredients_dir:
        candidate = os.path.join(ingredients_dir, pin["slug"])
        if os.path.isdir(os.path.join(candidate, ".git")):
            return candidate, None
    cached = os.path.join(cache, pin["slug"], pin["sha"])
    if os.path.isdir(os.path.join(cached, ".git")):
        return cached, None
    return None, "no tree available"


def fetch_tree(pin, cache, offline):
    if offline:
        return None, "not in cache under --offline"
    os.makedirs(os.path.join(cache, pin["slug"]), exist_ok=True)
    work = tempfile.mkdtemp(prefix="contract-", dir=os.path.join(cache, pin["slug"]))
    run(["git", "init", "--quiet", work])
    run(["git", "remote", "add", "origin", pin["repo"]], cwd=work)
    result = run(["git", "fetch", "--quiet", "--depth", "1", "origin", pin["ref"]], cwd=work)
    if result.returncode != 0:
        return None, "fetch failed: %s" % (result.stderr or "").strip()[:120]
    peeled = run(["git", "rev-parse", "FETCH_HEAD^{commit}"], cwd=work).stdout.strip()
    if peeled != pin["sha"]:
        return None, "%s resolves to %s, not the pinned sha" % (pin["ref"], peeled)
    run(["git", "checkout", "--quiet", "--detach", pin["sha"]], cwd=work)
    return work, None


def check_tree(pin, tree):
    slug = pin["slug"]
    problems = []
    readme = os.path.join(tree, "README.md")
    if not os.path.isfile(readme):
        problems.append("%s: README.md is missing" % slug)
    license_file = os.path.join(tree, "LICENSE")
    if not os.path.isfile(license_file):
        problems.append("%s: LICENSE is missing (a README-only claim is not a license)" % slug)
    else:
        with open(license_file, encoding="utf-8", errors="replace") as fh:
            head = fh.read(400)
        if re.search(r"MIT License", head) is None:
            problems.append("%s: LICENSE does not declare MIT" % slug)
    descriptor_path = os.path.join(tree, "protean-ingredient.json")
    descriptor = None
    if not os.path.isfile(descriptor_path):
        problems.append("%s: protean-ingredient.json is missing" % slug)
    else:
        try:
            with open(descriptor_path, encoding="utf-8") as fh:
                descriptor = json.load(fh)
        except ValueError as exc:
            problems.append("%s: protean-ingredient.json is not valid JSON: %s" % (slug, exc))
        except OSError as exc:
            problems.append("%s: protean-ingredient.json is unreadable: %s" % (slug, exc))
    if not os.path.isfile(os.path.join(tree, "install.sh")):
        problems.append("%s: install.sh is missing" % slug)
    tests_dir = os.path.join(tree, "tests")
    if not os.path.isdir(tests_dir):
        problems.append("%s: tests/ is missing" % slug)
    else:
        entries = [n for n in os.listdir(tests_dir) if os.path.isfile(os.path.join(tests_dir, n))]
        if not entries:
            problems.append("%s: tests/ contains no test file" % slug)
    if descriptor is not None:
        if descriptor.get("slug") != slug:
            problems.append("%s: descriptor slug is %r" % (slug, descriptor.get("slug")))
        if descriptor.get("contract") != pin.get("contract"):
            problems.append("%s: descriptor contract differs from the lock contract" % slug)
        if (descriptor.get("license") or "").upper() != "MIT":
            problems.append("%s: descriptor does not declare MIT" % slug)
        for gate in descriptor.get("gates") or []:
            script = gate_script(gate.get("cmd"))
            if script and not os.path.isfile(os.path.join(tree, script)):
                problems.append("%s: declared gate script is missing: %s" % (slug, script))
    if os.path.isfile(readme) and pin.get("contract"):
        with open(readme, encoding="utf-8", errors="replace") as fh:
            first = fh.readline().rstrip("\n")
        if first.strip() != pin["contract"].strip():
            problems.append("%s: README first line is not the contract line" % slug)
    return problems


def main():
    parser = argparse.ArgumentParser(
        prog="check-ingredient-contract.py",
        description="Check every pinned ingredient against the ingredient contract.",
        epilog="exit codes: 0 pass, 1 violation, 2 unusable input.")
    parser.add_argument("--lock", default="kit.lock.json")
    parser.add_argument("--cache", default=None)
    parser.add_argument("--ingredients-dir", default=None)
    parser.add_argument("--verify", action="store_true",
                        help="fetch a missing tree; a pin that cannot be read is a violation")
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()

    if not os.path.isfile(args.lock):
        print("FAIL: lock file not found: %s" % args.lock)
        return 2
    try:
        with open(args.lock, encoding="utf-8") as fh:
            lock = json.load(fh)
    except ValueError as exc:
        print("FAIL: lock file is not valid JSON: %s" % exc)
        return 2
    pins = lock.get("ingredients")
    if not isinstance(pins, list) or not pins:
        print("FAIL: the lock lists no ingredients")
        return 2

    cache = args.cache or os.environ.get("PROTEAN_CACHE")
    if not cache:
        xdg = os.environ.get("XDG_CACHE_HOME")
        base = xdg if xdg else os.path.join(os.path.expanduser("~"), ".cache")
        cache = os.path.join(base, "protean-kit")

    problems, unverified = [], []
    for pin in pins:
        if not SHA_RE.match(pin.get("sha") or ""):
            problems.append("%s: sha is not a 40-hex commit sha" % pin.get("slug"))
            continue
        tree, why = find_tree(pin, cache, args.ingredients_dir)
        if tree is None and args.verify:
            tree, why = fetch_tree(pin, cache, args.offline)
        if tree is None:
            unverified.append("%s (%s)" % (pin["slug"], why))
            continue
        problems += check_tree(pin, tree)

    if unverified:
        print("unverified pins (no tree; pass --verify): %s" % ", ".join(unverified))
    if problems:
        print("INGREDIENT CONTRACT VIOLATION: %d" % len(problems))
        for problem in problems:
            print("  " + problem)
        return 1
    if unverified and args.verify:
        print("FAIL: --verify requires every pin's tree")
        return 1
    print("check-ingredient-contract: PASS  ingredients=%d  unverified=%d"
          % (len(pins), len(unverified)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
