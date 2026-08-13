#!/usr/bin/env python3
"""Generate the harness-neutral `.agents/skills/` adapters from `.claude/skills/`.

Canonical Dex skills live under `.claude/skills/`. `.agents/skills/` is not a
second source of truth: it is a generated Agent Skills surface so harnesses
that do not read `.claude/skills/` still get the named journeys (capability
Tier 2). Claude-only frontmatter (`hooks`, `context`, `model_routing`) is
stripped. User-authored `*-custom/` directories are never touched.

Default writes the adapters. `--check` fails when the committed tree drifted.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPO_ROOT / ".claude" / "skills"
DEST_ROOT = REPO_ROOT / ".agents" / "skills"
GENERATOR_PATH = "scripts/generate-agents-skills.py"

# Claude Code skill frontmatter that other Agent Skills harnesses do not run.
CLAUDE_ONLY_FRONTMATTER = frozenset({"hooks", "context", "model_routing"})

# Instruction and eval companions. Scripts stay at their canonical
# `.claude/skills/.../scripts/` paths so generated adapters do not fork them.
COPY_FILENAMES = frozenset({"AGENT_INSTRUCTIONS.md"})
COPY_DIR_NAMES = frozenset({"references", "evals"})
SKIP_DIR_NAMES = frozenset({"ooxml"})
SKIP_FILENAMES = frozenset({"LICENSE.txt", "README.md", "MIGRATION_SUMMARY.md"})

FRONTMATTER_KEY = re.compile(r"^([A-Za-z0-9_-]+):")
GENERATED_COMMENT = (
    "<!-- Generated from `{source}` by `{generator}`. Do not edit. -->\n"
)


def _is_custom_path(path: Path) -> bool:
    return any(part.endswith("-custom") for part in path.parts)


def discover_canonical_skills(source_root: Path = SOURCE_ROOT) -> list[Path]:
    """Return every shipped SKILL.md under `.claude/skills/`, including rooms."""
    skills: list[Path] = []
    for path in sorted(source_root.rglob("SKILL.md")):
        if _is_custom_path(path):
            continue
        skills.append(path)
    return skills


def strip_claude_only_frontmatter(frontmatter: str) -> str:
    """Drop Claude-only top-level YAML keys, including nested blocks."""
    lines = frontmatter.splitlines(keepends=True)
    kept: list[str] = []
    skipping = False
    for line in lines:
        if skipping:
            if line.strip() == "":
                continue
            if line[:1] in {" ", "\t"}:
                continue
            skipping = False
        match = FRONTMATTER_KEY.match(line)
        if match and match.group(1) in CLAUDE_ONLY_FRONTMATTER:
            skipping = True
            continue
        kept.append(line)
    text = "".join(kept)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip("\n") + ("\n" if text.strip() else "")


def transform_skill_markdown(
    source_text: str, *, source_relative: str
) -> tuple[str, str, str]:
    if not source_text.startswith("---\n"):
        raise ValueError(f"skill lacks frontmatter: {source_relative}")
    parts = source_text.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"skill has unterminated frontmatter: {source_relative}")
    _empty, frontmatter, body = parts
    stripped = strip_claude_only_frontmatter(frontmatter)
    comment = GENERATED_COMMENT.format(
        source=source_relative,
        generator=GENERATOR_PATH,
    )
    body = body.lstrip("\n")
    return stripped, comment, body


def _adapter_relative(skill_md: Path, source_root: Path = SOURCE_ROOT) -> Path:
    return skill_md.parent.relative_to(source_root)


def rewrite_this_skill_paths(text: str, rel_dir: Path) -> str:
    """Point this skill's own instruction files at the generated adapter."""
    posix = rel_dir.as_posix()
    canonical = f".claude/skills/{posix}/"
    adapter = f".agents/skills/{posix}/"
    return text.replace(canonical, adapter)


