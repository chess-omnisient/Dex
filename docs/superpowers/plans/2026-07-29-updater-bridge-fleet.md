# Updater Bridge Fleet Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make “no released Dex installation is left behind” a repeatable, evidence-backed release gate: every distinct published release tree must reach a foundation release safely, then reach a subsequent release through `/dex-update` alone.

**Architecture:** Keep the acceptance tool in the repository so its behaviour is reviewed and tested, but create every aged installation in a fresh temporary directory outside the repository. The tool will discover every distinct public release tree (`dist/release/v*` plus older public `v*` tags that predate that format), construct a realistic old vault with non-personal fixture data and recorded ownership hashes, and emit a machine-readable case manifest. A separate journey runner will consume only an immutable, published foundation tag and follow-up tag, record the before/after evidence, and refuse to call the fleet complete unless every case has both receipts and unchanged user-owned hashes.

**Tech Stack:** Python 3 standard library, Git command line, existing lifecycle delivery service, pytest, shell release scripts.

---

## Release contract

The gate has two irreversible truth rules:

1. The foundation and follow-up inputs are annotated `dist/release/v*` tags that exist on the public release remote. A local branch, a source checkout, or an untagged `main` commit is not an input.
2. A case passes only after its own installed release identity resolves to the foundation tag, its user-owned fixture hashes match exactly, `/dex-doctor` is healthy, then the same installation resolves to the follow-up tag through the release-delivery service and still preserves those hashes.

There are currently 156 distinct trees across the public release tags. The test set must retain different trees that share a semantic version, because they are different packages a real person might have installed. It may collapse only byte-identical trees.

### Task 1: Add the release-tree discovery contract

**Files:**
- Create: `scripts/release_fleet.py`
- Create: `core/tests/test_release_fleet.py`

- [ ] **Step 1: Write the failing discovery tests**

```python
def test_discovers_each_distinct_distribution_tree_once(tmp_path: Path) -> None:
    repo = _repository(tmp_path)
    first = _tag_release(repo, "1.61.0", "one")
    second = _tag_release(repo, "1.61.0", "two")
    _same_tree = _tag_release(repo, "1.62.0", "two", allow_empty=True)
    releases = release_fleet.discover_distribution_releases(repo)
    assert [release.tag for release in releases] == [
        first,
        second,
    ]


def test_rejects_distribution_tag_that_does_not_name_its_commit(tmp_path: Path) -> None:
    repo = _repository(tmp_path)
    _tag_release(repo, "1.61.0", "actual", suffix="deadbee")
    with pytest.raises(release_fleet.FleetError, match="does not match"):
        release_fleet.discover_distribution_releases(repo)
```

- [ ] **Step 2: Run the discovery tests and verify they fail because `release_fleet` does not exist**

Run: `.venv/bin/python -m pytest core/tests/test_release_fleet.py -q`

Expected: collection fails with `ModuleNotFoundError: No module named 'scripts.release_fleet'`.

- [ ] **Step 3: Implement only the immutable-release discovery surface**

```python
@dataclass(frozen=True)
class DistributionRelease:
    tag: str
    version: str
    commit: str
    tree: str


def discover_distribution_releases(repo: Path) -> tuple[DistributionRelease, ...]:
    seen_trees: set[str] = set()
    discovered: list[DistributionRelease] = []
    for tag in _git_lines(repo, "tag", "--list", "dist/release/v*"):
        match = RELEASE_TAG.fullmatch(tag)
        if match is None:
            continue
        commit = _git(repo, "rev-parse", f"{tag}^{{commit}}")
        if not commit.startswith(match.group("short")):
            raise FleetError(f"{tag}: tag suffix does not match its commit")
        tree = _git(repo, "rev-parse", f"{tag}^{{tree}}")
        if tree in seen_trees:
            continue
        seen_trees.add(tree)
        discovered.append(DistributionRelease(tag, match.group("version"), commit, tree))
    return tuple(sorted(discovered, key=lambda item: (_version_key(item.version), item.tag)))
```

`_git` must invoke Git with `check=True`, capture text output, and raise `FleetError` with the command’s stderr on failure. `_version_key` must return `tuple(int(part) for part in version.split("."))`.

- [ ] **Step 4: Run the discovery tests and verify they pass**

Run: `.venv/bin/python -m pytest core/tests/test_release_fleet.py -q`

Expected: `2 passed`.

- [ ] **Step 5: Commit the tested discovery contract**

```bash
git add scripts/release_fleet.py core/tests/test_release_fleet.py
git commit -m "test: discover every distinct published Dex release tree"
```

### Task 2: Build clean, non-personal aged-vault fixtures

**Files:**
- Modify: `scripts/release_fleet.py`
- Modify: `core/tests/test_release_fleet.py`

- [ ] **Step 1: Write the failing fixture tests**

