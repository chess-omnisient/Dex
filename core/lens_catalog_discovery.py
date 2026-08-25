"""Repository-backed discovery for Dex Lens catalogue capabilities."""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path

SKILL_ID = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
CONTROL = re.compile(r"[\x00-\x1f\x7f]")


class LensDiscoveryError(RuntimeError):
    """A shipped capability cannot be discovered without ambiguity."""


@dataclass(frozen=True, slots=True)
class SkillCandidate:
    """One active, first-party skill discovered from a release tree."""

    capability_id: str
    name: str
    description: str
    source_path: str


def _frontmatter_scalar(raw_value: str, *, context: str) -> str:
    value = raw_value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        try:
            parsed = ast.literal_eval(value)
        except (SyntaxError, ValueError) as error:
            raise LensDiscoveryError(f"{context} is not a valid quoted scalar") from error
        if not isinstance(parsed, str):
            raise LensDiscoveryError(f"{context} must be text")
        value = parsed
    if not value:
        raise LensDiscoveryError(f"{context} must be non-empty")
    if CONTROL.search(value):
        raise LensDiscoveryError(f"{context} contains control characters")
    return value


def _skill_frontmatter(path: Path, *, skill_id: str) -> tuple[str, str]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise LensDiscoveryError(f"cannot read active skill {path}: {error}") from error
    if not text.startswith("---\n"):
        raise LensDiscoveryError(f"active skill {path} has no frontmatter")

    fields: dict[str, str] = {}
    for line in text.splitlines()[1:]:
        if line == "---":
            break
        if ":" not in line:
            continue
        key, raw_value = line.split(":", 1)
        if key in {"name", "description"}:
            if key in fields:
                raise LensDiscoveryError(f"active skill {path} repeats {key}")
            fields[key] = _frontmatter_scalar(raw_value, context=f"active skill {path} {key}")
    else:
        raise LensDiscoveryError(f"active skill {path} has unclosed frontmatter")

    if "name" not in fields:
        raise LensDiscoveryError(f"active skill {path} has no name")
    if "description" not in fields:
        raise LensDiscoveryError(f"active skill {path} has no description")
    if fields["name"] != skill_id:
        raise LensDiscoveryError(
            f"active skill {path} name {fields['name']!r} does not match its directory {skill_id!r}"
        )
    return fields["name"], fields["description"]


def discover_active_skills(release_root: Path) -> tuple[SkillCandidate, ...]:
    """Discover direct, active, first-party skill payloads in a release tree."""

    root = release_root.resolve(strict=True)
    skills_root = root / ".claude" / "skills"
    if skills_root.is_symlink() or not skills_root.is_dir():
        raise LensDiscoveryError(f"active skills directory is missing or unsafe: {skills_root}")

    candidates: list[SkillCandidate] = []
    for directory in sorted(skills_root.iterdir(), key=lambda path: path.name):
        skill_id = directory.name
        if skill_id == "_available" or skill_id.startswith("anthropic-"):
            continue
        if directory.is_symlink() or not directory.is_dir():
            continue
        if SKILL_ID.fullmatch(skill_id) is None:
            raise LensDiscoveryError(f"active skill directory is not kebab-case: {skill_id!r}")

        payload = directory / "SKILL.md"
        if payload.is_symlink():
            raise LensDiscoveryError(f"active skill payload is missing or not a regular file: {payload}")
        if not payload.exists():
            continue
        if not payload.is_file():
            raise LensDiscoveryError(f"active skill payload is missing or not a regular file: {payload}")
        name, description = _skill_frontmatter(payload, skill_id=skill_id)
        candidates.append(
            SkillCandidate(
                capability_id=skill_id,
                name=name,
                description=description,
                source_path=f".claude/skills/{skill_id}/SKILL.md",
            )
        )
    return tuple(candidates)