def companion_files(skill_dir: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(skill_dir.rglob("*")):
        if not path.is_file() or path.name == "SKILL.md":
            continue
        if path.name in SKIP_FILENAMES:
            continue
        if any(part in SKIP_DIR_NAMES for part in path.relative_to(skill_dir).parts):
            continue
        relative = path.relative_to(skill_dir)
        if path.name in COPY_FILENAMES:
            files.append(path)
            continue
        if relative.parts and relative.parts[0] in COPY_DIR_NAMES:
            files.append(path)
    return files


def expected_adapters(
    repo_root: Path = REPO_ROOT,
) -> dict[Path, str]:
    """Map destination paths (relative to repo root) to generated file text."""
    source_root = repo_root / ".claude" / "skills"
    dest_root = repo_root / ".agents" / "skills"
    expected: dict[Path, str] = {}
    for skill_md in discover_canonical_skills(source_root):
        rel_dir = _adapter_relative(skill_md, source_root)
        dest_skill = dest_root / rel_dir / "SKILL.md"
        source_relative = skill_md.relative_to(repo_root).as_posix()
        stripped, comment, body = transform_skill_markdown(
            skill_md.read_text(encoding="utf-8"),
            source_relative=source_relative,
        )
        body = rewrite_this_skill_paths(body.lstrip("\n"), rel_dir)
        expected[dest_skill.relative_to(repo_root)] = (
            f"---\n{stripped}---\n\n{comment}\n{body}"
        )
        for companion in companion_files(skill_md.parent):
            dest = dest_root / rel_dir / companion.relative_to(skill_md.parent)
            text = companion.read_text(encoding="utf-8")
            expected[dest.relative_to(repo_root)] = rewrite_this_skill_paths(
                text, rel_dir
            )
    return expected


def _existing_generated_files(dest_root: Path) -> set[Path]:
    existing: set[Path] = set()
    if not dest_root.is_dir():
        return existing
    for path in dest_root.rglob("*"):
        if not path.is_file() or _is_custom_path(path):
            continue
        existing.add(path)
    return existing


def write_adapters(repo_root: Path = REPO_ROOT) -> int:
    dest_root = repo_root / ".agents" / "skills"
    dest_root.mkdir(parents=True, exist_ok=True)
    expected = expected_adapters(repo_root)
    written = 0
    for relative, text in expected.items():
        dest = repo_root / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        current = dest.read_text(encoding="utf-8") if dest.is_file() else None
        if current != text:
            dest.write_text(text, encoding="utf-8")
            written += 1
    expected_paths = {repo_root / relative for relative in expected}
    removed = 0
    for stale in _existing_generated_files(dest_root):
        if stale not in expected_paths:
            stale.unlink()
            removed += 1
            parent = stale.parent
            while parent != dest_root and parent.is_dir() and not any(parent.iterdir()):
                parent.rmdir()
                parent = parent.parent
    print(
        f"Generated {len(expected)} adapter files under .agents/skills/ "
        f"({written} written, {removed} removed)."
    )
    return 0


def check_adapters(repo_root: Path = REPO_ROOT) -> int:
    dest_root = repo_root / ".agents" / "skills"
    expected = expected_adapters(repo_root)
    errors: list[str] = []
    for relative, text in expected.items():
        dest = repo_root / relative
        if not dest.is_file():
            errors.append(f"missing {relative.as_posix()}")
            continue
        current = dest.read_text(encoding="utf-8")
        if current != text:
            errors.append(f"drifted {relative.as_posix()}")
    expected_paths = {repo_root / relative for relative in expected}
    for extra in _existing_generated_files(dest_root):
        if extra not in expected_paths:
            errors.append(
                f"unexpected {extra.relative_to(repo_root).as_posix()}"
            )
    if errors:
        print("❌ .agents/skills adapters are stale or incomplete:", file=sys.stderr)
        for error in errors[:40]:
            print(f"  {error}", file=sys.stderr)
        if len(errors) > 40:
            print(f"  ... and {len(errors) - 40} more", file=sys.stderr)
        print(
            "Run python3 scripts/generate-agents-skills.py and commit.",
            file=sys.stderr,
        )
        return 1
    print(f".agents/skills adapters are current ({len(expected)} files).")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify committed adapters match canonical skills (CI drift gate)",
    )
    args = parser.parse_args()
    if args.check:
        return check_adapters()
    return write_adapters()


if __name__ == "__main__":
    raise SystemExit(main())