```python
def test_build_fixture_uses_the_requested_release_and_preserves_user_hashes(tmp_path: Path) -> None:
    repo = _repository(tmp_path)
    _tag_release(repo, "1.61.0", "one")
    release = release_fleet.discover_distribution_releases(repo)[0]
    case = release_fleet.build_fixture(repo, release, tmp_path / "fleet")
    assert _git(case.vault, "rev-parse", "HEAD^") == release.commit
    assert _git(case.vault, "remote", "get-url", "upstream") == release_fleet.PUBLIC_REMOTE
    assert _git(case.vault, "remote", "get-url", "--push", "upstream") == "DISABLED"
    assert case.user_hashes == release_fleet.hash_user_owned_files(case.vault)


def test_build_fixture_refuses_a_nonempty_output_directory(tmp_path: Path) -> None:
    output = tmp_path / "fleet"
    output.mkdir()
    release = _release()
    case = output / release_fleet.safe_case_name(release)
    case.mkdir()
    (case / "keep-me").write_text("do not delete", encoding="utf-8")
    with pytest.raises(release_fleet.FleetError, match="empty"):
        release_fleet.build_fixture(tmp_path, release, output)
```

- [ ] **Step 2: Run the fixture tests and verify they fail because `build_fixture` does not exist**

Run: `.venv/bin/python -m pytest core/tests/test_release_fleet.py -q`

Expected: failure naming `build_fixture`.

- [ ] **Step 3: Implement fresh fixture creation without copying founder data or deleting an existing directory**

```python
USER_FIXTURES = {
    "00-Inbox/keep.md": b"# User note\\nThis must survive updates.\\n",
    "03-Tasks/Tasks.md": b"# My task\\n- Keep this task exactly.\\n",
    "System/user-profile.yaml": b"updates:\\n  channel: stable\\n",
    ".claude/skills/my-weekly-review/SKILL.md": b"---\\nname: my-weekly-review\\n---\\n# User skill\\n",
}


def build_fixture(repo: Path, release: DistributionRelease, output: Path) -> FleetCase:
    output.mkdir(parents=True, exist_ok=True)
    vault = output / safe_case_name(release)
    if vault.exists():
        raise FleetError(f"fleet case directory must be empty: {vault}")
    _run(repo, "clone", "--no-checkout", "--no-local", str(repo), str(vault))
    _run(vault, "checkout", "--detach", release.tag)
    _run(vault, "remote", "rename", "origin", "upstream")
    _run(vault, "remote", "set-url", "upstream", PUBLIC_REMOTE)
    _run(vault, "remote", "set-url", "--push", "upstream", "DISABLED")
    for relative, content in USER_FIXTURES.items():
        path = vault / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    _run(vault, "config", "user.name", "Dex Fleet Fixture")
    _run(vault, "config", "user.email", "fleet@example.invalid")
    _run(vault, "add", "-A")
    _run(vault, "commit", "-m", "test: simulated user content")
    return FleetCase(release=release, vault=vault, user_hashes=hash_user_owned_files(vault))
```

`hash_user_owned_files` must hash only `USER_FIXTURES` paths using SHA-256 and must fail when any expected fixture path is missing, a directory, or a symlink.

- [ ] **Step 4: Run the fixture tests and verify they pass**

Run: `.venv/bin/python -m pytest core/tests/test_release_fleet.py -q`

Expected: all release-fleet tests pass.

- [ ] **Step 5: Commit the fixture builder**

```bash
git add scripts/release_fleet.py core/tests/test_release_fleet.py
git commit -m "test: build disposable historic Dex update fixtures"
```

### Task 3: Define the two-release acceptance report and fail-closed checker

**Files:**
- Modify: `scripts/release_fleet.py`
- Modify: `core/tests/test_release_fleet.py`
- Create: `docs/release-fleet-acceptance.md`

- [ ] **Step 1: Write the failing report tests**

```python
def test_acceptance_report_requires_both_release_hops_and_unchanged_user_hashes() -> None:
    report = release_fleet.AcceptanceReport(
        foundation_tag="dist/release/v1.80.0-aaaaaaa",
        follow_up_tag="dist/release/v1.80.1-bbbbbbb",
        cases=(
            release_fleet.CaseResult("dist/release/v1.61.0-ccccccc", True, True, True),
            release_fleet.CaseResult("dist/release/v1.62.0-ddddddd", True, False, True),
        ),
    )
    with pytest.raises(release_fleet.FleetError, match="follow-up"):
        release_fleet.assert_complete(report)
```

- [ ] **Step 2: Run the report test and verify it fails because the report classes do not exist**

Run: `.venv/bin/python -m pytest core/tests/test_release_fleet.py -q`

Expected: failure naming `AcceptanceReport` or `assert_complete`.

- [ ] **Step 3: Implement the fail-closed report contract and CLI**

