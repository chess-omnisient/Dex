"""Fail-closed tests for cross-platform historic updater acceptance."""

from __future__ import annotations

import hashlib
import importlib
import json
import stat
import subprocess
from dataclasses import fields
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import release_fleet
from scripts.dex_update_bridge import FOUNDATION


def _acceptance():
    try:
        return importlib.import_module("scripts.release_fleet_acceptance")
    except ModuleNotFoundError:
        pytest.fail("release_fleet_acceptance is not implemented")


def _release(tag: str, version: str, suffix: str) -> release_fleet.DistributionRelease:
    return release_fleet.DistributionRelease(
        tag=tag,
        version=version,
        commit=(suffix * 40)[:40],
        tree=((chr(ord(suffix) + 1)) * 40)[:40],
    )


def _foundation() -> dict[str, str]:
    return FOUNDATION.identity()


def _foundation_release() -> release_fleet.DistributionRelease:
    identity = FOUNDATION.identity()
    return release_fleet.DistributionRelease(
        tag=identity["tag"],
        version=identity["version"],
        commit=identity["commit"],
        tree=identity["tree"],
    )


def test_frozen_cohort_excludes_later_control_and_follow_up_releases() -> None:
    acceptance = _acceptance()
    historic = (
        _release("v1.20.1", "1.20.1", "1"),
        _foundation_release(),
    )
    later = (
        _release("v1.81.0", "1.81.0", "3"),
        _release("dist/release/v1.81.1-4444444", "1.81.1", "4"),
    )

    manifest = acceptance.frozen_cohort_manifest(
        historic + later,
        foundation=_foundation(),
        expected_count=2,
    )
    parsed = acceptance.releases_from_frozen_cohort(
        json.dumps(manifest),
        current_releases=historic + later,
        foundation=_foundation(),
        expected_count=2,
    )

    assert parsed == historic
    assert manifest["case_count"] == 2
    assert manifest["foundation"] == _foundation()


def test_frozen_cohort_rejects_a_new_release_at_or_before_the_foundation() -> None:
    acceptance = _acceptance()
    historic = (
        _release("v1.20.1", "1.20.1", "1"),
        _foundation_release(),
    )
    manifest = acceptance.frozen_cohort_manifest(
        historic,
        foundation=_foundation(),
        expected_count=2,
    )
    unexpected = _release("dist/release/v1.79.0-5555555", "1.79.0", "5")

    with pytest.raises(release_fleet.FleetError, match="unexpected historical release"):
        acceptance.releases_from_frozen_cohort(
            json.dumps(manifest),
            current_releases=historic + (unexpected,),
            foundation=_foundation(),
            expected_count=2,
        )


def test_frozen_cohort_rejects_identity_drift_and_wrong_foundation() -> None:
    acceptance = _acceptance()
    historic = (
        _release("v1.20.1", "1.20.1", "1"),
        _foundation_release(),
    )
    manifest = acceptance.frozen_cohort_manifest(
        historic,
        foundation=_foundation(),
        expected_count=2,
    )
    changed = release_fleet.DistributionRelease(
        tag=historic[0].tag,
        version=historic[0].version,
        commit="9" * 40,
        tree=historic[0].tree,
    )

    with pytest.raises(release_fleet.FleetError, match="historic cohort identity drift"):
        acceptance.releases_from_frozen_cohort(
            json.dumps(manifest),
            current_releases=(changed, historic[1]),
            foundation=_foundation(),
            expected_count=2,
        )

    other_foundation = dict(_foundation(), tree="e" * 40)
    with pytest.raises(release_fleet.FleetError, match="foundation identity"):
        acceptance.releases_from_frozen_cohort(
            json.dumps(manifest),
            current_releases=historic,
            foundation=other_foundation,
            expected_count=2,
        )


def test_frozen_cohort_requires_the_exact_foundation_release() -> None:
    acceptance = _acceptance()
    without_foundation = (
        _release("v1.20.1", "1.20.1", "1"),
        _release("dist/release/v1.80.5-2222222", "1.80.5", "2"),
    )

    with pytest.raises(release_fleet.FleetError, match="foundation release"):
        acceptance.frozen_cohort_manifest(
            without_foundation,
            foundation=_foundation(),
            expected_count=2,
        )


