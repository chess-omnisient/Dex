"""CLAUDE.md must reflect CLAUDE-custom.md without waiting for an update.

The bug these cover: composition ran only inside the delivered-release
transaction, so a personal instruction did nothing until the next update
applied — silently, because the file saved and the content was correct.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

import pytest

from core.transaction.lock import acquire_owned_lock
from core.update.apply_update import CompositionError
from core.utils import doctor
from core.utils.claude_composition import (
    RecomposeUnavailable,
    compose_current,
    installed_release_tag,
    needs_recompose,
    recompose_if_needed,
)

TEMPLATE = (
    b"# Dex\n\nPreamble that the release owns.\n\n"
    b"## USER_EXTENSIONS_START\n"
    b"## USER_EXTENSIONS_END\n\n"
    b"## Trailing release section\n"
)
VERSION = "9.9.9"
TAG = f"dist/release/v{VERSION}-abc1234"


def _vault(tmp_path: Path, *, custom: bytes | None = b"\n## Mine\n\nDo the thing.\n") -> Path:
    """A vault with a real brain store carrying the release template at TAG."""
    root = tmp_path / "vault"
    (root / "System/.dex/lifecycle").mkdir(parents=True)
    (root / "System/.dex/lifecycle/activation.json").write_text(
        json.dumps({"bridge_release_version": VERSION})
    )

    work = tmp_path / "work"
    work.mkdir()
    (work / "CLAUDE.md").write_bytes(TEMPLATE)
    env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@t", "PATH": "/usr/bin:/bin:/usr/local/bin"}
    subprocess.run(["git", "init", "-q"], cwd=work, check=True, env=env)
    subprocess.run(["git", "add", "-A"], cwd=work, check=True, env=env)
    subprocess.run(["git", "commit", "-qm", "release"], cwd=work, check=True, env=env)
    subprocess.run(["git", "tag", TAG], cwd=work, check=True, env=env)
    subprocess.run(["git", "clone", "-q", "--bare", str(work), str(root / ".dex/brain.git")],
                   check=True, env=env)

    if custom is not None:
        (root / "CLAUDE-custom.md").write_bytes(custom)
    return root


def test_composes_the_custom_block_into_claude(tmp_path):
    root = _vault(tmp_path)
    out = compose_current(root)
    assert b"Do the thing." in out
    assert b"USER_EXTENSIONS_START" not in out, "markers must be consumed"
    assert b"Trailing release section" in out, "release content after the block must survive"


def test_recompose_writes_when_custom_is_newer(tmp_path):
    root = _vault(tmp_path)
    (root / "CLAUDE.md").write_bytes(b"stale\n")
    os.utime(root / "CLAUDE.md", (time.time() - 60, time.time() - 60))

    assert needs_recompose(root) is True
    assert recompose_if_needed(root) == "recomposed"
    assert b"Do the thing." in (root / "CLAUDE.md").read_bytes()
    # and it settles: a second call is a no-op
    assert recompose_if_needed(root) == "current"


def test_absent_custom_block_is_not_drift(tmp_path):
    """A vault with no personal instructions is a valid state, not a fault."""
    root = _vault(tmp_path, custom=None)
    assert needs_recompose(root) is False
    assert recompose_if_needed(root) == "current"


def test_missing_brain_store_reports_unavailable_not_clean(tmp_path):
    """Not being able to check is different from having nothing to fix.

    Reporting "current" here would be the silent-success failure this whole
    change exists to remove.
    """
    root = _vault(tmp_path)
    shutil.rmtree(root / ".dex/brain.git")
    (root / "CLAUDE.md").write_bytes(b"stale\n")
    os.utime(root / "CLAUDE.md", (time.time() - 60, time.time() - 60))

    with pytest.raises(RecomposeUnavailable):
        compose_current(root)
    assert recompose_if_needed(root).startswith("unavailable:")


def test_ambiguous_release_tags_fail_closed(tmp_path):
    """Two tags for one version must refuse, not pick one.

    Composing from the wrong template would produce a CLAUDE.md for a release
    that is not installed, and nothing downstream would notice.
    """
    root = _vault(tmp_path)
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin"}
    subprocess.run(
        ["git", f"--git-dir={root / '.dex/brain.git'}", "tag",
         f"dist/release/v{VERSION}-def5678", TAG],
        check=True, env=env,
    )
    with pytest.raises(RecomposeUnavailable, match="tags match"):
        installed_release_tag(root)


def test_existing_claude_is_untouched_when_composition_fails(tmp_path):
    """A half-written instruction file is worse than a stale one."""
    root = _vault(tmp_path)
    marker = b"the file the user already had\n"
    (root / "CLAUDE.md").write_bytes(marker)
    os.utime(root / "CLAUDE.md", (time.time() - 60, time.time() - 60))
    shutil.rmtree(root / ".dex/brain.git")

    assert recompose_if_needed(root).startswith("unavailable:")
    assert (root / "CLAUDE.md").read_bytes() == marker


def test_touch_without_content_change_settles(tmp_path):
    """The cheap mtime gate may false-positive; the byte check must absorb it."""
    root = _vault(tmp_path)
    assert recompose_if_needed(root) == "recomposed"
    os.utime(root / "CLAUDE.md", (time.time() - 60, time.time() - 60))
    (root / "CLAUDE-custom.md").touch()
    assert needs_recompose(root) is True, "gate trips on touch, by design"
    assert recompose_if_needed(root) == "current", "byte check finds no change"
    assert needs_recompose(root) is False, "and the gate stops firing"


# --- The Doctor probe -------------------------------------------------------
#
# The hook is the fix; this probe is the detector for the hook having failed.
# An untested detector is the silent-success failure this change exists to
# remove, so every verdict branch is exercised here.


def _context(root: Path) -> doctor.DoctorContext:
    return doctor.DoctorContext(
        vault_root=root,
        repo_root=root,
        home=root / "home",
        now=datetime(2026, 8, 17, tzinfo=timezone.utc),
    )


def test_probe_reports_off_when_there_are_no_customisations(tmp_path):
    """No custom block is healthy optional absence, not a fault to nag about."""
    result = doctor._probe_claude_composition(_context(_vault(tmp_path, custom=None)))

    assert result.verdict == "OFF"
    assert result.feature_status == "off"


def test_probe_is_ok_when_the_custom_block_is_live(tmp_path):
    root = _vault(tmp_path)
    assert recompose_if_needed(root) == "recomposed"

    assert doctor._probe_claude_composition(_context(root)).verdict == "OK"


def test_probe_reports_broken_when_claude_has_drifted(tmp_path):
    """Drift means personal instructions are silently not loaded."""
    root = _vault(tmp_path)
    (root / "CLAUDE.md").write_bytes(b"stale, missing the custom block\n")

    result = doctor._probe_claude_composition(_context(root))

    assert result.verdict == "BROKEN"
    assert "not being loaded" in result.detail
    assert result.heal is not None and not result.heal.applied
    assert "python" not in result.heal.action.lower()


def test_the_tier2_advice_names_a_route_that_actually_repairs(tmp_path):
    """Doctor's printed advice must lead to a repair, not merely sound like one.

    "Send any message" was wrong for this case. The everyday refresh is
    mtime-gated and here CLAUDE.md is the newer file, so following that advice
    leaves the drift in place and the next checkup reports BROKEN again. That is
    the same silent-success shape as the original bug, moved into the remedy.

    Asserting the wording alone cannot catch this, which is how it survived. So
    this walks both routes and checks which one actually ends in OK.
    """
    root = _vault(tmp_path)
    (root / "CLAUDE.md").write_bytes(b"stale, missing the custom block\n")
    context = _context(root)

    advice = doctor._probe_claude_composition(context).heal.action

    # The route the advice used to name does nothing in this case.
    assert recompose_if_needed(root) == "current"
    assert doctor._probe_claude_composition(context).verdict == "BROKEN"

    # The route it names now repairs, and the advice has to point at it.
    assert "/dex-doctor" in advice
    doctor._apply_t1_heals(context)
    assert doctor._probe_claude_composition(context).verdict == "OK"


def test_mtime_gate_does_not_repair_stale_claude_written_after_custom(tmp_path):
    """Doctor's drift case: CLAUDE.md is newer, so the everyday path no-ops."""
    root = _vault(tmp_path)
    (root / "CLAUDE.md").write_bytes(b"stale, missing the custom block\n")

    assert needs_recompose(root) is False
    assert recompose_if_needed(root) == "current"
    assert (root / "CLAUDE.md").read_bytes() == b"stale, missing the custom block\n"