```python
def assert_complete(report: AcceptanceReport) -> None:
    if not report.cases:
        raise FleetError("acceptance report contains no historic releases")
    failures = [
        result.tag for result in report.cases
        if not (result.reached_foundation and result.reached_follow_up and result.user_hashes_preserved)
    ]
    if failures:
        raise FleetError("release fleet acceptance failed: " + ", ".join(failures))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    subcommands = parser.add_subparsers(dest="command", required=True)
    build = subcommands.add_parser("build")
    build.add_argument("--repo", type=Path, required=True)
    build.add_argument("--output", type=Path, required=True)
    check = subcommands.add_parser("check-report")
    check.add_argument("report", type=Path)
    args = parser.parse_args(argv)
    if args.command == "build":
        cases = [build_fixture(args.repo, release, args.output) for release in discover_distribution_releases(args.repo)]
        print(json.dumps({"case_count": len(cases), "cases": [case.to_dict() for case in cases]}, indent=2))
        return 0
    report = AcceptanceReport.from_json(args.report.read_text(encoding="utf-8"))
    assert_complete(report)
    print(f"PASS: {len(report.cases)} historic release trees reached both releases")
    return 0
```

The JSON report must include the full starting tag, foundation tag, follow-up tag, exact installed identity after each hop, before/after user hash maps, Doctor verdict, timestamp, and the path to the user-visible journey transcript. Missing fields, unknown versions, or a changed user hash must make `check-report` fail.

- [ ] **Step 4: Document the only acceptable live rehearsal**

`docs/release-fleet-acceptance.md` must say:

```markdown
1. Build fixtures from the public `dist/release/v*` tags; never from `main`.
2. Publish the foundation tag before starting the first hop.
3. Run each fixture's own `/dex-update` journey. A refusal is a finding; do not repair around it.
4. Run `/dex-doctor` and record the receipt and user-hash comparison.
5. Publish a follow-up tag, then repeat `/dex-update` from the same fixture.
6. Run `python3 scripts/release_fleet.py check-report REPORT.json`.
7. Do not describe the update promise as proven unless this command passes for every distinct published release tree on every supported platform.
```

- [ ] **Step 5: Run the full release-fleet unit suite and verify it passes**

Run: `.venv/bin/python -m pytest core/tests/test_release_fleet.py -q`

Expected: all tests pass with no network access or mutation outside pytest’s temporary directory.

- [ ] **Step 6: Commit the gate and its operating instructions**

```bash
git add scripts/release_fleet.py core/tests/test_release_fleet.py docs/release-fleet-acceptance.md
git commit -m "feat: add all-version Dex update acceptance gate"
```

### Task 4: Rehearse the gate before any production release

**Files:**
- Modify: `core/tests/test_release_fleet.py` only if rehearsal exposes a contract gap
- Create outside the repository: a temporary fleet directory created with `mktemp -d`

- [ ] **Step 1: Install the isolated test dependencies**

Run:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
npm ci
```

Expected: test interpreter and Node dependencies are available in this worktree only.

- [ ] **Step 2: Run the focused unit suite and the existing delivery contracts**

Run:

```bash
.venv/bin/python -m pytest \
  core/tests/test_release_fleet.py \
  core/tests/test_apply_update.py \
  core/tests/test_lifecycle_service_contract.py -q
npm run test:hooks
```

Expected: all selected Python tests and hooks pass.

- [ ] **Step 3: Discover the complete current historic matrix without building duplicate repositories**

Run:

```bash
.venv/bin/python scripts/release_fleet.py manifest --repo . > /private/tmp/dex-release-fleet-manifest.json
```

Expected: the manifest reports 156 distinct starting trees; no path under `~/dex/artifacts/migration-fleet/` is changed. Build and exercise one starting tag at a time with `build --starting-tag TAG` so the final run never stores 156 full repositories concurrently.

- [ ] **Step 4: Record the release blocker honestly**

The current public tag is v1.79.0. There is no published foundation tag containing self-delivery and no subsequent public follow-up tag. Therefore no command can truthfully complete live two-hop acceptance yet. Record the prepared matrix count and unit verification, but do not call it release proof.

- [ ] **Step 5: Commit only a regression exposed by the rehearsal, otherwise leave the completed implementation commit unchanged**

```bash
git status --short
```

Expected: clean tree after the committed implementation; temporary fleet is not tracked.

## Plan self-review

- Every distinct published distribution tree is discovered from immutable annotated tags (Task 1).
- No fixture reads Dave’s vault or copies personal content; every user-owned byte is synthetic and hash-checked (Task 2).
- The release report requires both historical-to-foundation and foundation-to-follow-up evidence, not merely a passing unit test (Task 3).
- The final proof is intentionally blocked until two actual public tags exist; Task 4 distinguishes prepared infrastructure from release acceptance.
- No step deletes an existing directory or uses a mutable working tree as a historic release fixture.
