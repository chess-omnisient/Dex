"""B4 inventory contract, including E6 and folder-map canonicalization."""

from __future__ import annotations

from pathlib import Path

from core.lifecycle.catalog import HASH_TABLE_PATH
from core.lifecycle.customizations import load_release_baseline
from core.lifecycle.inventory import build_inventory, canonical_inventory_bytes
from core.tests.lifecycle_test_helpers import (
    catalog_for,
    write_file,
    write_manifest,
    write_release_hash_table,
)


def _by_path(report):
    return {entry.actual_path: entry for entry in report.entries}


def test_inventory_layers_contract_ownership_and_release_state_without_writes(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()
    shipped = b"release bytes\n"
    write_file(vault, "core/feature.py", shipped)
    write_file(vault, "04-Projects/Client/notes.md", b"private notes\n")
    write_file(vault, "mystery/place.txt", b"unknown\n")
    write_file(vault, ".env", b"API_KEY=never-read\n")
    manifest = write_manifest(
        vault,
        [
            "core/feature.py",
            "core/missing.py",
            "04-Projects/Client/notes.md",
            "mystery/place.txt",
            ".env",
        ],
    )
    catalog = catalog_for(manifest, {"core/feature.py": shipped, "core/missing.py": b"expected\n"})
    before = sorted((path.relative_to(vault).as_posix(), path.lstat().st_mtime_ns) for path in vault.rglob("*"))

    first = build_inventory(vault, catalog=catalog)
    second = build_inventory(vault, catalog=catalog)

    entries = _by_path(first)
    assert entries["core/feature.py"].ownership_class == "brain"
    assert entries["core/feature.py"].release_state == "stock-unmodified"
    assert entries["04-Projects/Client/notes.md"].ownership_class == "vault"
    assert entries["04-Projects/Client/notes.md"].release_state == "canonical-customization"
    assert entries["mystery/place.txt"].ownership_class is None
    assert {"mystery", "mystery/place.txt"}.issubset(first.unknown_paths)
    assert entries["core/missing.py"].kind == "missing"
    assert entries["core/missing.py"].release_state == "stock-missing"
    denied = entries[".env"].to_dict()
    assert denied["redacted"] is True
    assert "size" not in denied and "sha256" not in denied
    assert canonical_inventory_bytes(first) == canonical_inventory_bytes(second)
    after = sorted((path.relative_to(vault).as_posix(), path.lstat().st_mtime_ns) for path in vault.rglob("*"))
    assert after == before


def _hash_table_vault(tmp_path: Path):
    """One vault whose catalog items cover a single file; a second brain file
    is provable only through the sibling whole-tree hash table."""
    vault = tmp_path / "vault"
    vault.mkdir()
    shipped = b"release bytes\n"
    engine = b"engine release bytes\n"
    write_file(vault, "core/feature.py", shipped)
    write_file(vault, "core/engine.py", engine)
    binding = write_release_hash_table(vault, {"core/engine.py": engine})
    manifest = write_manifest(
        vault,
        ["core/feature.py", "core/engine.py", HASH_TABLE_PATH],
    )
    catalog = catalog_for(
        manifest,
        {"core/feature.py": shipped},
        hash_table=binding,
    )
    return vault, catalog, binding


def test_verified_hash_table_proves_files_the_catalog_items_do_not(tmp_path: Path) -> None:
    vault, catalog, binding = _hash_table_vault(tmp_path)

    # Without the binding, the table-only file is release-identity-unproved.
    sparse = build_inventory(vault, catalog=catalog_for(
        write_manifest(vault, ["core/feature.py", "core/engine.py", HASH_TABLE_PATH]),
        {"core/feature.py": b"release bytes\n"},
    ))
    assert _by_path(sparse)["core/engine.py"].release_state == "unknown"

    report = build_inventory(vault, catalog=catalog)
    entries = _by_path(report)

    assert report.baseline.identity_state == "VERIFIED"
    assert report.baseline.hash_table_state == "verified"
    assert entries["core/engine.py"].release_state == "stock-unmodified"
    assert entries["core/feature.py"].release_state == "stock-unmodified"
    # The table's own bytes are proved by the catalog binding row.
    assert entries[HASH_TABLE_PATH].release_state == "stock-unmodified"
    assert report.baseline.expected_sha256(HASH_TABLE_PATH) == binding[1]

    # A locally modified table-covered file is a divergence, never pristine.
    write_file(vault, "core/engine.py", b"locally changed\n")
    modified = _by_path(build_inventory(vault, catalog=catalog))
    assert modified["core/engine.py"].release_state == "stock-modified"


def test_tampered_hash_table_contributes_nothing_and_baseline_still_loads(
    tmp_path: Path,
) -> None:
    vault, catalog, _binding = _hash_table_vault(tmp_path)
    table = vault / HASH_TABLE_PATH
    table.write_bytes(table.read_bytes().replace(b"engine", b"attacker"))

    baseline = load_release_baseline(vault, catalog=catalog)
    report = build_inventory(vault, catalog=catalog)
    entries = _by_path(report)

    # Fail closed to LESS trust: identical to a catalog without the binding.
    assert baseline.identity_state == "VERIFIED"
    assert baseline.hash_table_state == "rejected"
    assert set(baseline.expected_hashes) == {"core/feature.py"}
    assert baseline.errors == ()
    assert entries["core/engine.py"].release_state == "unknown"
    assert entries["core/feature.py"].release_state == "stock-unmodified"


def test_missing_hash_table_with_binding_present_falls_back_fail_closed(
    tmp_path: Path,
) -> None:
    vault, catalog, _binding = _hash_table_vault(tmp_path)
    (vault / HASH_TABLE_PATH).unlink()

    baseline = load_release_baseline(vault, catalog=catalog)
    report = build_inventory(vault, catalog=catalog)
    entries = _by_path(report)

    assert baseline.identity_state == "VERIFIED"
    assert baseline.hash_table_state == "rejected"
    assert set(baseline.expected_hashes) == {"core/feature.py"}
    assert baseline.errors == ()
    assert entries["core/engine.py"].release_state == "unknown"
    # The absent table itself surfaces as a missing expectation nowhere: it
    # contributed nothing, so nothing expects it either.
    assert HASH_TABLE_PATH not in baseline.expected_hashes


def test_catalog_without_hash_table_binding_keeps_todays_behavior(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()
    shipped = b"release bytes\n"
    write_file(vault, "core/feature.py", shipped)
    write_file(vault, "core/engine.py", b"engine release bytes\n")
    manifest = write_manifest(vault, ["core/feature.py", "core/engine.py"])
    catalog = catalog_for(manifest, {"core/feature.py": shipped})

    assert catalog.release.hash_table is None
    assert "hash_table" not in catalog.to_dict()["release"]

    baseline = load_release_baseline(vault, catalog=catalog)
    entries = _by_path(build_inventory(vault, catalog=catalog))

    assert baseline.identity_state == "VERIFIED"
    assert baseline.hash_table_state == "absent"
    assert dict(baseline.expected_hashes) == {
        "core/feature.py": catalog.items[0].files[0].sha256
    }
    assert entries["core/feature.py"].release_state == "stock-unmodified"
    assert entries["core/engine.py"].release_state == "unknown"


def test_hash_table_rows_outside_the_manifest_reject_the_whole_table(
    tmp_path: Path,
) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()
    shipped = b"release bytes\n"
    write_file(vault, "core/feature.py", shipped)
    binding = write_release_hash_table(
        vault, {"core/not-in-manifest.py": b"planted row\n"}
    )
    manifest = write_manifest(vault, ["core/feature.py", HASH_TABLE_PATH])
    catalog = catalog_for(manifest, {"core/feature.py": shipped}, hash_table=binding)

    baseline = load_release_baseline(vault, catalog=catalog)

    assert baseline.identity_state == "VERIFIED"
    assert baseline.hash_table_state == "rejected"
    assert set(baseline.expected_hashes) == {"core/feature.py"}


def test_remapped_folder_is_canonicalized_before_contract_resolution(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()
    write_file(
        vault,
        "System/folder-paths.yaml",
        b'projects: "Work/Projects"\n',
    )
    write_file(vault, "Work/Projects/README.md", b"starter edited by user\n")
    write_file(vault, "Work/Projects/Client/notes.md", b"user content\n")
    write_manifest(vault, ["System/folder-paths.yaml"])

    report = build_inventory(vault)
    entries = _by_path(report)

    assert report.folder_map.state == "LOADED"
    assert entries["Work/Projects/README.md"].canonical_path == "04-Projects/README.md"
    assert entries["Work/Projects/README.md"].ownership_class == "seed"
    assert entries["Work/Projects/Client/notes.md"].canonical_path == "04-Projects/Client/notes.md"
    assert entries["Work/Projects/Client/notes.md"].ownership_class == "vault"
    assert "Work/Projects/Client/notes.md" not in report.unknown_paths
