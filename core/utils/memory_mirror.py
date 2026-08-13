#!/usr/bin/env python3
"""Copy Claude Code's per-project auto-memory into the vault.

Claude Code stores per-project memory outside the vault, at
``~/.claude/projects/<encoded>/memory/``. That folder is not git, has no Dex
backup, and losing it does not error — sessions just get quietly worse.

This module mirrors that directory into ``System/memory-mirror/`` so it rides
the vault's existing history and backups. Deletions are mirrored; git history
is the safety net. A tracked ``_MANIFEST.md`` records the file count and when
the copy last ran, which is how a dead hook becomes visible.

User-level memory (``~/.claude/CLAUDE.md`` and anything else outside
``projects/<encoded>/memory/``) is intentionally not copied. It applies to
every project on the machine; dumping it into one vault would mix global
personal context into a tree that can be shared or backed up with that vault.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Mapping

MIRROR_RELATIVE = "System/memory-mirror"
MANIFEST_NAME = "_MANIFEST.md"
ENTRYPOINT_NAME = "MEMORY.md"
USER_LEVEL_CLAUDE_MD = "CLAUDE.md"
DRY_RUN_ENV = "DEX_MEMORY_MIRROR_DRY_RUN"
STALE_DROP_FRACTION = 0.5
STALE_DROP_MIN_FILES = 5
DOCTOR_STALE_AFTER = timedelta(days=7)
MUTATION_LOCK_RELATIVE = "System/.dex/mutation.lock"

_NON_ALNUM = re.compile(r"[^A-Za-z0-9]")
_MANIFEST_AT = re.compile(r"^\s*(?:-\s+)?\*\*Mirrored at:\*\*\s*(.+?)\s*$", re.MULTILINE)
_MANIFEST_COUNT = re.compile(r"^\s*(?:-\s+)?\*\*File count:\*\*\s*(\d+)\s*$", re.MULTILINE)

STATUS_FOUND = "found"
STATUS_MISSING = "missing"
STATUS_EMPTY_ENCODED = "empty_encoded"
STATUS_AMBIGUOUS = "ambiguous"

ACTION_MIRRORED = "mirrored"
ACTION_NOOP = "noop"
ACTION_DRY_RUN = "dry_run"
ACTION_REFUSED = "refused"
ACTION_SKIPPED = "skipped"


@dataclass(frozen=True)
class SourceResolution:
    """Where this vault's Claude project memory lives, or why it does not."""

    status: str
    path: Path | None
    detail: str
    method: str = "none"
    candidates: tuple[Path, ...] = ()


@dataclass(frozen=True)
class Manifest:
    """Parsed ``_MANIFEST.md`` from a previous successful copy."""

    mirrored_at: datetime
    file_count: int


@dataclass(frozen=True)
class MirrorOutcome:
    """Result of one mirror attempt. Never includes file contents."""

    action: str
    detail: str
    copied: tuple[str, ...] = ()
    removed: tuple[str, ...] = ()
    unchanged: int = 0
    file_count: int = 0
    wrote: bool = False
    source_method: str = "none"


@dataclass(frozen=True)
class InspectOutcome:
    """Read-only doctor view of the live source and the vault copy."""

    verdict: str
    detail: str
    heal_action: str | None = None


def claude_config_home(home: Path, env: Mapping[str, str] | None = None) -> Path:
    """Return Claude's config home, honouring ``CLAUDE_CONFIG_DIR`` when set."""

    environ = env if env is not None else {}
    override = (environ.get("CLAUDE_CONFIG_DIR") or "").strip()
    if override:
        return Path(override)
    return Path(home) / ".claude"


def encode_separators(project_root: Path) -> str:
    """Encode the way Claude historically did: ``/`` and ``\\`` become ``-``."""

    text = str(project_root)
    return text.replace("\\", "/").replace("/", "-")


def encode_non_alnum(project_root: Path) -> str:
    """Encode by replacing every non-alphanumeric character with ``-``.

    Claude Code has changed this scheme between versions. Both encodings are
    tried; if neither finds ``MEMORY.md``, the copy refuses rather than
    mirroring an empty folder.
    """

    return _NON_ALNUM.sub("-", str(project_root))


