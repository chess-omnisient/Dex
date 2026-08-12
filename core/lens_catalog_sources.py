"""Release-owned source authority for active and adoptable Lens skill entries.

The Lens registry names a source kind, but it does not duplicate lifecycle or
capability-room payload identity. This module resolves every reference through the
publisher-owned authority and returns one verified source/target pin. Catalogue
generation and room surfacing share this boundary so they cannot disagree about
which bytes are trusted.
"""

from __future__ import annotations

import hashlib
import json
import posixpath
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

DEFAULT_LIFECYCLE_CATALOG = Path("core/lifecycle/catalog/official-capabilities.json")
DEFAULT_PORTABLE_CONTRACT = Path("packages/dex-contracts/dist/portable-vault.contract.json")
HEX_SHA256 = re.compile(r"^[0-9a-f]{64}$")


class SkillSourceError(ValueError):
    """A skill reference cannot be resolved to release-owned bytes."""


@dataclass(frozen=True)
class SkillSourcePin:
    """One verified dormant-or-active source and its canonical active target."""

    kind: str
    source_path: str
    target_path: str
    sha256: str
    byte_size: int
    path: Path


def _mapping(value: object, *, context: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping) or not all(isinstance(key, str) for key in value):
        raise SkillSourceError(f"{context} must be a JSON object")
    return value


def _exact_fields(value: Mapping[str, object], expected: set[str], *, context: str) -> None:
    missing = sorted(expected - set(value))
    unknown = sorted(set(value) - expected)
    if missing or unknown:
        details = []
        if missing:
            details.append("missing " + ", ".join(missing))
        if unknown:
            details.append("unknown " + ", ".join(unknown))
        raise SkillSourceError(f"{context} fields are not closed ({'; '.join(details)})")


def _strict_json(path: Path, *, context: str) -> object:
    def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise SkillSourceError(f"{context} repeats JSON field {key!r}")
            result[key] = value
        return result

    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=unique_object,
            parse_constant=lambda value: (_ for _ in ()).throw(
                SkillSourceError(f"{context} contains non-finite JSON number {value}")
            ),
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise SkillSourceError(f"cannot read {context}: {error}") from error


def _authority_path(release_root: Path, explicit: Path | str | None, default: Path) -> Path:
    candidate = Path(explicit) if explicit is not None else default
    return candidate if candidate.is_absolute() else release_root / candidate


