"""Tests for the historic-release acceptance fleet builder."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts import release_fleet


def _git(repo: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *arguments],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _repository(tmp_path: Path) -> Path:
    repo = tmp_path / "releases"
    _git(tmp_path, "init", "--quiet", str(repo))
    _git(repo, "config", "user.name", "Dex Fleet Tests")
    _git(repo, "config", "user.email", "fleet-tests@example.com")
    return repo


def _tag_release(
    repo: Path,
    version: str,
    content: str,
    *,
    allow_empty: bool = False,
    suffix: str | None = None,
) -> str:
    (repo / "README.md").write_text(content + "\n", encoding="utf-8")
    _git(repo, "add", "README.md")
    commit_args = ["commit", "--quiet", "-m", f"release {version}"]
    if allow_empty:
        commit_args.insert(1, "--allow-empty")
    _git(repo, *commit_args)
    commit = _git(repo, "rev-parse", "HEAD")
    tag = f"dist/release/v{version}-{suffix or commit[:7]}"
    _git(repo, "tag", "-a", tag, "-m", tag)
    return tag


def _tag_legacy_release(repo: Path, version: str, content: str) -> str:
    (repo / "README.md").write_text(content + "\n", encoding="utf-8")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "--quiet", "-m", f"legacy release {version}")
    tag = f"v{version}"
    _git(repo, "tag", "-a", tag, "-m", tag)
    return tag


def test_discovers_each_distinct_distribution_tree_once(tmp_path: Path) -> None:
    repo = _repository(tmp_path)
    first = _tag_release(repo, "1.61.0", "one")
    second = _tag_release(repo, "1.61.0", "two")
    _tag_release(repo, "1.62.0", "two", allow_empty=True)

    releases = release_fleet.discover_distribution_releases(repo)

    assert [release.tag for release in releases] == sorted([first, second])


def test_rejects_distribution_tag_that_does_not_name_its_commit(tmp_path: Path) -> None:
    repo = _repository(tmp_path)
    _tag_release(repo, "1.61.0", "actual", suffix="deadbee")

    with pytest.raises(release_fleet.FleetError, match="does not match"):
        release_fleet.discover_distribution_releases(repo)


def test_discovers_legacy_published_release_trees_too(tmp_path: Path) -> None:
    repo = _repository(tmp_path)
    legacy = _tag_legacy_release(repo, "1.20.1", "legacy")
    distribution = _tag_release(repo, "1.61.0", "distribution")

    releases = release_fleet.discover_distribution_releases(repo)

    assert [release.tag for release in releases] == [legacy, distribution]


def test_build_fixture_uses_requested_release_and_preserves_user_hashes(tmp_path: Path) -> None:
    repo = _repository(tmp_path)
    _tag_release(repo, "1.61.0", "one")
    release = release_fleet.discover_distribution_releases(repo)[0]

    case = release_fleet.build_fixture(repo, release, tmp_path / "fleet")

    assert _git(case.vault, "rev-parse", "HEAD^") == release.commit
    assert _git(case.vault, "remote", "get-url", "upstream") == release_fleet.PUBLIC_REMOTE
    assert _git(case.vault, "remote", "get-url", "--push", "upstream") == "DISABLED"
    assert case.user_hashes == release_fleet.hash_user_owned_files(case.vault)


def test_build_fixture_does_not_preload_future_release_tags(tmp_path: Path) -> None:
    repo = _repository(tmp_path)
    first = _tag_release(repo, "1.61.0", "one")
    future = _tag_release(repo, "1.62.0", "two")
    release = next(
        candidate
        for candidate in release_fleet.discover_distribution_releases(repo)
        if candidate.tag == first
    )

    case = release_fleet.build_fixture(repo, release, tmp_path / "fleet")

    assert _git(case.vault, "tag", "--list", future) == ""


def test_build_fixture_refuses_to_overwrite_an_existing_case(tmp_path: Path) -> None:
    repo = _repository(tmp_path)
    _tag_release(repo, "1.61.0", "one")
    release = release_fleet.discover_distribution_releases(repo)[0]
    output = tmp_path / "fleet"
    case = output / release_fleet.safe_case_name(release)
    case.mkdir(parents=True)
    (case / "keep-me").write_text("do not delete", encoding="utf-8")

    with pytest.raises(release_fleet.FleetError, match="case directory"):
        release_fleet.build_fixture(repo, release, output)


def test_acceptance_report_requires_both_hops_and_unchanged_user_hashes() -> None:
    hashes = {"00-Inbox/keep.md": "a" * 64}
    report = release_fleet.AcceptanceReport(
        foundation_tag="dist/release/v1.80.0-aaaaaaa",
        follow_up_tag="dist/release/v1.80.1-bbbbbbb",
        cases=(
            release_fleet.CaseResult(
                starting_tag="dist/release/v1.61.0-ccccccc",
                reached_foundation=True,
                reached_follow_up=True,
                foundation_doctor_healthy=True,
                follow_up_doctor_healthy=True,
                user_hashes_before=hashes,
                user_hashes_after_foundation=hashes,
                user_hashes_after_follow_up=hashes,
                transcript_path="journeys/v1.61.0.md",
            ),
            release_fleet.CaseResult(
                starting_tag="dist/release/v1.62.0-ddddddd",
                reached_foundation=True,
                reached_follow_up=False,
                foundation_doctor_healthy=True,
                follow_up_doctor_healthy=True,
                user_hashes_before=hashes,
                user_hashes_after_foundation=hashes,
                user_hashes_after_follow_up=hashes,
                transcript_path="journeys/v1.62.0.md",
            ),
        ),
    )

    with pytest.raises(release_fleet.FleetError, match="follow-up"):
        release_fleet.assert_complete(
            report,
            {
                "dist/release/v1.61.0-ccccccc",
                "dist/release/v1.62.0-ddddddd",
            },
        )


def test_acceptance_report_refuses_when_any_published_start_is_missing() -> None:
    hashes = {"00-Inbox/keep.md": "a" * 64}
    report = release_fleet.AcceptanceReport(
        foundation_tag="dist/release/v1.80.0-aaaaaaa",
        follow_up_tag="dist/release/v1.80.1-bbbbbbb",
        cases=(
            release_fleet.CaseResult(
                starting_tag="dist/release/v1.61.0-ccccccc",
                reached_foundation=True,
                reached_follow_up=True,
                foundation_doctor_healthy=True,
                follow_up_doctor_healthy=True,
                user_hashes_before=hashes,
                user_hashes_after_foundation=hashes,
                user_hashes_after_follow_up=hashes,
                transcript_path="journeys/v1.61.0.md",
            ),
        ),
    )

    with pytest.raises(release_fleet.FleetError, match="missing"):
        release_fleet.assert_complete(
            report,
            {
                "dist/release/v1.61.0-ccccccc",
                "dist/release/v1.62.0-ddddddd",
            },
        )


def test_build_command_outputs_every_distinct_historic_release(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = _repository(tmp_path)
    _tag_release(repo, "1.61.0", "one")
    _tag_release(repo, "1.62.0", "two")

    exit_code = release_fleet.main(
        ["build", "--repo", str(repo), "--output", str(tmp_path / "fleet")]
    )

    manifest = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert manifest["case_count"] == 2
    assert [case["starting"]["tag"] for case in manifest["cases"]] == [
        release.tag for release in release_fleet.discover_distribution_releases(repo)
    ]


def test_manifest_command_lists_every_release_without_building_fixtures(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = _repository(tmp_path)
    _tag_release(repo, "1.61.0", "one")
    _tag_release(repo, "1.62.0", "two")
    output = tmp_path / "fleet"

    exit_code = release_fleet.main(["manifest", "--repo", str(repo)])

    manifest = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert manifest["case_count"] == 2
    assert not output.exists()


def test_manifest_cli_runs_from_the_documented_repository_root(tmp_path: Path) -> None:
    repo = _repository(tmp_path)
    _tag_release(repo, "1.61.0", "one")

    result = subprocess.run(
        [sys.executable, release_fleet.__file__, "manifest", "--repo", str(repo)],
        cwd=release_fleet.Path(__file__).resolve().parents[2],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["case_count"] == 1


def test_build_command_can_construct_one_historic_release_at_a_time(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = _repository(tmp_path)
    first = _tag_release(repo, "1.61.0", "one")
    _tag_release(repo, "1.62.0", "two")

    exit_code = release_fleet.main(
        [
            "build",
            "--repo",
            str(repo),
            "--output",
            str(tmp_path / "fleet"),
            "--starting-tag",
            first,
        ]
    )

    manifest = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert manifest["case_count"] == 1
    assert manifest["cases"][0]["starting"]["tag"] == first


def test_check_report_command_requires_all_discovered_starting_releases(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = _repository(tmp_path)
    start_tag = _tag_release(repo, "1.61.0", "one")
    hashes = {"00-Inbox/keep.md": "a" * 64}
    report = {
        "foundation_tag": "dist/release/v1.80.0-aaaaaaa",
        "follow_up_tag": "dist/release/v1.80.1-bbbbbbb",
        "cases": [
            {
                "starting_tag": start_tag,
                "reached_foundation": True,
                "reached_follow_up": True,
                "foundation_doctor_healthy": True,
                "follow_up_doctor_healthy": True,
                "user_hashes_before": hashes,
                "user_hashes_after_foundation": hashes,
                "user_hashes_after_follow_up": hashes,
                "transcript_path": "journeys/v1.61.0.md",
            }
        ],
    }
    report_path = tmp_path / "report.json"
    report_path.write_text(json.dumps(report), encoding="utf-8")

    exit_code = release_fleet.main(
        ["check-report", "--repo", str(repo), str(report_path)]
    )

    assert exit_code == 0
    assert "PASS: 1 historic release trees reached both releases" in capsys.readouterr().out