def test_force_recomposes_when_content_has_drifted_but_custom_is_not_newer(tmp_path):
    """The force/bytes path must write the case the mtime gate cannot see."""
    root = _vault(tmp_path)
    (root / "CLAUDE.md").write_bytes(b"stale, missing the custom block\n")

    assert recompose_if_needed(root, force=True) == "recomposed"
    assert b"Do the thing." in (root / "CLAUDE.md").read_bytes()
    assert recompose_if_needed(root, force=True) == "current"


def test_doctor_heal_repairs_content_drift_when_custom_is_not_newer(tmp_path):
    """The prescribed heal must actually write, not point at a no-op path."""
    root = _vault(tmp_path)
    (root / "CLAUDE.md").write_bytes(b"stale, missing the custom block\n")
    context = _context(root)

    assert doctor._probe_claude_composition(context).verdict == "BROKEN"
    action = doctor._heal_claude_composition(context)

    assert action is not None
    assert "python" not in action.lower()
    assert b"Do the thing." in (root / "CLAUDE.md").read_bytes()
    assert doctor._probe_claude_composition(context).verdict == "OK"


def test_refuses_to_write_when_mutation_lock_is_held(tmp_path):
    """A hook must not compose from a stale tag over an in-flight update."""
    root = _vault(tmp_path)
    stale = b"stale, must not be overwritten during an update\n"
    (root / "CLAUDE.md").write_bytes(stale)
    os.utime(root / "CLAUDE.md", (time.time() - 60, time.time() - 60))
    assert needs_recompose(root) is True

    release = acquire_owned_lock(root, "transaction:update-in-flight")
    try:
        result = recompose_if_needed(root)
        assert result.startswith("unavailable:")
        assert (root / "CLAUDE.md").read_bytes() == stale
        forced = recompose_if_needed(root, force=True)
        assert forced.startswith("unavailable:")
        assert (root / "CLAUDE.md").read_bytes() == stale
    finally:
        release()

    assert recompose_if_needed(root) == "recomposed"
    assert b"Do the thing." in (root / "CLAUDE.md").read_bytes()