def _relative_path(value: object, *, context: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise SkillSourceError(f"{context} is not a canonical release-relative path")
    normalized = posixpath.normpath(value)
    if (
        normalized != value
        or normalized in ("", ".", "..")
        or normalized.startswith("/")
        or normalized.startswith("../")
    ):
        raise SkillSourceError(f"{context} is not a canonical release-relative path")
    return value


def _digest(value: object, *, context: str) -> str:
    if not isinstance(value, str) or HEX_SHA256.fullmatch(value) is None:
        raise SkillSourceError(f"{context} must be a lowercase sha256 digest")
    return value


def _byte_size(value: object, *, context: str) -> int:
    if type(value) is not int or value < 0:
        raise SkillSourceError(f"{context} must be a non-negative integer")
    return value


def _release_file(release_root: Path, relative: str, *, context: str) -> Path:
    root = release_root.resolve()
    candidate = root / relative
    resolved = candidate.resolve(strict=False)
    if not resolved.is_relative_to(root):
        raise SkillSourceError(f"{context} escapes the release root: {relative}")

    cursor = root
    for part in Path(relative).parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise SkillSourceError(f"{context} contains a symlink: {relative}")
    if not candidate.is_file():
        raise SkillSourceError(f"{context} is missing or not a regular file: {relative}")
    return candidate


def _require_tracked(release_root: Path, relative: str, *, context: str) -> None:
    if not (release_root / ".git").exists():
        return
    try:
        result = subprocess.run(
            [
                "git",
                "-C",
                str(release_root),
                "ls-files",
                "--error-unmatch",
                relative,
            ],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as error:
        raise SkillSourceError(f"cannot prove {context} is tracked: {error}") from error
    if result.returncode != 0:
        raise SkillSourceError(f"{context} is not tracked by the release tree: {relative}")


def _verify_pin(
    *,
    kind: str,
    release_root: Path,
    source_path: str,
    target_path: str,
    sha256: str,
    byte_size: int,
    context: str,
    exact_room_directory: bool = False,
) -> SkillSourcePin:
    source = _release_file(release_root, source_path, context=context)
    _require_tracked(release_root, source_path, context=context)
    if exact_room_directory:
        entries = tuple(source.parent.iterdir())
        if len(entries) != 1 or entries[0].name != "SKILL.md" or entries[0] != source:
            raise SkillSourceError(f"{context} directory contains unpinned entries; only SKILL.md is allowed")
    payload = source.read_bytes()
    actual_sha = hashlib.sha256(payload).hexdigest()
    if actual_sha != sha256 or len(payload) != byte_size:
        raise SkillSourceError(
            f"{context} bytes do not match the authoritative sha256 or byte_size "
            f"(declared sha256={sha256} byte_size={byte_size}; "
            f"actual sha256={actual_sha} byte_size={len(payload)})"
        )
    return SkillSourcePin(
        kind=kind,
        source_path=source_path,
        target_path=target_path,
        sha256=actual_sha,
        byte_size=len(payload),
        path=source,
    )


def _active_skill(reference: Mapping[str, object], release_root: Path) -> SkillSourcePin:
    _exact_fields(
        reference,
        {"kind", "path", "sha256", "byte_size"},
        context="active-skill source",
    )
    path = _relative_path(reference.get("path"), context="active-skill path")
    if not path.startswith(".claude/skills/") or not path.endswith("/SKILL.md"):
        raise SkillSourceError("active-skill path must be a shipped skill SKILL.md")
    if "/_available/" in path:
        raise SkillSourceError("active-skill path must not be dormant")
    if path.startswith(".claude/skills/anthropic-"):
        raise SkillSourceError("active-skill path must not be a vendored skill")
    return _verify_pin(
        kind="active-skill",
        release_root=release_root,
        source_path=path,
        target_path=path,
        sha256=_digest(reference.get("sha256"), context="active-skill sha256"),
        byte_size=_byte_size(reference.get("byte_size"), context="active-skill byte_size"),
        context="active-skill source",
    )


def _lifecycle_items(path: Path) -> dict[str, Mapping[str, object]]:
    document = _mapping(
        _strict_json(path, context="official lifecycle catalogue"),
        context="official lifecycle catalogue",
    )
    _exact_fields(
        document,
        {"catalog_source_version", "items"},
        context="official lifecycle catalogue",
    )
    if document.get("catalog_source_version") != 1:
        raise SkillSourceError("official lifecycle catalogue version is unsupported")
    raw_items = document.get("items")
    if not isinstance(raw_items, list):
        raise SkillSourceError("official lifecycle catalogue items must be an array")

    items: dict[str, Mapping[str, object]] = {}
    for index, raw_item in enumerate(raw_items):
        context = f"official lifecycle item {index}"
        item = _mapping(raw_item, context=context)
        _exact_fields(
            item,
            {"id", "kind", "version", "files", "dependencies", "capabilities"},
            context=context,
        )
        item_id = item.get("id")
        if not isinstance(item_id, str) or not item_id:
            raise SkillSourceError(f"{context} id must be non-empty text")
        if item_id in items:
            raise SkillSourceError(f"official lifecycle catalogue has duplicate item id {item_id!r}")
        items[item_id] = item
    return items


def _lifecycle_skill(
    reference: Mapping[str, object],
    release_root: Path,
    lifecycle_catalog_path: Path,
) -> SkillSourcePin:
    _exact_fields(
        reference,
        {"kind", "item_id"},
        context="lifecycle-skill source",
    )
    item_id = reference.get("item_id")
    if not isinstance(item_id, str) or not item_id:
        raise SkillSourceError("lifecycle-skill item_id must be non-empty text")
    item = _lifecycle_items(lifecycle_catalog_path).get(item_id)
    if item is None:
        raise SkillSourceError(f"lifecycle item {item_id!r} was not found")
    if item.get("kind") != "skill":
        raise SkillSourceError(f"lifecycle item {item_id!r} kind must be skill")
    files = item.get("files")
    if not isinstance(files, list) or len(files) != 1:
        raise SkillSourceError(f"lifecycle item {item_id!r} must contain exactly one file")
    declared = _mapping(files[0], context=f"lifecycle item {item_id!r} file")
    _exact_fields(
        declared,
        {"path", "source_path", "sha256", "byte_size"},
        context=f"lifecycle item {item_id!r} file",
    )
    target = _relative_path(declared.get("path"), context=f"lifecycle item {item_id!r} target")
    expected_target = f".claude/skills/{item_id}/SKILL.md"
    if target != expected_target:
        raise SkillSourceError(f"lifecycle item {item_id!r} target must be {expected_target}")
    source = _relative_path(
        declared.get("source_path"),
        context=f"lifecycle item {item_id!r} source",
    )
    if not source.startswith(".claude/skills/_available/") or not source.endswith("/SKILL.md"):
        raise SkillSourceError(f"lifecycle item {item_id!r} source must be a dormant skill SKILL.md")
    if Path(source).parent.name != item_id:
        raise SkillSourceError(
            f"lifecycle item {item_id!r} source identity must come from its {item_id} directory"
        )
    return _verify_pin(
        kind="lifecycle-skill",
        release_root=release_root,
        source_path=source,
        target_path=target,
        sha256=_digest(
            declared.get("sha256"),
            context=f"lifecycle item {item_id!r} sha256",
        ),
        byte_size=_byte_size(
            declared.get("byte_size"),
            context=f"lifecycle item {item_id!r} byte_size",
        ),
        context=f"lifecycle item {item_id!r} source",
    )


def _room_authorities(release_root: Path, portable_contract_path: Path) -> dict[tuple[str, str], Mapping[str, object]]:
    document = _mapping(
        _strict_json(portable_contract_path, context="portable vault contract"),
        context="portable vault contract",
    )
    rooms = document.get("capabilities")
    if not isinstance(rooms, Mapping):
        raise SkillSourceError("portable vault contract has no capability rooms")

    authorities: dict[tuple[str, str], Mapping[str, object]] = {}
    target_owners: dict[str, tuple[str, str]] = {}
    for room, raw_spec in rooms.items():
        if not isinstance(room, str) or not room:
            raise SkillSourceError("capability room id must be non-empty text")
        spec = _mapping(raw_spec, context=f"room {room!r}")
        raw_skills = spec.get("skills", [])
        if not isinstance(raw_skills, list) or not all(isinstance(skill, str) and skill for skill in raw_skills):
            raise SkillSourceError(f"room {room!r} skills must be an array of text")
        if len(raw_skills) != len(set(raw_skills)):
            raise SkillSourceError(f"room {room!r} skills contains duplicates")
        raw_pins = spec.get("skill_sources")
        if not isinstance(raw_pins, list):
            raise SkillSourceError(f"room {room!r} skill_sources must be an array")

        room_skills: set[str] = set()
        for index, raw_pin in enumerate(raw_pins):
            context = f"room {room!r} authority {index}"
            pin = _mapping(raw_pin, context=context)
            _exact_fields(
                pin,
                {
                    "room",
                    "skill",
                    "source_path",
                    "target_path",
                    "sha256",
                    "byte_size",
                },
                context=context,
            )
            skill = pin.get("skill")
            if pin.get("room") != room or not isinstance(skill, str) or not skill:
                raise SkillSourceError(f"room {room!r} authority must declare the same room and a skill")
            key = (room, skill)
            if key in authorities:
                raise SkillSourceError(f"room {room!r} authority duplicates skill {skill!r}")
            source = _relative_path(pin.get("source_path"), context=f"{context} source_path")
            target = _relative_path(pin.get("target_path"), context=f"{context} target_path")
            expected_source = f".claude/skills/_available/capabilities/{room}/skills/{skill}/SKILL.md"
            expected_target = f".claude/skills/{skill}/SKILL.md"
            if source != expected_source or target != expected_target:
                raise SkillSourceError(f"room {room!r} authority paths do not match skill {skill!r}")
            previous = target_owners.setdefault(target, key)
            if previous != key:
                raise SkillSourceError(f"room authorities duplicate active target {target!r}")
            _digest(pin.get("sha256"), context=f"{context} sha256")
            _byte_size(pin.get("byte_size"), context=f"{context} byte_size")
            authorities[key] = pin
            room_skills.add(skill)

        if room_skills != set(raw_skills):
            raise SkillSourceError(f"room {room!r} authority skill_sources must exactly match declared skills")
    return authorities


def resolve_room_skill_sources(
    room: str,
    release_root: Path | str,
    *,
    portable_contract_path: Path | str | None = None,
) -> tuple[SkillSourcePin, ...]:
    """Resolve and verify every skill pin belonging to one capability room."""
    root = Path(release_root).resolve()
    contract = _authority_path(root, portable_contract_path, DEFAULT_PORTABLE_CONTRACT)
    authorities = _room_authorities(root, contract)
    selected = [(skill, raw) for (authority_room, skill), raw in authorities.items() if authority_room == room]
    if not selected:
        document = _mapping(
            _strict_json(contract, context="portable vault contract"),
            context="portable vault contract",
        )
        capabilities = document.get("capabilities")
        if not isinstance(capabilities, Mapping) or room not in capabilities:
            raise SkillSourceError(f"room {room!r} was not found")
    result = []
    for skill, raw in sorted(selected):
        result.append(
            _verify_pin(
                kind="room-skill",
                release_root=root,
                source_path=str(raw["source_path"]),
                target_path=str(raw["target_path"]),
                sha256=str(raw["sha256"]),
                byte_size=int(raw["byte_size"]),
                context=f"room {room!r} skill {skill!r} source identity",
                exact_room_directory=True,
            )
        )
    return tuple(result)


def _room_skill(
    reference: Mapping[str, object],
    release_root: Path,
    portable_contract_path: Path,
) -> SkillSourcePin:
    _exact_fields(
        reference,
        {"kind", "room", "skill"},
        context="room-skill source",
    )
    room = reference.get("room")
    skill = reference.get("skill")
    if not isinstance(room, str) or not room or not isinstance(skill, str) or not skill:
        raise SkillSourceError("room-skill room and skill must be non-empty text")
    pins = resolve_room_skill_sources(
        room,
        release_root,
        portable_contract_path=portable_contract_path,
    )
    matches = [pin for pin in pins if pin.target_path == f".claude/skills/{skill}/SKILL.md"]
    if len(matches) != 1:
        raise SkillSourceError(f"room {room!r} skill authority for {skill!r} was not found exactly once")
    return matches[0]


def resolve_skill_source(
    reference: object,
    release_root: Path | str,
    *,
    lifecycle_catalog_path: Path | str | None = None,
    portable_contract_path: Path | str | None = None,
) -> SkillSourcePin:
    """Resolve a closed Lens source reference to release-owned, verified bytes."""
    root = Path(release_root).resolve()
    raw = _mapping(reference, context="skill source")
    kind = raw.get("kind")
    if kind == "active-skill":
        return _active_skill(raw, root)
    if kind == "lifecycle-skill":
        lifecycle = _authority_path(root, lifecycle_catalog_path, DEFAULT_LIFECYCLE_CATALOG)
        return _lifecycle_skill(raw, root, lifecycle)
    if kind == "room-skill":
        contract = _authority_path(root, portable_contract_path, DEFAULT_PORTABLE_CONTRACT)
        return _room_skill(raw, root, contract)
    raise SkillSourceError("skill source kind must be active-skill, lifecycle-skill, or room-skill")
