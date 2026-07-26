"""Reusable two-hop transport: local -> lab Windows host -> Linux GPU host.

Credential files remain external to the repository. Each contains
``user@host``, a password, and an optional work-directory hint on separate
lines. Commands for the Linux host are base64 encoded before passing through
the Windows ``cmd.exe`` shell.
"""

from __future__ import annotations

import base64
import hashlib
import posixpath
import time
from dataclasses import dataclass
from pathlib import Path

import paramiko  # type: ignore[import-untyped]


@dataclass(frozen=True)
class _Credential:
    username: str
    host: str
    password: str
    workdir: str


def _load_credential(path: Path) -> _Credential:
    if not path.exists():
        raise FileNotFoundError(f"credential file not found: {path}")
    lines = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if len(lines) < 2 or "@" not in lines[0]:
        raise ValueError("credential file requires user@host and password lines")
    username, host = lines[0].split("@", 1)
    return _Credential(
        username=username,
        host=host,
        password=lines[1],
        workdir=lines[2] if len(lines) > 2 else "",
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


class Hop:
    """Two-hop SSH session using the jump host's authorized target key."""

    def __init__(
        self,
        *,
        lab_host_file: Path,
        target_file: Path,
        timeout: int = 20,
    ) -> None:
        self.lab = _load_credential(lab_host_file)
        self.target = _load_credential(target_file)
        self._client: paramiko.SSHClient | None = None
        self._timeout = timeout

    def _jump(self) -> paramiko.SSHClient:
        if self._client is None:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                self.lab.host,
                username=self.lab.username,
                password=self.lab.password,
                look_for_keys=False,
                allow_agent=False,
                timeout=self._timeout,
            )
            self._client = client
        return self._client

    def _exec_on_lab_host(
        self,
        command: str,
        *,
        timeout: int = 60,
    ) -> tuple[int, str, str]:
        client = self._jump()
        _stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
        output = stdout.read().decode("gbk", errors="replace")
        error = stderr.read().decode("gbk", errors="replace")
        return stdout.channel.recv_exit_status(), output, error

    def run(
        self,
        remote_command: str,
        *,
        timeout: int = 300,
        quiet: bool = False,
    ) -> tuple[int, str, str]:
        """Run a Bash command on the target host."""
        payload = base64.b64encode(remote_command.encode("utf-8")).decode("ascii")
        jump_command = (
            f'ssh -o StrictHostKeyChecking=no {self.target.username}@{self.target.host} '
            f'"echo {payload} | base64 -d | bash"'
        )
        return_code, output, error = self._exec_on_lab_host(
            jump_command,
            timeout=timeout,
        )
        if not quiet:
            print(f">>> {remote_command}")
            if output:
                print(output)
            if error.strip():
                print(f"ERR: {error}")
            print(f"[exit {return_code}]")
        return return_code, output, error

    def upload(
        self,
        local_path: str | Path,
        remote_path: str,
        *,
        verify: bool = True,
    ) -> None:
        """Upload a file through the jump host and optionally verify SHA256."""
        source = Path(local_path)
        if not source.exists():
            raise FileNotFoundError(source)
        local_sha = _sha256(source)
        stage_dir = rf"C:\Users\{self.lab.username}\_hop_transfer"
        stage_path = f"{stage_dir}\\{source.name}"
        self._exec_on_lab_host(f'mkdir "{stage_dir}" 2>nul & echo ok')
        sftp = self._jump().open_sftp()
        started = time.time()
        sftp.put(str(source), stage_path)
        sftp.close()
        print(f"[upload] local -> jump: {source.name} in {time.time() - started:.1f}s")
        remote_dir = posixpath.dirname(remote_path)
        if remote_dir:
            self.run(f"mkdir -p {remote_dir}", quiet=True)
        return_code, output, error = self._exec_on_lab_host(
            f'scp -o StrictHostKeyChecking=no "{stage_path}" '
            f"{self.target.username}@{self.target.host}:{remote_path}",
            timeout=900,
        )
        self._exec_on_lab_host(f'del /f /q "{stage_path}" & echo cleaned')
        if return_code != 0:
            raise RuntimeError(f"target upload failed: {error or output}")
        if verify:
            return_code, output, _ = self.run(
                f"sha256sum {remote_path}",
                quiet=True,
            )
            remote_sha = output.split()[0] if return_code == 0 and output.strip() else ""
            if remote_sha != local_sha:
                raise RuntimeError(
                    f"upload SHA256 mismatch: local={local_sha} remote={remote_sha}"
                )
            print(f"[upload] verified SHA256 {local_sha}")

    def download(
        self,
        remote_path: str,
        local_path: str | Path,
        *,
        verify: bool = True,
    ) -> None:
        """Download a file through the jump host and optionally verify SHA256."""
        destination = Path(local_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        remote_sha = ""
        if verify:
            return_code, output, _ = self.run(
                f"sha256sum {remote_path}",
                quiet=True,
            )
            if return_code == 0 and output.strip():
                remote_sha = output.split()[0]
        stage_dir = rf"C:\Users\{self.lab.username}\_hop_transfer"
        stage_path = f"{stage_dir}\\{posixpath.basename(remote_path)}"
        self._exec_on_lab_host(f'mkdir "{stage_dir}" 2>nul & echo ok')
        return_code, output, error = self._exec_on_lab_host(
            f"scp -o StrictHostKeyChecking=no "
            f'{self.target.username}@{self.target.host}:{remote_path} "{stage_path}"',
            timeout=900,
        )
        if return_code != 0:
            raise RuntimeError(f"target download failed: {error or output}")
        sftp = self._jump().open_sftp()
        started = time.time()
        sftp.get(stage_path, str(destination))
        sftp.close()
        self._exec_on_lab_host(f'del /f /q "{stage_path}" & echo cleaned')
        print(f"[download] jump -> local: {destination.name} in {time.time() - started:.1f}s")
        if remote_sha:
            local_sha = _sha256(destination)
            if local_sha != remote_sha:
                raise RuntimeError(
                    f"download SHA256 mismatch: remote={remote_sha} local={local_sha}"
                )
            print(f"[download] verified SHA256 {local_sha}")

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None

    def __enter__(self) -> Hop:
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()
