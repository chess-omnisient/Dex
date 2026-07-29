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
    _git(repo, "add", "-A")
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


def _archive_release_tag(repo: Path, tag: str) -> str:
    commit = _git(repo, "rev-parse", f"{tag}^{{commit}}")
    version, short = tag.removeprefix("dist/release/v").split("-", maxsplit=1)
    archive_tag = f"dist/archive/v{version}-{short}"
    _git(repo, "tag", "-a", archive_tag, commit, "-m", archive_tag)
    return archive_tag


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


def test_discovers_archived_distribution_tree_when_the_canonical_tag_is_absent(
    tmp_path: Path,
) -> None:
    repo = _repository(tmp_path)
    tag = _tag_release(repo, "1.64.0", "historic release")
    archive_tag = _archive_release_tag(repo, tag)
    _git(repo, "tag", "-d", tag)

    releases = release_fleet.discover_distribution_releases(repo)

    assert [release.tag for release in releases] == [archive_tag]


def test_discovers_exact_v164_archived_starting_tree(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    tag = "dist/archive/v1.64.0-366c168"
    commit = "366c168af61c50ee7157976a9eb8a154ca0fd7f4"
    tree = "0bf7e30785d511e4b3774358f73ce569167f3f60"

    def fake_git(_repo: Path, *arguments: str) -> str:
        if arguments == ("tag", "--list"):
            return tag
        if arguments == ("rev-parse", f"{tag}^{{commit}}"):
            return commit
        if arguments == ("rev-parse", f"{tag}^{{tree}}"):
            return tree
        raise AssertionError(arguments)

    monkeypatch.setattr(release_fleet, "_git", fake_git)

    assert release_fleet.discover_distribution_releases(tmp_path) == (
        release_fleet.DistributionRelease(
            tag=tag,
            version="1.64.0",
            commit=commit,
            tree=tree,
        ),
    )


def test_prefers_canonical_tag_when_archive_tag_has_the_same_tree(tmp_path: Path) -> None:
    repo = _repository(tmp_path)
    tag = _tag_release(repo, "1.64.0", "historic release")
    _archive_release_tag(repo, tag)

    releases = release_fleet.discover_distribution_releases(repo)

    assert [release.tag for release in releases] == [tag]


def test_rejects_colliding_immutable_distribution_identities(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    canonical_tag = "dist/release/v1.64.0-366c168"
    archive_tag = "dist/archive/v1.64.0-366c168"
    commits = {
        canonical_tag: "366c168af61c50ee7157976a9eb8a154ca0fd7f4",
        archive_tag: "366c168dddddddddddddddddddddddddddddddddd",
    }
    trees = {
        canonical_tag: "0bf7e30785d511e4b3774358f73ce569167f3f60",
        archive_tag: "ad5c7be7f2075bc3de74d4d0b168bb29e72c2d4e",
    }

    def fake_git(_repo: Path, *arguments: str) -> str:
        if arguments == ("tag", "--list"):
            return "\n".join((canonical_tag, archive_tag))
        for suffix, values in (("^{commit}", commits), ("^{tree}", trees)):
            tag = arguments[1].removesuffix(suffix)
            if arguments == ("rev-parse", f"{tag}{suffix}"):
                return values[tag]
        raise AssertionError(arguments)

    monkeypatch.setattr(release_fleet, "_git", fake_git)

    with pytest.raises(release_fleet.FleetError, match="ambiguous immutable distribution identity"):
        release_fleet.discover_distribution_releases(tmp_path)


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


def test_installed_fixture_runs_the_historic_installer_before_seeding_user_content(
    tmp_path: Path,
) -> None:
    repo = _repository(tmp_path)
    installer = repo / "install.sh"
    installer.write_text(
        "#!/bin/sh\n"
        "test ! -e 00-Inbox/keep.md\n"
        "mkdir -p System\n"
        "printf installed > System/fixture-install-proof\n",
        encoding="utf-8",
    )
    installer.chmod(0o755)
    _tag_release(repo, "1.61.0", "one")
    release = release_fleet.discover_distribution_releases(repo)[0]

    case = release_fleet.build_installed_fixture(repo, release, tmp_path / "fleet")

    assert (case.vault / "System/fixture-install-proof").read_text(encoding="utf-8") == "installed"
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


def test_acceptance_report_requires_each_declared_platform_to_cover_each_release() -> None:
    hashes = {"00-Inbox/keep.md": "a" * 64}
    common = {
        "starting_tag": "dist/release/v1.61.0-ccccccc",
        "reached_foundation": True,
        "reached_follow_up": True,
        "foundation_doctor_healthy": True,
        "follow_up_doctor_healthy": True,
        "user_hashes_before": hashes,
        "user_hashes_after_foundation": hashes,
        "user_hashes_after_follow_up": hashes,
        "transcript_path": "journeys/v1.61.0.md",
    }
    report = release_fleet.AcceptanceReport(
        foundation_tag="dist/release/v1.80.0-aaaaaaa",
        follow_up_tag="dist/release/v1.80.1-bbbbbbb",
        cases=(
            release_fleet.CaseResult(**common, platform="darwin"),
            release_fleet.CaseResult(**common, platform="linux"),
        ),
        platforms=("darwin", "linux"),
    )

    release_fleet.assert_complete(report, {common["starting_tag"]})


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


def test_generated_starting_manifest_supplies_the_required_case_count(tmp_path: Path) -> None:
    repo = _repository(tmp_path)
    _tag_release(repo, "1.61.0", "one")
    _tag_release(repo, "1.62.0", "two")
    releases = release_fleet.discover_distribution_releases(repo)
    generated = release_fleet.starting_release_manifest(releases)

    assert generated["case_count"] == len(releases) == 2
    assert release_fleet.releases_from_starting_manifest(
        json.dumps(generated), current_releases=releases
    ) == releases
    generated["case_count"] = 165
    with pytest.raises(release_fleet.FleetError, match="case count"):
        release_fleet.releases_from_starting_manifest(json.dumps(generated), current_releases=releases)


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


def _write_update_surface(repo: Path) -> None:
    skill = repo / release_fleet.UPDATE_SKILL_RELATIVE
    skill.parent.mkdir(parents=True, exist_ok=True)
    skill.write_text(
        "core.lifecycle.service\npreview\napproval\nApply this exact update?\nreceipt\n"
        "deliver_latest_release\nbuild_and_preview_delivered_release\n"
        "execute_approved_delivered_release\n",
        encoding="utf-8",
    )
    rescue = repo / release_fleet.UPDATE_RESCUE_RELATIVE
    rescue.parent.mkdir(parents=True, exist_ok=True)
    rescue.write_text("# Published rescue\n", encoding="utf-8")


def _write_starting_manifest(root: Path, releases: tuple[release_fleet.DistributionRelease, ...]) -> Path:
    path = root / "historic-release-manifest.json"
    path.write_text(json.dumps(release_fleet.starting_release_manifest(releases)), encoding="utf-8")
    return path


def _write_complete_evidence(
    repo: Path,
    root: Path,
    *,
    start: release_fleet.DistributionRelease,
    foundation: release_fleet.ImmutableRelease,
    follow_up: release_fleet.ImmutableRelease,
) -> tuple[dict[str, object], str, str]:
    evidence = root / "case.evidence"
    evidence.mkdir()
    historic_surface = release_fleet.shipped_update_surface(repo, start)
    foundation_surface = release_fleet.shipped_update_surface(repo, foundation)
    (evidence / "historic-update-surface.json").write_text(json.dumps(historic_surface))
    (evidence / "foundation-update-surface.json").write_text(json.dumps(foundation_surface))
    (evidence / "foundation-receipt.json").write_text(
        json.dumps({"release": foundation.identity(), "receipt": {"transaction_id": "foundation"}})
    )
    (evidence / "follow-up-receipt.json").write_text(
        json.dumps({"release": follow_up.identity(), "receipt": {"transaction_id": "follow-up"}})
    )
    doctor = json.dumps({"checks": [{"id": "doctor", "verdict": "OK"}]})
    (evidence / "foundation-doctor.json").write_text(doctor)
    (evidence / "follow-up-doctor.json").write_text(doctor)
    (evidence / "smoke.json").write_text(json.dumps({"status": "OK", "platform": "darwin"}))
    events = [
        {
            "id": "historic-update-surface",
            "command": ["git", "show", f"{start.tag}:{release_fleet.UPDATE_SKILL_RELATIVE}"],
            "release": historic_surface["release"],
            "skill_sha256": historic_surface["skill_sha256"],
            "rescue_sha256": historic_surface["rescue_sha256"],
        },
        {"id": "historic-route-refusal", "command": ["/dex-update"], "release": historic_surface["release"]},
        {"id": "bridge-foundation", "command": ["fleet-journey", "bridge"], "release": foundation.identity()},
        {
            "id": "foundation-update-surface",
            "command": ["git", "show", f"{foundation.tag}:{release_fleet.UPDATE_SKILL_RELATIVE}"],
            "release": foundation.identity(),
            "skill_sha256": foundation_surface["skill_sha256"],
            "rescue_sha256": foundation_surface["rescue_sha256"],
        },
        {
            "id": "foundation-preview",
            "command": ["/dex-update", "preview"],
            "from_release": foundation.identity(),
            "target_release": follow_up.identity(),
        },
        {
            "id": "foundation-approval",
            "command": ["/dex-update", "approve"],
            "target_release": follow_up.identity(),
            "answer": "APPLY",
        },
        {"id": "foundation-receipt", "command": ["/dex-update", "receipt"], "release": follow_up.identity()},
        {"id": "follow-up-installed", "command": ["git", "rev-parse"], "release": follow_up.identity()},
        {"id": "follow-up-doctor", "command": ["/dex-doctor"]},
        {"id": "follow-up-smoke", "command": ["dex-smoke"], "platform": "darwin"},
    ]
    transcript = evidence / "journey.json"
    transcript.write_text(json.dumps({"events": events}))
    manifest_path, manifest_sha256 = release_fleet._write_evidence_manifest(
        evidence,
        start=historic_surface["release"],
        foundation=foundation,
        follow_up=follow_up,
        events=events,
        artifacts={
            "transcript": transcript,
            "historic_update_surface": evidence / "historic-update-surface.json",
            "foundation_update_surface": evidence / "foundation-update-surface.json",
            "foundation_receipt": evidence / "foundation-receipt.json",
            "follow_up_receipt": evidence / "follow-up-receipt.json",
            "foundation_doctor": evidence / "foundation-doctor.json",
            "follow_up_doctor": evidence / "follow-up-doctor.json",
            "follow_up_smoke": evidence / "smoke.json",
        },
    )
    return ({"events": events}, manifest_path, manifest_sha256)


def test_check_report_rejects_a_fully_self_consistent_evidence_set_without_an_executable_protocol(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _repository(tmp_path)
    _write_update_surface(repo)
    start_tag = _tag_release(repo, "1.61.0", "one")
    hashes = {"00-Inbox/keep.md": "a" * 64}
    foundation_tag = _tag_release(repo, "1.80.0", "foundation")
    follow_up_tag = _tag_release(repo, "1.80.1", "follow-up")
    start = next(item for item in release_fleet.discover_distribution_releases(repo) if item.tag == start_tag)
    foundation = release_fleet.resolve_immutable_release(repo, foundation_tag)
    follow_up = release_fleet.resolve_immutable_release(repo, follow_up_tag)
    monkeypatch.setattr(release_fleet, "discover_distribution_releases", lambda _repo: (start,))
    starting_manifest = _write_starting_manifest(tmp_path, (start,))
    _events, manifest_path, manifest_sha256 = _write_complete_evidence(
        repo, tmp_path, start=start, foundation=foundation, follow_up=follow_up
    )
    report = {
        "foundation_tag": foundation_tag,
        "follow_up_tag": follow_up_tag,
        "platforms": ["darwin"],
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
                "transcript_path": "case.evidence/journey.json",
                "foundation_receipt_path": "case.evidence/foundation-receipt.json",
                "follow_up_receipt_path": "case.evidence/follow-up-receipt.json",
                "foundation_doctor_path": "case.evidence/foundation-doctor.json",
                "follow_up_doctor_path": "case.evidence/follow-up-doctor.json",
                "follow_up_smoke_path": "case.evidence/smoke.json",
                "platform": "darwin",
                "evidence_manifest_path": manifest_path,
                "evidence_manifest_sha256": manifest_sha256,
            }
        ],
    }
    report_path = tmp_path / "report.json"
    report_path.write_text(json.dumps(report), encoding="utf-8")

    with pytest.raises(release_fleet.FleetError, match="executable journey protocol"):
        release_fleet.main(
            [
                "check-report",
                "--repo",
                str(repo),
                "--starting-manifest",
                str(starting_manifest),
                str(report_path),
            ]
        )

    assert "PASS" not in capsys.readouterr().out


def test_check_report_rejects_a_plausible_manifest_when_surface_bytes_are_not_from_the_tag(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _repository(tmp_path)
    _write_update_surface(repo)
    start_tag = _tag_release(repo, "1.61.0", "start")
    foundation_tag = _tag_release(repo, "1.80.0", "foundation")
    follow_up_tag = _tag_release(repo, "1.80.1", "follow-up")
    start = next(item for item in release_fleet.discover_distribution_releases(repo) if item.tag == start_tag)
    foundation = release_fleet.resolve_immutable_release(repo, foundation_tag)
    follow_up = release_fleet.resolve_immutable_release(repo, follow_up_tag)
    monkeypatch.setattr(release_fleet, "discover_distribution_releases", lambda _repo: (start,))
    starting_manifest = _write_starting_manifest(tmp_path, (start,))
    _events, manifest_path, manifest_sha256 = _write_complete_evidence(
        repo, tmp_path, start=start, foundation=foundation, follow_up=follow_up
    )
    forged_surface = {"not": "a release surface"}
    (tmp_path / "case.evidence" / "historic-update-surface.json").write_text(json.dumps(forged_surface))
    # Rewriting the runner manifest's digest cannot make a hand-authored surface
    # pass: check-report independently re-reads the immutable tag bytes.
    manifest = tmp_path / manifest_path
    value = json.loads(manifest.read_text())
    value["artifacts"]["historic_update_surface"]["sha256"] = release_fleet.hashlib.sha256(
        (tmp_path / "case.evidence" / "historic-update-surface.json").read_bytes()
    ).hexdigest()
    manifest.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    manifest_sha256 = release_fleet.hashlib.sha256(manifest.read_bytes()).hexdigest()
    hashes = {"00-Inbox/keep.md": "a" * 64}
    report = {
        "foundation_tag": foundation_tag,
        "follow_up_tag": follow_up_tag,
        "platforms": ["darwin"],
        "cases": [{
            "starting_tag": start_tag, "reached_foundation": True, "reached_follow_up": True,
            "foundation_doctor_healthy": True, "follow_up_doctor_healthy": True,
            "user_hashes_before": hashes, "user_hashes_after_foundation": hashes,
            "user_hashes_after_follow_up": hashes, "transcript_path": "case.evidence/journey.json",
            "foundation_receipt_path": "case.evidence/foundation-receipt.json",
            "follow_up_receipt_path": "case.evidence/follow-up-receipt.json",
            "foundation_doctor_path": "case.evidence/foundation-doctor.json",
            "follow_up_doctor_path": "case.evidence/follow-up-doctor.json",
            "follow_up_smoke_path": "case.evidence/smoke.json", "platform": "darwin",
            "evidence_manifest_path": manifest_path, "evidence_manifest_sha256": manifest_sha256,
        }],
    }
    report_path = tmp_path / "report.json"
    report_path.write_text(json.dumps(report))

    with pytest.raises(release_fleet.FleetError, match="executable journey protocol"):
        release_fleet.main(
            [
                "check-report",
                "--repo",
                str(repo),
                "--starting-manifest",
                str(starting_manifest),
                str(report_path),
            ]
        )


def test_journey_target_must_be_an_immutable_annotated_distribution_tag(tmp_path: Path) -> None:
    repo = _repository(tmp_path)
    _tag_legacy_release(repo, "1.20.1", "legacy")

    with pytest.raises(release_fleet.FleetError, match="immutable dist/release"):
        release_fleet.resolve_immutable_release(repo, "v1.20.1")


def test_case_environment_is_allowlisted_and_has_an_isolated_home(tmp_path: Path) -> None:
    environment = release_fleet._case_environment(tmp_path / "vault", tmp_path / "runtime")

    assert set(environment) == {
        "HOME",
        "TMPDIR",
        "PATH",
        "LANG",
        "LC_ALL",
        "PYTHONNOUSERSITE",
        "PYTHONDONTWRITEBYTECODE",
        "GIT_CONFIG_NOSYSTEM",
        "GIT_TERMINAL_PROMPT",
        "VAULT_PATH",
    }
    assert Path(environment["HOME"]).is_dir()
    assert environment["HOME"] != str(Path.home())
    assert environment["VAULT_PATH"] == str(tmp_path / "vault")


def test_journey_fails_closed_after_recording_immutable_update_surfaces(tmp_path: Path) -> None:
    repo = _repository(tmp_path)
    _write_update_surface(repo)
    start_tag = _tag_release(repo, "1.61.0", "start")
    foundation_tag = _tag_release(repo, "1.80.0", "foundation")
    follow_up_tag = _tag_release(repo, "1.80.5", "follow-up")

    with pytest.raises(release_fleet.FleetError, match="Markdown-only"):
        release_fleet.run_journey(
            repo,
            output=tmp_path / "output",
            starting_tag=start_tag,
            foundation_tag=foundation_tag,
            follow_up_tag=follow_up_tag,
        )

    start = next(item for item in release_fleet.discover_distribution_releases(repo) if item.tag == start_tag)
    evidence_root = tmp_path / "output" / f"{release_fleet.safe_case_name(start)}.evidence"
    result = json.loads((evidence_root / "journey-result.json").read_text())
    manifest = evidence_root / "evidence-manifest.json"
    transcript = json.loads((evidence_root / "journey-transcript.json").read_text())
    assert result["failure"].startswith("published /dex-update surfaces are Markdown-only")
    assert result["evidence_manifest_sha256"] == release_fleet.hashlib.sha256(manifest.read_bytes()).hexdigest()
    assert [event["id"] for event in transcript["events"]] == [
        "historic-update-surface",
        "foundation-update-surface",
    ]
    assert not (tmp_path / "output" / release_fleet.safe_case_name(start)).exists()
