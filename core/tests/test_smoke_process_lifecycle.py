"""Harness lifecycle contracts for smoke journeys under sandbox / xdist races.

#477: revived journeys failed ~1/3 of GitHub-hosted runs with a bare EPERM from
process-group teardown (internal-journey dispatch and descendant cleanup are the
same lifecycle). These tests pin the product choice: diagnosable OSErrors,
named skip when the syscall is unavailable, real descendant kill when Darwin
returns EPERM on a zombie leader, and no unfailable exit_code==0 gate.
"""

from __future__ import annotations

import errno
import json
import sys
import time
from pathlib import Path

from core.utils import mcp_handshake, process_isolation, smoke
from core.tests.test_smoke import REPO_ROOT, _definition, _write_valid_vault


def test_format_os_error_names_errno_operation_and_path() -> None:
    bare = OSError(errno.EPERM, "Operation not permitted")
    detail = process_isolation.format_os_error(bare, operation="internal-journey")

    assert "internal-journey" in detail
    assert "errno=1 (EPERM)" in detail
    assert "path=<none>" in detail
    assert "Operation not permitted" in detail

    with_path = OSError(errno.EPERM, "Operation not permitted", "/tmp/dex-smoke-x")
    assert "path=/tmp/dex-smoke-x" in process_isolation.format_os_error(
        with_path, operation="chmod"
    )


def test_sandbox_refused_is_only_bare_eperm() -> None:
    assert process_isolation.sandbox_refused(OSError(errno.EPERM, "Operation not permitted"))
    assert not process_isolation.sandbox_refused(
        OSError(errno.EPERM, "Operation not permitted", "/tmp/vault")
    )
    assert not process_isolation.sandbox_refused(
        PermissionError("internal smoke mode requires a regular parent-created run marker")
    )
    assert not process_isolation.sandbox_refused(OSError(errno.EACCES, "Permission denied"))


def test_bare_eperm_in_internal_journey_is_named_skip_with_errno(
    monkeypatch,
    tmp_path: Path,
    capsys,
) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()
    monkeypatch.setenv("VAULT_PATH", str(vault))
    monkeypatch.setattr(smoke, "_authorize_internal", lambda *_args: None)
    monkeypatch.setattr(smoke, "_block_python_network", lambda: None)
    monkeypatch.setattr(smoke, "_internal_release_root", lambda *_args: tmp_path)

    def fail_with_bare_eperm(*_args: object) -> dict[str, str]:
        raise OSError(errno.EPERM, "Operation not permitted")

    monkeypatch.setitem(smoke.INTERNAL_JOURNEYS, "configs", fail_with_bare_eperm)

    exit_code = smoke.main(["--_journey", "configs"])
    result = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert result["verdict"] == "UNKNOWN"
    assert result["detail"].startswith(process_isolation.SANDBOX_UNAVAILABLE_PREFIX)
    assert "internal-journey" in result["detail"]
    assert "errno=1 (EPERM)" in result["detail"]
    assert "path=<none>" in result["detail"]


def test_authorize_permissionerror_still_refuses_with_exit_two(
    monkeypatch,
    tmp_path: Path,
    capsys,
) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()
    monkeypatch.setenv("VAULT_PATH", str(vault))
    monkeypatch.setattr(
        smoke,
        "_authorize_internal",
        lambda *_args: (_ for _ in ()).throw(
            PermissionError("internal smoke mode requires a regular parent-created run marker")
        ),
    )

    exit_code = smoke.main(["--_journey", "configs"])
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "internal smoke journey refused:" in captured.err
    assert "internal-journey" in captured.err
    assert "requires a regular parent-created run marker" in captured.err
    assert captured.out == ""


def test_start_new_session_eperm_is_named_skip_not_harness_failed(
    monkeypatch,
    tmp_path: Path,
) -> None:
    vault = _write_valid_vault(tmp_path)
    original = smoke.subprocess.Popen

    def refuse_new_session(*args: object, **kwargs: object):
        if kwargs.get("start_new_session"):
            raise OSError(errno.EPERM, "Operation not permitted")
        return original(*args, **kwargs)

    monkeypatch.setattr(smoke.subprocess, "Popen", refuse_new_session)

    run = smoke.run_smoke(
        vault_root=vault,
        repo_root=REPO_ROOT,
        journey_definitions=(_definition("configs"),),
    )

    assert run.harness_failed is False
    assert run.exit_code == 0
    detail = run.report["journeys"][0]["detail"]
    assert detail.startswith(process_isolation.SANDBOX_UNAVAILABLE_PREFIX)
    assert "start_new_session" in detail
    assert "errno=1 (EPERM)" in detail


def test_broken_product_journey_still_fails_the_gate(tmp_path: Path) -> None:
    vault = _write_valid_vault(tmp_path)
    (vault / "System" / "pillars.yaml").write_text("pillars: [\n", encoding="utf-8")

    run = smoke.run_smoke(
        vault_root=vault,
        repo_root=REPO_ROOT,
        journey_definitions=(_definition("configs"),),
    )

    assert run.exit_code == 1
    assert run.harness_failed is False
    assert run.report["journeys"][0]["verdict"] == "BROKEN"


