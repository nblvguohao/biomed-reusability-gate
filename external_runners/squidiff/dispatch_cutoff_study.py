"""Package, dispatch, monitor, and retrieve cutoff studies on the lab A100s."""

from __future__ import annotations

import argparse
import hashlib
import json
import shlex
import subprocess
import sys
import tarfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "remote"))

from lab_a100_hop import Hop  # noqa: E402

REMOTE_ROOT = "/data/lgh/reusability_report_nmi_20260727"
DEFAULT_DATA = (
    REPO
    / "artifacts"
    / "squidiff_tier0_gpu"
    / "source_data"
    / "gse190976_combined.h5ad"
)
STAGING = REPO / "remote_staging"
REMOTE_BASE_PYTHON = "/home/user/miniconda3/envs/gc-nkgraph/bin/python"


def validate_remote_root(path: str) -> bool:
    """Reject broad or non-project-scoped remote destinations."""
    normalized = path.rstrip("/")
    if not normalized.startswith("/data/lgh/"):
        raise ValueError("remote root must be a project directory below /data/lgh")
    relative = normalized.removeprefix("/data/lgh/")
    if not relative or "/" in relative or len(relative) < 12:
        raise ValueError("remote root is not sufficiently project-scoped")
    return True


def build_remote_manifest(
    commit: str,
    archive_sha256: str,
    cutoffs: list[str] | tuple[str, ...],
) -> dict[str, Any]:
    """Build a provenance manifest without connection or credential fields."""
    validate_remote_root(REMOTE_ROOT)
    return {
        "git_commit": commit,
        "source_archive_sha256": archive_sha256,
        "cutoffs": list(cutoffs),
        "remote_root": REMOTE_ROOT,
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git_commit() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def create_source_archive(cutoffs: tuple[str, ...]) -> tuple[Path, Path]:
    """Archive the committed source tree and write its credential-free manifest."""
    STAGING.mkdir(parents=True, exist_ok=True)
    archive = STAGING / "reusability_report_source.tar.gz"
    subprocess.run(
        ["git", "archive", "--format=tar.gz", f"--output={archive}", "HEAD"],
        cwd=REPO,
        check=True,
    )
    manifest = build_remote_manifest(_git_commit(), _sha256(archive), cutoffs)
    manifest_path = STAGING / "remote_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return archive, manifest_path


def launch_commands(cutoffs: tuple[str, ...]) -> list[str]:
    """Return one background cutoff command per GPU."""
    validate_remote_root(REMOTE_ROOT)
    commands = []
    for gpu, cutoff in enumerate(cutoffs):
        if gpu > 1:
            raise ValueError("at most two cutoff workers can be launched on this host")
        log = f"{REMOTE_ROOT}/logs/{cutoff}.log"
        pid = f"{REMOTE_ROOT}/logs/{cutoff}.pid"
        python = f"{REMOTE_ROOT}/venv/bin/python"
        runner = f"{REMOTE_ROOT}/repo/external_runners/squidiff/cutoff_study.py"
        config = f"{REMOTE_ROOT}/repo/configs/cutoff_studies.yaml"
        data = f"{REMOTE_ROOT}/input/gse190976_combined.h5ad"
        output = f"{REMOTE_ROOT}/results/{cutoff}"
        inner = (
            "set -euo pipefail; "
            f"export CUDA_VISIBLE_DEVICES={gpu}; "
            f"export PYTHONPATH={REMOTE_ROOT}/repo/src:"
            f"{REMOTE_ROOT}/repo/vendor/Squidiff:"
            f"{REMOTE_ROOT}/repo/external_runners/squidiff; "
            f"{python} -u {runner} --config {config} --name {cutoff} "
            f"--data {data} --output {output}"
        )
        commands.append(
            f"mkdir -p {REMOTE_ROOT}/logs {REMOTE_ROOT}/results; "
            f"nohup bash -lc {shlex.quote(inner)} > {log} 2>&1 < /dev/null & "
            f"echo $! > {pid}; cat {pid}"
        )
    return commands


def _hop(args: argparse.Namespace) -> Hop:
    return Hop(
        lab_host_file=args.lab_host,
        target_file=args.target,
        timeout=args.connect_timeout,
    )


def check(args: argparse.Namespace) -> None:
    """Run a read-only hardware and software preflight."""
    with _hop(args) as hop:
        commands = (
            "whoami && hostname && uname -a",
            "nvidia-smi --query-gpu=name,memory.total,memory.free,driver_version "
            "--format=csv,noheader",
            "df -h /data && free -h",
            "python3 --version && python3 -m pip --version || true",
            f"{REMOTE_BASE_PYTHON} -c \"import sys, torch; "
            "print(sys.version.split()[0]); "
            "print('torch', torch.__version__, 'cuda', torch.cuda.is_available(), "
            "torch.version.cuda)\"",
        )
        for command in commands:
            return_code, _, _ = hop.run(command, timeout=120)
            if return_code != 0:
                raise RuntimeError(f"preflight command failed: {command}")


def launch(args: argparse.Namespace) -> None:
    """Upload committed code/data, create an environment, and start GPU workers."""
    cutoffs = tuple(args.cutoffs)
    archive, manifest = create_source_archive(cutoffs)
    validate_remote_root(REMOTE_ROOT)
    with _hop(args) as hop:
        hop.run(
            f"mkdir -p {REMOTE_ROOT}/repo {REMOTE_ROOT}/input "
            f"{REMOTE_ROOT}/logs {REMOTE_ROOT}/results",
            timeout=120,
        )
        hop.upload(archive, f"{REMOTE_ROOT}/{archive.name}")
        hop.upload(manifest, f"{REMOTE_ROOT}/{manifest.name}")
        hop.upload(args.data, f"{REMOTE_ROOT}/input/gse190976_combined.h5ad")
        setup = (
            f"tar -xzf {REMOTE_ROOT}/{archive.name} -C {REMOTE_ROOT}/repo && "
            f"{REMOTE_BASE_PYTHON} -m venv --system-site-packages {REMOTE_ROOT}/venv && "
            f"{REMOTE_ROOT}/venv/bin/python -m pip install --upgrade pip && "
            f"{REMOTE_ROOT}/venv/bin/python -m pip install -e {REMOTE_ROOT}/repo"
        )
        return_code, _, _ = hop.run(setup, timeout=3600)
        if return_code != 0:
            raise RuntimeError("remote environment setup failed")
        for command in launch_commands(cutoffs):
            return_code, _, _ = hop.run(command, timeout=120)
            if return_code != 0:
                raise RuntimeError("remote cutoff launch failed")


def status(args: argparse.Namespace) -> None:
    """Report worker state and completed seed counts."""
    with _hop(args) as hop:
        for cutoff in args.cutoffs:
            command = (
                f"cutoff={shlex.quote(cutoff)}; "
                f"pidfile={REMOTE_ROOT}/logs/$cutoff.pid; "
                "if [ -f \"$pidfile\" ]; then pid=$(cat \"$pidfile\"); "
                "if kill -0 \"$pid\" 2>/dev/null; then state=RUNNING; else state=EXITED; fi; "
                "else pid=none; state=NOT_LAUNCHED; fi; "
                f"done_count=$(find {REMOTE_ROOT}/results/$cutoff -path "
                "'*/seed_*/metrics.json' -type f 2>/dev/null | wc -l); "
                "echo \"$cutoff state=$state pid=$pid completed_seeds=$done_count\"; "
                f"tail -n 12 {REMOTE_ROOT}/logs/$cutoff.log 2>/dev/null || true"
            )
            hop.run(command, timeout=120)


def _safe_extract(archive: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    resolved_destination = destination.resolve()
    with tarfile.open(archive, "r:gz") as handle:
        for member in handle.getmembers():
            target = (destination / member.name).resolve()
            if resolved_destination not in target.parents and target != resolved_destination:
                raise ValueError(f"unsafe archive member: {member.name}")
        handle.extractall(destination)


def retrieve(args: argparse.Namespace) -> None:
    """Create compact result archives remotely, download, and verify them."""
    STAGING.mkdir(parents=True, exist_ok=True)
    local_root = REPO / "artifacts" / "cutoff_studies"
    with _hop(args) as hop:
        for cutoff in args.cutoffs:
            remote_archive = f"{REMOTE_ROOT}/retrieval_{cutoff}.tar.gz"
            command = (
                f"tar --exclude='*/training_logs/opt*.pt' "
                f"--exclude='*/training_logs/model*.pt' "
                f"-czf {remote_archive} -C {REMOTE_ROOT}/results {shlex.quote(cutoff)}"
            )
            return_code, _, _ = hop.run(command, timeout=900)
            if return_code != 0:
                raise RuntimeError(f"could not archive remote cutoff: {cutoff}")
            local_archive = STAGING / f"retrieval_{cutoff}.tar.gz"
            hop.download(remote_archive, local_archive)
            _safe_extract(local_archive, local_root)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lab-host", type=Path, required=True)
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--connect-timeout", type=int, default=20)
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("check")
    launch_parser = subparsers.add_parser("launch")
    launch_parser.add_argument(
        "--cutoffs",
        nargs="+",
        default=["early_d14", "late_d28"],
    )
    launch_parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    for name in ("status", "retrieve"):
        child = subparsers.add_parser(name)
        child.add_argument(
            "--cutoffs",
            nargs="+",
            default=["early_d14", "late_d28"],
        )
    return parser


def main() -> None:
    args = _parser().parse_args()
    {"check": check, "launch": launch, "status": status, "retrieve": retrieve}[
        args.command
    ](args)


if __name__ == "__main__":
    main()