def test_real_repository_freezes_exactly_168_historic_trees() -> None:
    acceptance = _acceptance()
    repository = Path(__file__).resolve().parents[2]
    current = release_fleet.discover_distribution_releases(repository)

    manifest = acceptance.frozen_cohort_manifest(current)

    assert manifest["case_count"] == acceptance.EXPECTED_HISTORIC_CASES == 168
    assert manifest["foundation"]["tag"] == "dist/release/v1.80.5-9211053"


def _case(tag: str, platform: str) -> release_fleet.CaseResult:
    hashes = {"00-Inbox/keep.md": "a" * 64}
    return release_fleet.CaseResult(
        starting_tag=tag,
        reached_foundation=True,
        reached_follow_up=True,
        foundation_doctor_healthy=True,
        follow_up_doctor_healthy=True,
        user_hashes_before=hashes,
        user_hashes_after_foundation=hashes,
        user_hashes_after_follow_up=hashes,
        transcript_path=f"{tag}.evidence/transcript.json",
        foundation_receipt_path=f"{tag}.evidence/foundation.json",
        follow_up_receipt_path=f"{tag}.evidence/follow-up.json",
        foundation_doctor_path=f"{tag}.evidence/foundation-doctor.json",
        follow_up_doctor_path=f"{tag}.evidence/follow-up-doctor.json",
        follow_up_smoke_path=f"{tag}.evidence/smoke.json",
        platform=platform,
        evidence_manifest_path=f"{tag}.evidence/manifest.json",
        evidence_manifest_sha256="b" * 64,
    )


def test_platform_report_is_bound_to_one_real_protocol_platform() -> None:
    acceptance = _acceptance()
    tags = {"v1.20.1", "dist/release/v1.80.5-2222222"}
    protocol = SimpleNamespace(platforms=("darwin", "linux"))
    report = release_fleet.AcceptanceReport(
        foundation_tag=FOUNDATION.tag,
        follow_up_tag="dist/release/v1.81.1-3333333",
        cases=tuple(_case(tag, "darwin") for tag in sorted(tags)),
        platforms=("darwin",),
    )

    acceptance.assert_platform_report_bound(
        report,
        protocol=protocol,
        running_platform="darwin",
        expected_start_tags=tags,
    )

    with pytest.raises(release_fleet.FleetError, match="running platform"):
        acceptance.assert_platform_report_bound(
            report,
            protocol=protocol,
            running_platform="linux",
            expected_start_tags=tags,
        )

    broad_report = release_fleet.AcceptanceReport(
        report.foundation_tag,
        report.follow_up_tag,
        report.cases,
        ("darwin", "linux"),
    )
    with pytest.raises(release_fleet.FleetError, match="exactly one"):
        acceptance.assert_platform_report_bound(
            broad_report,
            protocol=protocol,
            running_platform="darwin",
            expected_start_tags=tags,
        )


def test_platform_report_rejects_a_protocol_platform_subset() -> None:
    acceptance = _acceptance()
    report = release_fleet.AcceptanceReport(
        foundation_tag=FOUNDATION.tag,
        follow_up_tag="dist/release/v1.81.1-3333333",
        cases=(_case("v1.20.1", "darwin"),),
        platforms=("darwin",),
    )

    with pytest.raises(release_fleet.FleetError, match="protocol platforms"):
        acceptance.assert_platform_report_bound(
            report,
            protocol=SimpleNamespace(platforms=("darwin",)),
            running_platform="darwin",
            expected_start_tags={"v1.20.1"},
        )


def _signed_session_and_receipts(acceptance, *, expected_count: int = 2):
    key = bytes(range(32))
    session = acceptance.create_acceptance_session(
        cohort_sha256="a" * 64,
        foundation=_foundation(),
        follow_up_tag="dist/release/v1.81.1-3333333",
        source_commit="c" * 40,
        acceptance_source_sha256="d" * 64,
        protocol_platforms=("darwin", "linux"),
        key=key,
        expected_count=expected_count,
        session_id="e" * 64,
    )
    receipts = [
        acceptance.sign_platform_receipt(
            session,
            platform=platform,
            case_result_sha256=digest * 64,
            key=key,
            started=expected_count,
            completed=expected_count,
            passed=expected_count,
            failed=0,
        )
        for platform, digest in (("darwin", "1"), ("linux", "2"))
    ]
    return key, session, receipts


