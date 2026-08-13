"""Process-group lifecycle helpers for smoke journeys and MCP handshakes.

GitHub-hosted macOS runners (and pytest-xdist) make two syscalls unreliable:

* ``os.killpg`` on a session whose leader has already exited returns ``EPERM``
  instead of ``ESRCH`` (Darwin zombie-leader behaviour).
* ``start_new_session=True`` can itself return ``EPERM`` when the sandbox
  refuses a new session.

Neither is a product failure. Teardown must not raise, and a genuinely
unavailable isolation syscall degrades to a named skip rather than
``harness_failed``.
"""

from __future__ import annotations

import errno
import os
import signal
import subprocess
from pathlib import Path

SANDBOX_UNAVAILABLE_PREFIX = "sandbox unavailable:"

_PGREP_CANDIDATES = (Path("/usr/bin/pgrep"), Path("/bin/pgrep"))


def format_os_error(
    exc: BaseException,
    *,
    operation: str,
    path: object | None = None,
) -> str:
    """Render an OSError with errno, operation, and path instead of one collapsed line."""
    pieces = [operation]
    err = getattr(exc, "errno", None)
    if isinstance(err, int):
        name = errno.errorcode.get(err, "UNKNOWN")
        pieces.append(f"errno={err} ({name})")
    target = path if path is not None else getattr(exc, "filename", None)
    if target not in (None, ""):
        pieces.append(f"path={target}")
    else:
        pieces.append("path=<none>")
    second = getattr(exc, "filename2", None)
    if second not in (None, ""):
        pieces.append(f"path2={second}")
    if isinstance(err, int):
        try:
            pieces.append(os.strerror(err))
        except (OverflowError, ValueError):
            pieces.append(str(exc))
    else:
        pieces.append(" ".join(str(exc).split()) or type(exc).__name__)
    return " ".join(str(part) for part in pieces)


def sandbox_refused(exc: BaseException) -> bool:
    """True when a syscall returned bare EPERM with no filesystem path.

    ``PermissionError("explicit message")`` from authorization checks has
    ``errno is None`` and must not be treated as a sandbox skip. Path-bearing
    EPERM is a real access failure and stays a harness/product verdict.
    """
    if not isinstance(exc, OSError) or exc.errno != errno.EPERM:
        return False
    return getattr(exc, "filename", None) in (None, "")


def sandbox_skip_detail(exc: BaseException, *, operation: str, path: object | None = None) -> str:
    """Named skip detail for a syscall the sandbox will not perform."""
    return f"{SANDBOX_UNAVAILABLE_PREFIX} {format_os_error(exc, operation=operation, path=path)}"


def capture_process_group(process: subprocess.Popen[str]) -> int:
    """Record the session id at spawn, before the leader can be reaped."""
    return process.pid


def process_group_members(pgid: int) -> tuple[int, ...]:
    """Best-effort live members of ``pgid`` (Linux ``/proc``, else ``pgrep -g``)."""
    members = _proc_group_members(pgid)
    if members is not None:
        return members
    return _pgrep_group_members(pgid)


def terminate_process_group(
    process: subprocess.Popen[str],
    *,
    pgid: int | None = None,
    sig: int | None = None,
) -> None:
    """Stop a session started with ``start_new_session=True``.

    Never raises for the Darwin zombie-leader ``EPERM`` or for a group that
    has already vanished. Live descendants are signalled individually when
    ``killpg`` is refused.
    """
    if os.name != "posix":
        if process.poll() is not None:
            return
        process.kill()
        _wait_briefly(process)
        return

    target = pgid if pgid is not None else process.pid
    sent = sig if sig is not None else signal.SIGKILL
    try:
        os.killpg(target, sent)
    except ProcessLookupError:
        return
    except OSError:
        _kill_process_group_members(target)
        if process.poll() is None:
            try:
                process.kill()
            except OSError:
                pass
    _wait_briefly(process)


def _wait_briefly(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    try:
        process.wait(timeout=0.2)
    except subprocess.TimeoutExpired:
        pass


def _kill_process_group_members(pgid: int) -> None:
    for pid in process_group_members(pgid):
        try:
            os.kill(pid, signal.SIGKILL)
        except OSError:
            continue


def _proc_group_members(pgid: int) -> tuple[int, ...] | None:
    proc = Path("/proc")
    if not proc.is_dir():
        return None
    found: list[int] = []
    try:
        entries = list(proc.iterdir())
    except OSError:
        return ()
    for entry in entries:
        if not entry.name.isdigit():
            continue
        try:
            status = (entry / "stat").read_text(encoding="utf-8")
        except OSError:
            continue
        close = status.rfind(")")
        if close == -1:
            continue
        fields = status[close + 2 :].split()
        # After ``(comm)``: state, ppid, pgrp, ...
        if len(fields) < 3:
            continue
        try:
            group = int(fields[2])
        except ValueError:
            continue
        if group == pgid:
            found.append(int(entry.name))
    return tuple(found)


def _pgrep_group_members(pgid: int) -> tuple[int, ...]:
    executable = next((candidate for candidate in _PGREP_CANDIDATES if candidate.is_file()), None)
    if executable is None:
        return ()
    try:
        result = subprocess.run(
            [str(executable), "-g", str(pgid)],
            capture_output=True,
            text=True,
            timeout=1.0,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ()
    members: list[int] = []
    for token in result.stdout.split():
        if token.isdigit():
            members.append(int(token))
    return tuple(members)