def test_handshake_teardown_eperm_does_not_fail_a_finished_initialize(
    monkeypatch,
    tmp_path: Path,
) -> None:
    server = tmp_path / "fast-exit-server.py"
    server.write_text(
        "import json, sys\n"
        "request = json.loads(sys.stdin.readline())\n"
        "print(json.dumps({'jsonrpc': '2.0', 'id': request['id'], 'result': "
        "{'capabilities': {}, 'serverInfo': {'name': 'fast-exit', 'version': '1'}}}), "
        "flush=True)\n",
        encoding="utf-8",
    )

    def eperm_killpg(_pgid: int, _sig: int) -> None:
        raise PermissionError(errno.EPERM, "Operation not permitted")

    monkeypatch.setattr(process_isolation.os, "killpg", eperm_killpg)

    result = mcp_handshake.mcp_stdio_handshake(
        [sys.executable, str(server)],
        timeout=5.0,
    )

    assert result.ok is True
    assert result.error is None


def test_killpg_eperm_still_reaps_descendants_after_normal_exit(
    monkeypatch,
    tmp_path: Path,
) -> None:
    vault = _write_valid_vault(tmp_path)
    sentinel = tmp_path / "eperm-orphan-survived"
    spawned = tmp_path / "eperm-descendant-spawned"
    descendant = (
        "import time; from pathlib import Path; time.sleep(2.5); "
        f"Path({str(sentinel)!r}).touch()"
    )
    parent = (
        "import json, subprocess, sys; from pathlib import Path; "
        f"subprocess.Popen([sys.executable, '-c', {descendant!r}], "
        "stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); "
        f"Path({str(spawned)!r}).touch(); "
        "print(json.dumps({'verdict': 'OK', 'detail': 'parent exited'}))"
    )
    monkeypatch.setattr(
        smoke,
        "_journey_command",
        lambda *_args: [sys.executable, "-c", parent],
    )

    def eperm_killpg(_pgid: int, _sig: int) -> None:
        raise PermissionError(errno.EPERM, "Operation not permitted")

    monkeypatch.setattr(process_isolation.os, "killpg", eperm_killpg)

    run = smoke.run_smoke(
        vault_root=vault,
        repo_root=REPO_ROOT,
        journey_definitions=(_definition("configs"),),
    )
    time.sleep(4.0)

    assert run.exit_code == 0
    assert run.harness_failed is False
    assert spawned.exists(), "the parent never spawned a descendant"
    assert not sentinel.exists()


def test_timed_out_journey_kills_descendants_when_killpg_returns_eperm(
    monkeypatch,
    tmp_path: Path,
) -> None:
    vault = _write_valid_vault(tmp_path)
    sentinel = tmp_path / "eperm-timeout-orphan-survived"
    spawned = tmp_path / "eperm-timeout-descendant-spawned"
    budget, descendant_delay, post_run_wait = 3.0, 8.0, 10.0
    descendant = (
        f"import time; from pathlib import Path; time.sleep({descendant_delay}); "
        f"Path({str(sentinel)!r}).touch()"
    )
    parent = (
        "import subprocess, sys; from pathlib import Path; "
        f"subprocess.Popen([sys.executable, '-c', {descendant!r}]); "
        f"Path({str(spawned)!r}).touch(); "
        "import time; time.sleep(60)"
    )
    monkeypatch.setattr(
        smoke,
        "_journey_command",
        lambda *_args: [sys.executable, "-c", parent],
    )

    def eperm_killpg(_pgid: int, _sig: int) -> None:
        raise PermissionError(errno.EPERM, "Operation not permitted")

    monkeypatch.setattr(process_isolation.os, "killpg", eperm_killpg)

    run = smoke.run_smoke(
        vault_root=vault,
        repo_root=REPO_ROOT,
        journey_definitions=(_definition("configs", budget)),
    )
    time.sleep(post_run_wait)

    assert run.exit_code == 2
    assert "timed out" in run.report["journeys"][0]["detail"]
    assert spawned.exists(), (
        "the parent never spawned a descendant, so this test did not exercise the "
        "kill path at all; it cannot pass on that basis"
    )
    assert not sentinel.exists()


def test_smoke_temp_is_isolated_per_xdist_worker(monkeypatch, tmp_path: Path) -> None:
    vault = _write_valid_vault(tmp_path)
    monkeypatch.setenv("PYTEST_XDIST_WORKER", "gw7")
    observed_prefixes: list[str] = []
    original = smoke.tempfile.TemporaryDirectory

    def capture_temporary_directory(*args: object, **kwargs: object):
        prefix = kwargs.get("prefix")
        if isinstance(prefix, str):
            observed_prefixes.append(prefix)
        return original(*args, **kwargs)

    monkeypatch.setattr(smoke.tempfile, "TemporaryDirectory", capture_temporary_directory)

    run = smoke.run_smoke(
        vault_root=vault,
        repo_root=REPO_ROOT,
        journey_definitions=(_definition("configs"),),
    )

    assert run.exit_code == 0
    assert any(prefix.startswith("dex-smoke-gw7-run-") for prefix in observed_prefixes)