def test_signed_aggregation_requires_exact_darwin_and_linux_receipts() -> None:
    acceptance = _acceptance()
    key, session, receipts = _signed_session_and_receipts(acceptance)

    result = acceptance.aggregate_signed_platform_receipts(
        session,
        receipts,
        key=key,
        protocol_platforms=("darwin", "linux"),
        expected_count=2,
    )

    assert result == {
        "outcome": "HISTORIC_FLEET_ACCEPTED",
        "acceptance": True,
        "platforms": ["darwin", "linux"],
        "case_count": 2,
        "journey_count": 4,
        "discovered": 2,
        "started": 4,
        "completed": 4,
        "passed": 4,
        "failed": 0,
        "session_id": "e" * 64,
    }

    with pytest.raises(release_fleet.FleetError, match="exact protocol platforms"):
        acceptance.aggregate_signed_platform_receipts(
            session,
            [receipts[0]],
            key=key,
            protocol_platforms=("darwin", "linux"),
            expected_count=2,
        )

    with pytest.raises(release_fleet.FleetError, match="protocol platforms"):
        acceptance.aggregate_signed_platform_receipts(
            session,
            receipts,
            key=key,
            protocol_platforms=("darwin",),
            expected_count=2,
        )


def test_signed_aggregation_rejects_tampering_and_incomplete_counts() -> None:
    acceptance = _acceptance()
    key, session, receipts = _signed_session_and_receipts(acceptance)
    unsigned = [receipt["payload"] for receipt in receipts]
    with pytest.raises(release_fleet.FleetError, match="signed shape"):
        acceptance.aggregate_signed_platform_receipts(
            session,
            unsigned,
            key=key,
            protocol_platforms=("darwin", "linux"),
            expected_count=2,
        )

    tampered = json.loads(json.dumps(receipts))
    tampered[0]["payload"]["passed"] = 1

    with pytest.raises(release_fleet.FleetError, match="signature"):
        acceptance.aggregate_signed_platform_receipts(
            session,
            tampered,
            key=key,
            protocol_platforms=("darwin", "linux"),
            expected_count=2,
        )

    incomplete = acceptance.sign_platform_receipt(
        session,
        platform="darwin",
        case_result_sha256="1" * 64,
        key=key,
        started=2,
        completed=1,
        passed=1,
        failed=1,
    )
    with pytest.raises(release_fleet.FleetError, match="incomplete or failed"):
        acceptance.aggregate_signed_platform_receipts(
            session,
            [incomplete, receipts[1]],
            key=key,
            protocol_platforms=("darwin", "linux"),
            expected_count=2,
        )


def _case_document(case: release_fleet.CaseResult) -> dict[str, object]:
    return {field.name: getattr(case, field.name) for field in fields(case)}


def test_platform_collector_retains_every_live_run_and_exact_counts(
    tmp_path: Path,
) -> None:
    acceptance = _acceptance()
    releases = (
        _release("v1.20.1", "1.20.1", "1"),
        _release("dist/release/v1.80.5-2222222", "1.80.5", "2"),
    )
    created: list[object] = []

    def journey_runner(
        _repo: Path,
        *,
        output: Path,
        starting_tag: str,
        foundation_tag: str,
        follow_up_tag: str,
    ) -> object:
        assert output == tmp_path
        assert foundation_tag == FOUNDATION.tag
        assert follow_up_tag == "dist/release/v1.81.1-3333333"
        run = SimpleNamespace(case=_case_document(_case(starting_tag, "darwin")))
        created.append(run)
        return run

    execution = acceptance.collect_platform_runs(
        tmp_path,
        output=tmp_path,
        releases=releases,
        foundation_tag=FOUNDATION.tag,
        follow_up_tag="dist/release/v1.81.1-3333333",
        running_platform="darwin",
        journey_runner=journey_runner,
    )

    assert execution.executor_runs == tuple(created)
    assert [case.starting_tag for case in execution.report.cases] == [release.tag for release in releases]
    assert execution.report.platforms == ("darwin",)
    assert execution.counts == {
        "discovered": 2,
        "started": 2,
        "completed": 2,
        "passed": 2,
        "failed": 0,
    }