def test_apply_t1_heals_runs_the_force_composition_refresh(tmp_path, monkeypatch):
    """Doctor --heal must call the force path, not only prescribe a message."""
    root = _vault(tmp_path)
    calls = []
    monkeypatch.setattr(
        doctor,
        "_heal_claude_composition",
        lambda context: calls.append(context.vault_root) or "refreshed CLAUDE.md so your customisations are live",
    )
    monkeypatch.setattr(doctor, "_repo_shipped_executables", lambda _context: [])
    monkeypatch.setattr(doctor, "_paths_export_for", lambda _context: {})
    monkeypatch.setattr(doctor, "_env_permission_finding", lambda _context: None)
    monkeypatch.setattr(doctor, "_acknowledge_resolved_preflight_errors", lambda _context: 0)
    monkeypatch.setattr(
        doctor,
        "_probe_capability_rooms",
        lambda _context: doctor.ProbeResult("OK", "rooms"),
    )
    context = _context(root)
    for name in doctor.PARA_PATH_NAMES:
        context.core_path(name).mkdir(parents=True, exist_ok=True)
    (root / "core").mkdir(exist_ok=True)
    (root / "core/paths.json").write_text("{}\n")

    actions, errors = doctor._apply_t1_heals(context)

    assert calls == [root]
    assert actions["config.claude_composition"] == [
        "refreshed CLAUDE.md so your customisations are live"
    ]
    assert errors == []


def test_compose_current_refuses_symlink_custom_file(tmp_path):
    """A symlink custom file is CompositionError on the update path too."""
    root = _vault(tmp_path, custom=None)
    target = root / "elsewhere.md"
    target.write_bytes(b"must not be followed\n")
    (root / "CLAUDE-custom.md").symlink_to(target)

    with pytest.raises(CompositionError, match="not a regular file"):
        compose_current(root)
    assert recompose_if_needed(root, force=True).startswith("unavailable:composition refused:")


def test_probe_reports_broken_when_claude_is_absent_entirely(tmp_path):
    root = _vault(tmp_path)
    assert not (root / "CLAUDE.md").exists()

    result = doctor._probe_claude_composition(_context(root))

    assert result.verdict == "BROKEN"
    assert result.heal is not None


def test_probe_reports_unknown_when_it_cannot_check(tmp_path):
    """Not being able to check must never be reported as a clean result."""
    root = _vault(tmp_path)
    (root / "CLAUDE.md").write_bytes(b"anything\n")
    shutil.rmtree(root / ".dex/brain.git")

    result = doctor._probe_claude_composition(_context(root))

    assert result.verdict == "UNKNOWN"
    assert "Could not check" in result.detail