def encoding_candidates(project_root: Path) -> tuple[str, ...]:
    """Return unique encoded directory names for this vault path."""

    names: list[str] = []
    for encoded in (encode_separators(project_root), encode_non_alnum(project_root)):
        if encoded and encoded not in names:
            names.append(encoded)
    return tuple(names)


def _git_toplevel(vault_root: Path) -> Path | None:
    if not (vault_root / ".git").exists():
        return None
    try:
        result = subprocess.run(
            ["git", "-C", str(vault_root), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    text = result.stdout.strip()
    return Path(text) if text else None


def project_roots_for_encoding(vault_root: Path) -> tuple[Path, ...]:
    """Vault paths Claude might have encoded for this project."""

    roots: list[Path] = []
    for candidate in (vault_root, vault_root.resolve(), _git_toplevel(vault_root)):
        if candidate is None:
            continue
        if candidate not in roots:
            roots.append(candidate)
    return tuple(roots)


def _posix_relative(path: Path) -> str | None:
    text = path.as_posix().replace("\\", "/")
    parts = text.split("/")
    if not text or text.startswith("/") or parts[0] in {".", ".."}:
        return None
    if any(part in {"", ".", ".."} for part in parts):
        return None
    return text


def _iter_regular_files(root: Path) -> dict[str, Path]:
    """Map vault-relative posix paths to regular files, never following links."""

    files: dict[str, Path] = {}
    if not root.is_dir() or root.is_symlink():
        return files
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        current = Path(dirpath)
        if current.is_symlink():
            dirnames[:] = []
            continue
        dirnames[:] = sorted(
            name for name in dirnames if not (current / name).is_symlink()
        )
        for name in filenames:
            if name == MANIFEST_NAME:
                continue
            candidate = current / name
            if candidate.is_symlink() or not candidate.is_file():
                continue
            relative = _posix_relative(candidate.relative_to(root))
            if relative is None:
                continue
            files[relative] = candidate
    return files


def resolve_source(
    vault_root: Path,
    home: Path,
    env: Mapping[str, str] | None = None,
) -> SourceResolution:
    """Find this vault's Claude project memory directory.

    Derived encodings are tried first. If those folders exist but have no
    ``MEMORY.md``, the copy fails loudly instead of mirroring empty. A fallback
    scan only accepts a ``projects/*/memory/MEMORY.md`` whose encoded name
    still matches this vault. User-level files outside ``projects/`` are never
    considered.
    """

    config_home = claude_config_home(home, env)
    projects_dir = config_home / "projects"
    encoded_names: list[str] = []
    for root in project_roots_for_encoding(vault_root):
        for name in encoding_candidates(root):
            if name not in encoded_names:
                encoded_names.append(name)

    if not encoded_names:
        return SourceResolution(
            STATUS_MISSING,
            None,
            "Dex could not derive a Claude project folder name for this vault.",
        )

    derived_hits: list[Path] = []
    derived_empty: list[Path] = []
    for name in encoded_names:
        memory_dir = projects_dir / name / "memory"
        entry = memory_dir / ENTRYPOINT_NAME
        if _is_regular_file(entry):
            if memory_dir not in derived_hits:
                derived_hits.append(memory_dir)
        elif memory_dir.is_dir() and not memory_dir.is_symlink():
            if memory_dir not in derived_empty:
                derived_empty.append(memory_dir)

    unique_hits = tuple(derived_hits)
    if len(unique_hits) == 1:
        return SourceResolution(
            STATUS_FOUND,
            unique_hits[0],
            "Located Claude project memory from the derived folder name.",
            method="derived",
            candidates=unique_hits,
        )
    if len(unique_hits) > 1:
        return SourceResolution(
            STATUS_AMBIGUOUS,
            None,
            "More than one derived Claude project memory folder matched this vault. "
            "Dex will not guess which one to copy.",
            candidates=unique_hits,
        )

    fallback = _fallback_matches(projects_dir, encoded_names)
    if len(fallback) == 1:
        return SourceResolution(
            STATUS_FOUND,
            fallback[0],
            "Located Claude project memory with a fallback scan after the derived "
            "folder name did not contain MEMORY.md.",
            method="fallback",
            candidates=fallback,
        )
    if len(fallback) > 1:
        return SourceResolution(
            STATUS_AMBIGUOUS,
            None,
            "More than one Claude project memory folder could belong to this vault. "
            "Dex will not guess which one to copy.",
            candidates=fallback,
        )
    if derived_empty:
        return SourceResolution(
            STATUS_EMPTY_ENCODED,
            None,
            "Dex found the encoded Claude project folder, but it has no MEMORY.md. "
            "Refusing to copy an empty folder in case the folder-name scheme changed.",
            candidates=tuple(derived_empty),
        )
    return SourceResolution(
        STATUS_MISSING,
        None,
        "Claude Code has no per-project memory folder for this vault on this machine.",
    )


def _is_regular_file(path: Path) -> bool:
    try:
        return path.is_file() and not path.is_symlink()
    except OSError:
        return False


def _normalized_encoded_name(name: str) -> str:
    return _NON_ALNUM.sub("-", name)


def _fallback_matches(projects_dir: Path, encoded_names: list[str]) -> tuple[Path, ...]:
    if not projects_dir.is_dir() or projects_dir.is_symlink():
        return ()
    wanted = {_normalized_encoded_name(name) for name in encoded_names}
    wanted.update(encoded_names)
    matches: list[Path] = []
    try:
        children = list(projects_dir.iterdir())
    except OSError:
        return ()
    for child in children:
        if child.is_symlink() or not child.is_dir():
            continue
        memory_dir = child / "memory"
        if not _is_regular_file(memory_dir / ENTRYPOINT_NAME):
            continue
        if child.name in encoded_names or _normalized_encoded_name(child.name) in wanted:
            matches.append(memory_dir)
    return tuple(matches)


def mirror_destination(vault_root: Path) -> Path:
    return vault_root / MIRROR_RELATIVE


def manifest_path(vault_root: Path) -> Path:
    return mirror_destination(vault_root) / MANIFEST_NAME


def parse_manifest(text: str) -> Manifest | None:
    at_match = _MANIFEST_AT.search(text)
    count_match = _MANIFEST_COUNT.search(text)
    if at_match is None or count_match is None:
        return None
    raw_at = at_match.group(1).strip()
    try:
        mirrored_at = datetime.fromisoformat(raw_at.replace("Z", "+00:00"))
    except ValueError:
        return None
    if mirrored_at.tzinfo is None:
        mirrored_at = mirrored_at.replace(tzinfo=timezone.utc)
    try:
        file_count = int(count_match.group(1))
    except ValueError:
        return None
    return Manifest(mirrored_at=mirrored_at, file_count=file_count)


def read_manifest(vault_root: Path) -> Manifest | None:
    path = manifest_path(vault_root)
    if not _is_regular_file(path):
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    return parse_manifest(text)


def should_refuse_drop(*, previous_count: int, source_count: int) -> bool:
    """Refuse a copy that looks like the live folder was accidentally wiped."""

    if previous_count < STALE_DROP_MIN_FILES:
        return False
    dropped = previous_count - source_count
    if dropped < STALE_DROP_MIN_FILES:
        return False
    return source_count < previous_count * STALE_DROP_FRACTION


def render_manifest(
    *,
    mirrored_at: datetime,
    file_count: int,
    copied: tuple[str, ...],
    removed: tuple[str, ...],
    unchanged: int,
    source_method: str,
) -> str:
    stamped = mirrored_at.astimezone(timezone.utc).isoformat()
    lines = [
        "# Claude project memory mirror",
        "",
        "Copy of this vault's Claude Code per-project memory. User-level memory",
        "outside this project is not included.",
        "",
        f"- **Mirrored at:** {stamped}",
        f"- **File count:** {file_count}",
        f"- **Copied:** {len(copied)}",
        f"- **Removed:** {len(removed)}",
        f"- **Unchanged:** {unchanged}",
        f"- **Source match:** {source_method}",
        "",
        "## Changed this run",
        "",
    ]
    if not copied and not removed:
        lines.append("- none")
    else:
        for name in copied:
            lines.append(f"- copied: `{name}`")
        for name in removed:
            lines.append(f"- removed: `{name}`")
    lines.append("")
    return "\n".join(lines)


def _mutation_lock_present(vault_root: Path) -> bool:
    lock = vault_root / MUTATION_LOCK_RELATIVE
    return lock.exists()


def _plan_changes(
    source_files: dict[str, Path],
    dest_files: dict[str, Path],
) -> tuple[list[str], list[str], int]:
    copied: list[str] = []
    for relative, source_path in sorted(source_files.items()):
        dest_path = dest_files.get(relative)
        if dest_path is None:
            copied.append(relative)
            continue
        try:
            if source_path.read_bytes() != dest_path.read_bytes():
                copied.append(relative)
        except OSError:
            copied.append(relative)
    removed = sorted(name for name in dest_files if name not in source_files)
    unchanged = len(source_files) - len(copied)
    return copied, removed, unchanged


def _apply_changes(
    destination: Path,
    source_files: dict[str, Path],
    copied: list[str],
    removed: list[str],
) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    for relative in copied:
        target = destination / relative
        if ".." in Path(relative).parts:
            raise ValueError(f"refusing to write escaped memory path: {relative}")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_files[relative], target, follow_symlinks=False)
    for relative in removed:
        target = destination / relative
        if target.is_symlink() or not target.is_file():
            continue
        target.unlink()
        parent = target.parent
        while parent != destination and parent.is_dir() and not any(parent.iterdir()):
            parent.rmdir()
            parent = parent.parent


def mirror(
    *,
    vault_root: Path,
    home: Path,
    now: datetime | None = None,
    dry_run: bool = False,
    env: Mapping[str, str] | None = None,
) -> MirrorOutcome:
    """Copy current per-project memory into the vault, or refuse honestly."""

    when = now or datetime.now(timezone.utc)
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    if _mutation_lock_present(vault_root):
        return MirrorOutcome(
            ACTION_SKIPPED,
            "Paused because a Dex update or migration is running.",
        )
    resolution = resolve_source(vault_root, home, env)
    if resolution.status == STATUS_MISSING:
        return MirrorOutcome(ACTION_SKIPPED, resolution.detail)
    if resolution.status != STATUS_FOUND or resolution.path is None:
        return MirrorOutcome(ACTION_REFUSED, resolution.detail)

    source_files = _iter_regular_files(resolution.path)
    destination = mirror_destination(vault_root)
    dest_files = _iter_regular_files(destination)
    previous = read_manifest(vault_root)
    previous_count = previous.file_count if previous is not None else len(dest_files)
    if should_refuse_drop(previous_count=previous_count, source_count=len(source_files)):
        return MirrorOutcome(
            ACTION_REFUSED,
            "Claude's live project memory shrank sharply compared with the vault copy. "
            "Dex left the vault copy alone so the earlier files remain the recovery path.",
            file_count=previous_count,
            source_method=resolution.method,
        )

    copied, removed, unchanged = _plan_changes(source_files, dest_files)
    file_count = len(source_files)
    if dry_run:
        return MirrorOutcome(
            ACTION_DRY_RUN,
            (
                f"Dry run: would copy {len(copied)}, remove {len(removed)}, "
                f"leave {unchanged} unchanged ({file_count} files)."
            ),
            copied=tuple(copied),
            removed=tuple(removed),
            unchanged=unchanged,
            file_count=file_count,
            source_method=resolution.method,
        )
    if not copied and not removed and previous is not None and file_count == previous.file_count:
        # Still refresh the timestamp so a tracked file shows the hook ran.
        pass
    _apply_changes(destination, source_files, copied, removed)
    manifest_path(vault_root).write_text(
        render_manifest(
            mirrored_at=when,
            file_count=file_count,
            copied=tuple(copied),
            removed=tuple(removed),
            unchanged=unchanged,
            source_method=resolution.method,
        ),
        encoding="utf-8",
    )
    action = ACTION_NOOP if not copied and not removed else ACTION_MIRRORED
    return MirrorOutcome(
        action,
        f"Copied Claude project memory into the vault ({file_count} files).",
        copied=tuple(copied),
        removed=tuple(removed),
        unchanged=unchanged,
        file_count=file_count,
        wrote=True,
        source_method=resolution.method,
    )


def inspect(
    *,
    vault_root: Path,
    home: Path,
    now: datetime | None = None,
    env: Mapping[str, str] | None = None,
) -> InspectOutcome:
    """Read-only health view: the hook is the backup, this is the alarm."""

    when = now or datetime.now(timezone.utc)
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    resolution = resolve_source(vault_root, home, env)
    destination = mirror_destination(vault_root)
    dest_files = _iter_regular_files(destination)
    manifest = read_manifest(vault_root)
    mirror_present = bool(dest_files) or manifest is not None

    if resolution.status == STATUS_EMPTY_ENCODED:
        return InspectOutcome(
            "BROKEN",
            resolution.detail,
            "Finish a Claude Code session after Dex can see MEMORY.md, or report this as a Dex bug.",
        )
    if resolution.status == STATUS_AMBIGUOUS:
        return InspectOutcome(
            "BROKEN",
            resolution.detail,
            "Report this as a Dex bug — the project-memory folder name is ambiguous.",
        )

    if resolution.status == STATUS_MISSING:
        if not mirror_present:
            return InspectOutcome(
                "OFF",
                "Claude Code has no per-project memory on this machine yet, so there is nothing to copy into the vault.",
            )
        return InspectOutcome(
            "OK",
            "A vault copy of Claude's project memory is present. The live folder was not found on this machine.",
        )

    source_files = _iter_regular_files(resolution.path) if resolution.path is not None else {}
    if not mirror_present:
        return InspectOutcome(
            "BROKEN",
            "Claude has project memory, but Dex has never copied it into the vault.",
            "Finish a Claude Code session so Dex can copy project memory into the vault.",
        )
    if manifest is None:
        return InspectOutcome(
            "BROKEN",
            "The vault copy of Claude's project memory is missing its dated record, so Dex cannot tell when it last ran.",
            "Finish a Claude Code session so Dex can rewrite the dated record.",
        )
    if should_refuse_drop(previous_count=len(dest_files) or manifest.file_count, source_count=len(source_files)):
        return InspectOutcome(
            "BROKEN",
            "Claude's live project memory is much smaller than the vault copy. Dex will not overwrite the copy.",
            "If the live notes were deleted by mistake, restore them from the vault copy.",
        )
    age = when - manifest.mirrored_at
    if age > DOCTOR_STALE_AFTER:
        days = max(age.days, 1)
        return InspectOutcome(
            "BROKEN",
            f"The vault copy of Claude's project memory is {days} days old. If you have been using Claude Code, the session-end copy may have stopped.",
            "Finish a Claude Code session so Dex can refresh the vault copy.",
        )
    return InspectOutcome(
        "OK",
        f"Claude's project memory was copied into the vault ({manifest.file_count} files).",
    )


def _dry_run_requested(args_dry_run: bool, env: Mapping[str, str]) -> bool:
    if args_dry_run:
        return True
    value = (env.get(DRY_RUN_ENV) or "").strip().lower()
    return value in {"1", "true", "yes"}


def main(argv: list[str] | None = None, env: Mapping[str, str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", help="Vault root. Defaults to CLAUDE_PROJECT_DIR or the current directory.")
    parser.add_argument("--home", help="Home directory used to find ~/.claude. Defaults to the process home.")
    parser.add_argument("--dry-run", action="store_true", help="Report intended changes and write nothing.")
    parser.add_argument("--now", help="ISO-8601 timestamp for tests.")
    args = parser.parse_args(argv)
    environ = dict(env if env is not None else os.environ)
    vault = Path(args.vault or environ.get("CLAUDE_PROJECT_DIR") or Path.cwd())
    home = Path(args.home or Path.home())
    now = None
    if args.now:
        now = datetime.fromisoformat(args.now.replace("Z", "+00:00"))
    dry_run = _dry_run_requested(args.dry_run, environ)
    outcome = mirror(vault_root=vault, home=home, now=now, dry_run=dry_run, env=environ)
    stream = sys.stdout if outcome.action in {ACTION_MIRRORED, ACTION_NOOP, ACTION_DRY_RUN, ACTION_SKIPPED} else sys.stderr
    print(outcome.detail, file=stream)
    if outcome.action == ACTION_DRY_RUN:
        for name in outcome.copied:
            print(f"would copy: {name}", file=stream)
        for name in outcome.removed:
            print(f"would remove: {name}", file=stream)
    if outcome.action == ACTION_REFUSED:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