def test_platform_collector_stops_on_first_failure_with_honest_counts(
    tmp_path: Path,
) -> None:
    acceptance = _acceptance()
    releases = (
        _release("v1.20.1", "1.20.1", "1"),
        _release("dist/release/v1.80.5-2222222", "1.80.5", "2"),
    )

    def journey_runner(
        _repo: Path,
        *,
        output: Path,
        starting_tag: str,
        foundation_tag: str,
        follow_up_tag: str,
    ) -> object:
        del output, foundation_tag, follow_up_tag
        if starting_tag == releases[1].tag:
            raise release_fleet.FleetError("synthetic journey failed")
        return SimpleNamespace(case=_case_document(_case(starting_tag, "darwin")))

    with pytest.raises(acceptance.PlatformFleetFailure) as failure:
        acceptance.collect_platform_runs(
            tmp_path,
            output=tmp_path,
            releases=releases,
            foundation_tag=FOUNDATION.tag,
            follow_up_tag="dist/release/v1.81.1-3333333",
            running_platform="darwin",
            journey_runner=journey_runner,
        )

    assert failure.value.counts == {
        "discovered": 2,
        "started": 2,
        "completed": 1,
        "passed": 1,
        "failed": 1,
    }


def _immutable_foundation() -> release_fleet.ImmutableRelease:
    identity = FOUNDATION.identity()
    return release_fleet.ImmutableRelease(
        identity["tag"],
        identity["tag_object"],
        identity["commit"],
        identity["tree"],
        identity["version"],
    )


def _immutable_follow_up() -> release_fleet.ImmutableRelease:
    return release_fleet.ImmutableRelease(
        "dist/release/v1.81.1-3333333",
        "3" * 40,
        "3333333" + "4" * 33,
        "5" * 40,
        "1.81.1",
    )


def test_forged_executor_runs_cannot_mint_a_platform_receipt(
    tmp_path: Path,
) -> None:
    acceptance = _acceptance()
    key, session, _receipts = _signed_session_and_receipts(
        acceptance,
        expected_count=2,
    )
    releases = (
        _release("v1.20.1", "1.20.1", "1"),
        _release("dist/release/v1.80.5-2222222", "1.80.5", "2"),
    )
    execution = acceptance.collect_platform_runs(
        tmp_path,
        output=tmp_path,
        releases=releases,
        foundation_tag=FOUNDATION.tag,
        follow_up_tag="dist/release/v1.81.1-3333333",
        running_platform="darwin",
        journey_runner=lambda _repo, **kwargs: SimpleNamespace(
            case=_case_document(_case(str(kwargs["starting_tag"]), "darwin"))
        ),
    )

    with pytest.raises(release_fleet.FleetError, match="executor authority"):
        acceptance.finalize_live_platform_execution(
            execution,
            repo=tmp_path,
            evidence_root=tmp_path,
            foundation=_immutable_foundation(),
            follow_up=_immutable_follow_up(),
            protocol=SimpleNamespace(platforms=("darwin", "linux")),
            expected_start_tags={release.tag for release in releases},
            session=session,
            key=key,
            cohort_sha256="a" * 64,
            source_commit="c" * 40,
            acceptance_source_sha256="d" * 64,
            expected_count=2,
        )


