"""Process-wide state that shard workers reuse across tests.

CI shard 2 runs pytest-xdist workers. A test that substitutes ``time.sleep``,
``subprocess.Popen``, ``tempfile.tempdir``, or the executor's controller bridge
leaves that binding for every later test on the same worker. The shard-2
alternating failures in #443 were this class of leak, not a slow assertion.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from types import ModuleType
from typing import Any

# Filled by the pytest_runtest_teardown hook in conftest so a failed isolation
# check can name the test that just finished on this worker.
last_completed_nodeid = "session-start"


_WATCHED_ENV = (
    "VAULT_PATH",
    "TMPDIR",
    "TEMP",
    "TMP",
    "DEX_MCP_HANDSHAKE_TIMEOUT",
    "DEX_SMOKE_RUN_TOKEN",
)


def note_completed(nodeid: str) -> None:
    global last_completed_nodeid
    last_completed_nodeid = nodeid


def _env_snapshot() -> dict[str, str | None]:
    return {name: os.environ.get(name) for name in _WATCHED_ENV}


@dataclass(frozen=True)
class ProcessBaseline:
    sleep: Any
    time_fn: Any
    time_ns: Any
    popen: Any
    os_open: Any
    os_rename: Any
    os_killpg: Any
    os_fsync: Any
    tempdir: str | None
    stdin: Any
    stdout: Any
    env: dict[str, str | None]

    @classmethod
    def capture(cls) -> ProcessBaseline:
        return cls(
            sleep=time.sleep,
            time_fn=time.time,
            time_ns=time.time_ns,
            popen=subprocess.Popen,
            os_open=os.open,
            os_rename=os.rename,
            os_killpg=getattr(os, "killpg", None),
            os_fsync=os.fsync,
            tempdir=tempfile.tempdir,
            stdin=sys.stdin,
            stdout=sys.stdout,
            env=_env_snapshot(),
        )

    def differences(self) -> list[str]:
        current = ProcessBaseline.capture()
        mismatches: list[str] = []
        identity_fields = (
            "sleep",
            "time_fn",
            "time_ns",
            "popen",
            "os_open",
            "os_rename",
            "os_killpg",
            "os_fsync",
            "stdin",
            "stdout",
        )
        for field in identity_fields:
            if getattr(current, field) is not getattr(self, field):
                mismatches.append(field)
        if current.tempdir != self.tempdir:
            mismatches.append("tempdir")
        if current.env != self.env:
            changed = [
                name
                for name in _WATCHED_ENV
                if current.env.get(name) != self.env.get(name)
            ]
            mismatches.append("env:" + ",".join(changed))
        return mismatches


_BASELINE: ProcessBaseline | None = None


def session_baseline() -> ProcessBaseline:
    global _BASELINE
    if _BASELINE is None:
        _BASELINE = ProcessBaseline.capture()
    return _BASELINE


def assert_process_isolation(when: str) -> None:
    mismatches = session_baseline().differences()
    if not mismatches:
        return
    raise AssertionError(
        f"process state leaked {when}; leftover={mismatches}; "
        f"previous test on this worker={last_completed_nodeid!r}"
    )


def assert_executor_isolation(executor_module: ModuleType, when: str) -> None:
    assert_process_isolation(when)
    from scripts import dex_update_bridge as controller_bridge

    assert executor_module.dex_update_bridge is controller_bridge, (
        f"{when}: executor.dex_update_bridge is not the controller module; "
        f"previous test on this worker={last_completed_nodeid!r}"
    )
    assert not hasattr(executor_module, "_production_authority_intact"), (
        f"{when}: _production_authority_intact was left on the executor module; "
        f"previous test on this worker={last_completed_nodeid!r}"
    )
    assert not hasattr(executor_module, "_EXECUTOR_AUTHORITY"), (
        f"{when}: _EXECUTOR_AUTHORITY was left on the executor module; "
        f"previous test on this worker={last_completed_nodeid!r}"
    )
    assert executor_module._transient_delivery_backoff is session_baseline_backoff(
        executor_module
    ), (
        f"{when}: _transient_delivery_backoff was left substituted; "
        f"previous test on this worker={last_completed_nodeid!r}"
    )
    released_name = getattr(
        executor_module, "_RELEASED_BRIDGE_MODULE_NAME", "dex_released_update_bridge"
    )
    released = sys.modules.get(released_name)
    assert released is None or released is controller_bridge, (
        f"{when}: {released_name} was left in sys.modules; "
        f"previous test on this worker={last_completed_nodeid!r}"
    )


_BACKOFF_BY_MODULE: dict[int, Any] = {}


def session_baseline_backoff(executor_module: ModuleType) -> Any:
    key = id(executor_module)
    if key not in _BACKOFF_BY_MODULE:
        _BACKOFF_BY_MODULE[key] = executor_module._transient_delivery_backoff
    return _BACKOFF_BY_MODULE[key]
