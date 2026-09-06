#!/usr/bin/env python3
"""Fail closed unless every release-catalog file is present, owned, and hash-bound."""

from __future__ import annotations

import argparse
import hashlib
import json
import posixpath
import re
import sys
from pathlib import Path

# Coverage is a read-only release gate. Importing B1 from the release tree must
# not mutate that tree with __pycache__ files.
sys.dont_write_bytecode = True

CATALOG_PATH = Path("System/.release-catalog.json")
SHIPPABLE_OWNERSHIP = frozenset({"brain", "seed", "generated"})
CATALOG_SOURCE_DIR = Path("core/lifecycle/catalog")


class CatalogCoverageError(RuntimeError):
    """The release tree does not fully cover its catalog."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _payload_sources(release_root: Path) -> dict[str, tuple[str, str, int]]:
    sources: dict[str, tuple[str, str, int]] = {}
    for source_path in sorted((release_root / CATALOG_SOURCE_DIR).glob("*.json")):
        if source_path.name in ("bridge-release.json", "release-hashes.json"):
            continue
        raw = json.loads(source_path.read_text(encoding="utf-8"))
        if raw.get("catalog_source_version") != 1 or not isinstance(raw.get("items"), list):
            raise CatalogCoverageError(f"invalid catalog source registry: {source_path}")
        for item in raw["items"]:
            for declared_file in item.get("files", []):
                target = declared_file.get("path")
                source = declared_file.get("source_path", target)
                declared_hash = declared_file.get("sha256")
                declared_size = declared_file.get("byte_size")
                if not isinstance(target, str) or not isinstance(source, str):
                    raise CatalogCoverageError(
                        f"catalog source file mapping is incomplete: {source_path}"
                    )
                if any(
                    not value
                    or "\\" in value
                    or value.startswith("/")
                    or posixpath.normpath(value) != value
                    or value.startswith("../")
                    for value in (target, source)
                ):
                    raise CatalogCoverageError(
                        f"catalog source file mapping is unsafe: {source_path}"
                    )
                if not isinstance(declared_hash, str) or re.fullmatch(
                    r"[0-9a-f]{64}", declared_hash
                ) is None:
                    raise CatalogCoverageError(
                        f"catalog source payload hash is invalid: {source_path}"
                    )
                if type(declared_size) is not int or declared_size < 0:
                    raise CatalogCoverageError(
                        f"catalog source payload size is invalid: {source_path}"
                    )
                mapping = (source, declared_hash, declared_size)
                previous = sources.setdefault(target, mapping)
                if previous != mapping:
                    raise CatalogCoverageError(
                        f"catalog target has multiple payload sources: {target}"
                    )
    return sources


def check_coverage(
    release_root: Path,
    *,
    catalog_path: Path = CATALOG_PATH,
    contract_root: Path | None = None,
) -> int:
    release_root = release_root.resolve()
    contract_root = (contract_root or release_root).resolve()
    sys.path.insert(0, str(contract_root))
    try:
        from core import portable_contract
        from core.lifecycle.catalog import (
            canonical_catalog_bytes,
            load_catalog,
            parse_release_hash_table,
        )

        absolute_catalog = release_root / catalog_path
        catalog = load_catalog(absolute_catalog, release_root=release_root)
        if absolute_catalog.read_bytes() != canonical_catalog_bytes(catalog):
            raise CatalogCoverageError("release catalog bytes are not canonical")

        manifest_path = release_root / catalog.release.manifest.path
        manifest_paths = manifest_path.read_text(encoding="utf-8").splitlines()
        if manifest_paths != sorted(set(manifest_paths)):
            raise CatalogCoverageError("installed-files manifest is not canonical")
        manifest_members = set(manifest_paths)
        payload_sources = _payload_sources(release_root)

        checked = 0
        for item in catalog.items:
            for catalog_file in item.files:
                payload_mapping = payload_sources.get(catalog_file.path)
                if payload_mapping is None:
                    raise CatalogCoverageError(
                        f"catalog file has no declared payload source: {catalog_file.path}"
                    )
                source_relative, declared_hash, declared_size = payload_mapping
                candidate = release_root / source_relative
                resolved = candidate.resolve(strict=False)
                if not resolved.is_relative_to(release_root):
                    raise CatalogCoverageError(
                        f"catalog payload escapes the release root: {source_relative}"
                    )
                if candidate.is_symlink() or not candidate.is_file():
                    raise CatalogCoverageError(
                        f"missing catalog file payload: {source_relative} "
                        f"(target {catalog_file.path})"
                    )
                if source_relative not in manifest_members:
                    raise CatalogCoverageError(
                        f"catalog payload is absent from the installed manifest: {source_relative}"
                    )
                try:
                    ownership = portable_contract.resolve(catalog_file.path)
                except portable_contract.ContractViolation as error:
                    raise CatalogCoverageError(
                        f"catalog file has no ownership class: {catalog_file.path}"
                    ) from error
                if ownership.denied or ownership.ownership not in SHIPPABLE_OWNERSHIP:
                    raise CatalogCoverageError(
                        f"catalog file is not release-shippable: {catalog_file.path} "
                        f"({ownership.ownership})"
                    )
                if ownership.ownership != catalog_file.ownership_class:
                    raise CatalogCoverageError(
                        f"catalog ownership is stale for {catalog_file.path}: "
                        f"{catalog_file.ownership_class} != {ownership.ownership}"
                    )
                try:
                    source_ownership = portable_contract.resolve(source_relative)
                except portable_contract.ContractViolation as error:
                    raise CatalogCoverageError(
                        f"catalog payload has no ownership class: {source_relative}"
                    ) from error
                if (
                    source_ownership.denied
                    or source_ownership.ownership not in SHIPPABLE_OWNERSHIP
                ):
                    raise CatalogCoverageError(
                        f"catalog payload is not release-shippable: {source_relative} "
                        f"({source_ownership.ownership})"
                    )
                actual_hash = _sha256(candidate)
                if candidate.stat().st_size != declared_size:
                    raise CatalogCoverageError(
                        f"catalog payload size declaration is stale for {catalog_file.path}: "
                        f"{declared_size} != {candidate.stat().st_size}"
                    )
                if declared_hash != catalog_file.sha256:
                    raise CatalogCoverageError(
                        f"catalog payload hash declaration is stale for {catalog_file.path}: "
                        f"{declared_hash} != {catalog_file.sha256}"
                    )
                if actual_hash != catalog_file.sha256:
                    raise CatalogCoverageError(
                        f"catalog hash is stale for {catalog_file.path}: "
                        f"{catalog_file.sha256} != {actual_hash}"
                    )
                checked += 1

        # Tree -> catalog: every release-owned ("brain") manifest file must
        # carry a proven hash row — from a capability item or from the
        # catalog-bound sibling whole-tree hash table. A release build with
        # coverage gaps fails here.
        proven: dict[str, str] = {
            catalog_file.path: catalog_file.sha256
            for item in catalog.items
            for catalog_file in item.files
        }
        binding = catalog.release.hash_table
        if binding is None:
            if catalog.catalog_version >= 2:
                raise CatalogCoverageError(
                    "release catalog carries no whole-tree hash table binding"
                )
        else:
            table_candidate = release_root / binding.path
            table_resolved = table_candidate.resolve(strict=False)
            if not table_resolved.is_relative_to(release_root):
                raise CatalogCoverageError(
                    f"release hash table escapes the release root: {binding.path}"
                )
            if table_candidate.is_symlink() or not table_candidate.is_file():
                raise CatalogCoverageError(
                    f"missing release hash table: {binding.path}"
                )
            if binding.path not in manifest_members:
                raise CatalogCoverageError(
                    f"release hash table is absent from the installed manifest: {binding.path}"
                )
            table_bytes = table_candidate.read_bytes()
            if hashlib.sha256(table_bytes).hexdigest() != binding.sha256:
                raise CatalogCoverageError(
                    f"release hash table does not match its catalog binding: {binding.path}"
                )
            table_rows = parse_release_hash_table(
                table_bytes,
                binding=binding,
                release_version=catalog.release.version,
            )
            for row_path in sorted(table_rows):
                if row_path not in manifest_members:
                    raise CatalogCoverageError(
                        f"hash table row is absent from the installed manifest: {row_path}"
                    )
                row_candidate = release_root / row_path
                row_resolved = row_candidate.resolve(strict=False)
                if not row_resolved.is_relative_to(release_root):
                    raise CatalogCoverageError(
                        f"hash table row escapes the release root: {row_path}"
                    )
                if row_candidate.is_symlink() or not row_candidate.is_file():
                    raise CatalogCoverageError(
                        f"missing hash table file payload: {row_path}"
                    )
                if _sha256(row_candidate) != table_rows[row_path]:
                    raise CatalogCoverageError(
                        f"hash table row is stale for {row_path}"
                    )
                checked += 1
            proven.update(table_rows)
            proven[binding.path] = binding.sha256
        for manifest_path in sorted(manifest_members):
            try:
                manifest_ownership = portable_contract.resolve(manifest_path)
            except portable_contract.ContractViolation as error:
                raise CatalogCoverageError(
                    f"manifest file has no ownership class: {manifest_path}"
                ) from error
            if manifest_ownership.denied:
                raise CatalogCoverageError(
                    f"manifest file is denied by the ownership contract: {manifest_path}"
                )
            if manifest_ownership.ownership != "brain":
                continue
            if manifest_path not in proven:
                raise CatalogCoverageError(
                    f"release-owned file has no catalog hash row: {manifest_path}"
                )
        return checked
    except (OSError, UnicodeError, ValueError) as error:
        if isinstance(error, CatalogCoverageError):
            raise
        raise CatalogCoverageError(str(error)) from error
    finally:
        if sys.path and sys.path[0] == str(contract_root):
            sys.path.pop(0)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release-root", type=Path, default=Path.cwd())
    parser.add_argument("--contract-root", type=Path)
    parser.add_argument("--catalog", type=Path, default=CATALOG_PATH)
    args = parser.parse_args(argv)
    try:
        count = check_coverage(
            args.release_root,
            catalog_path=args.catalog,
            contract_root=args.contract_root,
        )
    except CatalogCoverageError as error:
        parser.exit(1, f"catalog coverage failed: {error}\n")
    print(f"Catalog coverage passed ({count} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