def test_changed_evidence_validator_cannot_mint_a_platform_receipt(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    acceptance = _acceptance()
    key, session, _receipts = _signed_session_and_receipts(
        acceptance,
        expected_count=2,
    )
    releases = (
        _release("v1.20.1", "1.20.1", "1"),
        _release("dist/release/v1.80.5-2222222", "1.80.5", "2"),
    )
    execution = acceptance.collect_platform_runs(
        tmp_path,
        output=tmp_path,
        releases=releases,
        foundation_tag=FOUNDATION.tag,
        follow_up_tag="dist/release/v1.81.1-3333333",
        running_platform="darwin",
        journey_runner=lambda _repo, **kwargs: SimpleNamespace(
            case=_case_document(_case(str(kwargs["starting_tag"]), "darwin"))
        ),
    )
    monkeypatch.setattr(release_fleet, "assert_evidence_bound", lambda *args, **kwargs: None)

    with pytest.raises(release_fleet.FleetError, match="validator changed"):
        acceptance.finalize_live_platform_execution(
            execution,
            repo=tmp_path,
            evidence_root=tmp_path,
            foundation=_immutable_foundation(),
            follow_up=_immutable_follow_up(),
            protocol=SimpleNamespace(platforms=("darwin", "linux")),
            expected_start_tags={release.tag for release in releases},
            session=session,
            key=key,
            cohort_sha256="a" * 64,
            source_commit="c" * 40,
            acceptance_source_sha256="d" * 64,
            expected_count=2,
        )


def test_session_key_file_is_private_and_rejects_symlinks(tmp_path: Path) -> None:
    acceptance = _acceptance()
    key_path = tmp_path / "acceptance.key"
    key = bytes(range(32))

    acceptance.write_session_key(key_path, key=key)

    assert acceptance.read_session_key(key_path) == key
    assert stat.S_IMODE(key_path.stat().st_mode) == 0o600
    with pytest.raises(release_fleet.FleetError, match="already exists"):
        acceptance.write_session_key(key_path, key=key)

    key_path.unlink()
    target = tmp_path / "target.key"
    target.write_bytes(key)
    key_path.symlink_to(target)
    with pytest.raises(release_fleet.FleetError, match="unsafe"):
        acceptance.read_session_key(key_path)


def test_cohort_cli_writes_the_exact_168_tree_manifest(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    acceptance = _acceptance()
    repository = Path(__file__).resolve().parents[2]
    output = tmp_path / "historic-through-v1.80.5.json"

    exit_code = acceptance.main(["cohort", "--repo", str(repository), "--output", str(output)])

    result = json.loads(capsys.readouterr().out)
    manifest = json.loads(output.read_text(encoding="utf-8"))
    assert exit_code == 0
    assert result == {
        "acceptance": False,
        "case_count": 168,
        "foundation_tag": FOUNDATION.tag,
        "outcome": "HISTORIC_COHORT_FROZEN",
        "output": str(output),
    }
    assert manifest["case_count"] == 168


def test_acceptance_source_is_bound_to_exact_publisher_commit_bytes(
    tmp_path: Path,
) -> None:
    acceptance = _acceptance()
    repository = tmp_path / "publisher"
    source = repository / "scripts" / "release_fleet_acceptance.py"
    source.parent.mkdir(parents=True)
    source.write_bytes(Path(acceptance.__file__).read_bytes())
    subprocess.run(["git", "init", "-q", str(repository)], check=True)
    subprocess.run(
        ["git", "-C", str(repository), "config", "user.name", "Dex Fleet Test"],
        check=True,
    )
    subprocess.run(
        [
            "git",
            "-C",
            str(repository),
            "config",
            "user.email",
            "fleet@example.com",
        ],
        check=True,
    )
    subprocess.run(["git", "-C", str(repository), "add", str(source)], check=True)
    subprocess.run(
        ["git", "-C", str(repository), "commit", "-qm", "exact publisher source"],
        check=True,
    )
    exact_commit = subprocess.run(
        ["git", "-C", str(repository), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    digest = acceptance.verify_acceptance_source_bound(repository, exact_commit)

    assert digest == hashlib.sha256(source.read_bytes()).hexdigest()
    source.write_text("# changed publisher source\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repository), "add", str(source)], check=True)
    subprocess.run(
        ["git", "-C", str(repository), "commit", "-qm", "changed publisher source"],
        check=True,
    )
    changed_commit = subprocess.run(
        ["git", "-C", str(repository), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    with pytest.raises(release_fleet.FleetError, match="acceptance orchestrator bytes"):
        acceptance.verify_acceptance_source_bound(repository, changed_commit)


def test_full_command_surface_aggregates_two_live_platform_receipts(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    acceptance = _acceptance()
    releases = tuple(
        _release(f"v1.0.{index}", f"1.0.{index}", f"{index % 10}")
        for index in range(1, acceptance.EXPECTED_HISTORIC_CASES + 1)
    )
    foundation = _immutable_foundation()
    follow_up = _immutable_follow_up()
    protocol = SimpleNamespace(platforms=("darwin", "linux"))
    inputs = acceptance.FleetInputs(
        releases=releases,
        foundation=foundation,
        follow_up=follow_up,
        protocol=protocol,
        source_commit="c" * 40,
        acceptance_source_sha256="d" * 64,
        cohort_sha256="a" * 64,
    )
    monkeypatch.setattr(acceptance, "load_fleet_inputs", lambda *args, **kwargs: inputs)
    session_path = tmp_path / "session.json"
    key_path = tmp_path / "session.key"

    assert (
        acceptance.main(
            [
                "session",
                "--repo",
                str(tmp_path),
                "--cohort",
                str(tmp_path / "cohort.json"),
                "--foundation-tag",
                foundation.tag,
                "--follow-up-tag",
                follow_up.tag,
                "--session-output",
                str(session_path),
                "--key-output",
                str(key_path),
            ]
        )
        == 0
    )
    session = json.loads(session_path.read_text(encoding="utf-8"))
    capsys.readouterr()

    def collect(*args, running_platform: str, **kwargs):
        del args, kwargs
        return SimpleNamespace(
            report=SimpleNamespace(platforms=(running_platform,)),
            counts={
                "discovered": 168,
                "started": 168,
                "completed": 168,
                "passed": 168,
                "failed": 0,
            },
        )

    def finalize(execution, **kwargs):
        return acceptance.sign_platform_receipt(
            kwargs["session"],
            platform=execution.report.platforms[0],
            case_result_sha256=("1" if execution.report.platforms[0] == "darwin" else "2") * 64,
            key=kwargs["key"],
            started=168,
            completed=168,
            passed=168,
            failed=0,
        )

    monkeypatch.setattr(acceptance, "collect_platform_runs", collect)
    monkeypatch.setattr(acceptance, "finalize_live_platform_execution", finalize)
    receipt_paths: list[Path] = []
    for platform in ("darwin", "linux"):
        monkeypatch.setattr(acceptance, "_running_platform", lambda value=platform: value)
        receipt_path = tmp_path / f"{platform}.receipt.json"
        receipt_paths.append(receipt_path)
        assert (
            acceptance.main(
                [
                    "platform",
                    "--repo",
                    str(tmp_path),
                    "--cohort",
                    str(tmp_path / "cohort.json"),
                    "--foundation-tag",
                    foundation.tag,
                    "--follow-up-tag",
                    follow_up.tag,
                    "--session",
                    str(session_path),
                    "--key",
                    str(key_path),
                    "--output",
                    str(tmp_path / platform),
                    "--receipt-output",
                    str(receipt_path),
                ]
            )
            == 0
        )
        capsys.readouterr()

    aggregate_path = tmp_path / "aggregate.json"
    assert (
        acceptance.main(
            [
                "aggregate",
                "--repo",
                str(tmp_path),
                "--cohort",
                str(tmp_path / "cohort.json"),
                "--foundation-tag",
                foundation.tag,
                "--follow-up-tag",
                follow_up.tag,
                "--session",
                str(session_path),
                "--key",
                str(key_path),
                "--receipt",
                str(receipt_paths[0]),
                "--receipt",
                str(receipt_paths[1]),
                "--output",
                str(aggregate_path),
            ]
        )
        == 0
    )
    result = json.loads(aggregate_path.read_text(encoding="utf-8"))
    assert result == {
        "acceptance": True,
        "case_count": 168,
        "completed": 336,
        "discovered": 168,
        "failed": 0,
        "journey_count": 336,
        "outcome": "HISTORIC_FLEET_ACCEPTED",
        "passed": 336,
        "platforms": ["darwin", "linux"],
        "session_id": session["payload"]["session_id"],
        "started": 336,
    }
