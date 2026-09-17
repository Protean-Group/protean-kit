#!/usr/bin/env python3
"""Tests for the install-time contribution-mode toggle.

Everything runs offline against fixture repositories built in a temporary
directory, reusing the fixtures from tests/test_kit_lock.py. No network access,
no third-party import.

Run: python3 -m unittest tests.test_contribution_mode
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_kit_lock import (FixtureCase, INSTALL, build_ingredient, lock_entry,  # noqa: E402
                           run, warm_cache, write_lock)

OPS_SLUG = "protean-ops-fixture"
STATE_TEMPLATE = """# CONTRIB-STATE - continual contribution mode (schema template)

## Header (fixed keys)

| key | value |
|---|---|
| schema_version | 1 |
| internal_contrib | on |
| external_contrib | off |
| read_at | - |
| mode_epoch | - |
| last_change | - |

## Rows (append-only; fixed columns)

| row id | kind | repo | action | thread | mode | authority | detail | lane / session | time | evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| (empty state - no rows recorded) | - | - | - | - | - | - | - | - | - | - |
"""


def header_of(path):
    header = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) == 2 and line.strip().startswith("|"):
                header[cells[0].lower()] = cells[1]
    return header


class ContributionModeCase(FixtureCase):
    def ops_fixture(self, slug=OPS_SLUG, with_template=True, **kwargs):
        extra = {"records/CONTRIB-STATE.md.tmpl": STATE_TEMPLATE} if with_template else None
        fixture = build_ingredient(self.repos, slug,
                                   install_targets=["records", "gates/" + slug],
                                   extra_files=extra, **kwargs)
        warm_cache(self.cache, slug, fixture)
        entry = lock_entry(slug, fixture)
        return fixture, write_lock(os.path.join(self.base, "kit.lock.json"), [entry])

    def install(self, target, *args, lock=None):
        return run(INSTALL, "--all", "--target", target, "--offline", "--cache", self.cache,
                   "--lock", lock, *args)


class TestContributionMode(ContributionModeCase):
    def test_the_default_is_off_and_the_record_is_written(self):
        _fixture, lock = self.ops_fixture()
        target = os.path.join(self.base, "installed")
        result = self.install(target, lock=lock)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        record = os.path.join(target, "records", "CONTRIB-STATE.md")
        self.assertTrue(os.path.isfile(record), result.stdout)
        header = header_of(record)
        self.assertEqual(header["external_contrib"], "off")
        self.assertEqual(header["internal_contrib"], "on")
        self.assertNotEqual(header["read_at"], "-")
        self.assertIn("contribution mode: off", result.stdout)
        self.assertIn("contribution state: wrote", result.stdout)

    def test_on_without_an_operator_reference_is_refused(self):
        _fixture, lock = self.ops_fixture()
        target = os.path.join(self.base, "installed")
        result = self.install(target, "--contribution-mode", "on", lock=lock)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("operator-ref", result.stdout + result.stderr)
        self.assertFalse(os.path.exists(os.path.join(target, "records", "CONTRIB-STATE.md")))

    def test_an_unknown_mode_is_a_usage_error(self):
        _fixture, lock = self.ops_fixture()
        result = self.install(os.path.join(self.base, "installed"),
                              "--contribution-mode", "maybe", lock=lock)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("off or on", result.stdout + result.stderr)

    def test_on_with_an_operator_reference_records_the_switch_row(self):
        _fixture, lock = self.ops_fixture()
        target = os.path.join(self.base, "installed")
        result = self.install(target, "--contribution-mode", "on", "--operator-ref", "OP-9",
                              lock=lock)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        record = os.path.join(target, "records", "CONTRIB-STATE.md")
        header = header_of(record)
        self.assertEqual(header["external_contrib"], "on")
        with open(record, encoding="utf-8") as fh:
            body = fh.read()
        self.assertIn("| switch |", body)
        self.assertIn("OP-9", body)
        self.assertNotIn("empty state", body)

    def test_an_existing_record_is_never_overwritten(self):
        _fixture, lock = self.ops_fixture()
        target = os.path.join(self.base, "installed")
        first = self.install(target, lock=lock)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        record = os.path.join(target, "records", "CONTRIB-STATE.md")
        with open(record, encoding="utf-8") as fh:
            before = fh.read()
        second = self.install(target, "--contribution-mode", "on", "--operator-ref", "OP-9",
                              lock=lock)
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        self.assertIn("left unchanged", second.stdout)
        with open(record, encoding="utf-8") as fh:
            self.assertEqual(before, fh.read())

    def test_mode_on_without_the_ops_template_is_exit_5(self):
        _fixture, lock = self.ops_fixture(with_template=False)
        result = self.install(os.path.join(self.base, "installed"),
                              "--contribution-mode", "on", "--operator-ref", "OP-9", lock=lock)
        self.assertEqual(result.returncode, 5, result.stdout + result.stderr)
        self.assertIn("template", result.stdout + result.stderr)

    def test_mode_off_without_the_ops_template_is_a_reported_note(self):
        _fixture, lock = self.ops_fixture(with_template=False)
        target = os.path.join(self.base, "installed")
        result = self.install(target, lock=lock)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("not in this selection", result.stdout)
        self.assertFalse(os.path.exists(os.path.join(target, "records", "CONTRIB-STATE.md")))

    def test_dry_run_reports_the_mode_and_writes_nothing(self):
        _fixture, lock = self.ops_fixture()
        target = os.path.join(self.base, "dry-target")
        result = run(INSTALL, "--all", "--target", target, "--dry-run", "--cache", self.cache,
                     "--lock", lock, "--contribution-mode", "on", "--operator-ref", "OP-9")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("contribution mode: on", result.stdout)
        self.assertIn("no files written", result.stdout)
        self.assertFalse(os.path.exists(target))


if __name__ == "__main__":
    unittest.main(verbosity=2)
