#!/usr/bin/env python3
"""Generate the canonical release-owned updater journey root contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

# Release generation must not add ignored bytecode beside the selected source.
sys.dont_write_bytecode = True

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.update.journey_protocol import (
    BRIDGE_ADAPTER,
    BRIDGE_SOURCE,
    CONTROLLER,
    EXECUTOR_SOURCE,
    FOLLOW_UP_ADAPTER,
    FOLLOW_UP_OPERATIONS,
    PROTOCOL_RELATIVE,
    PROTOCOL_VERSION,
    REQUIRED_EVIDENCE,
    RUNNER_SOURCE,
    SUPPORTED_PLATFORMS,
    load_update_journey_protocol,
)
from scripts.dex_update_bridge import FOUNDATION


def _sha256(relative: str) -> str:
    return hashlib.sha256((REPO_ROOT / relative).read_bytes()).hexdigest()


def protocol_document() -> dict[str, object]:
    """Build protocol v1 only from reviewed source constants and exact bytes."""

    return {
        "schema_version": PROTOCOL_VERSION,
        "controller": CONTROLLER,
        "platforms": list(SUPPORTED_PLATFORMS),
        "runner": {
            "source_path": RUNNER_SOURCE,
            "sha256": _sha256(RUNNER_SOURCE),
        },
        "executor": {
            "source_path": EXECUTOR_SOURCE,
            "sha256": _sha256(EXECUTOR_SOURCE),
        },
        "historic_to_foundation": {
            "adapter": BRIDGE_ADAPTER,
            "artifact": {
                "source_path": BRIDGE_SOURCE,
                "sha256": _sha256(BRIDGE_SOURCE),
            },
            "foundation": FOUNDATION.identity(),
            "approval": {"word": "APPLY", "count": 2},
        },
        "foundation_to_follow_up": {
            "adapter": FOLLOW_UP_ADAPTER,
            "operations": list(FOLLOW_UP_OPERATIONS),
            "approval": {"word": "APPLY", "count": 1},
        },
        "evidence": list(REQUIRED_EVIDENCE),
    }


def canonical_protocol_bytes() -> bytes:
    """Render and self-validate the generated contract."""

    content = (
        json.dumps(
            protocol_document(),
            ensure_ascii=False,
            allow_nan=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")
    load_update_journey_protocol(content)
    return content


def _atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as file:
            file.write(content)
            file.flush()
            os.fsync(file.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=REPO_ROOT / PROTOCOL_RELATIVE)
    args = parser.parse_args(argv)
    destination = args.output if args.output.is_absolute() else REPO_ROOT / args.output
    _atomic_write(destination, canonical_protocol_bytes())
    print(f"Wrote {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
