"""Run the benchmark directly from a local configuration file."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from elang_bench.cli import main as cli_main  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="易语言基准一键入口")
    parser.add_argument(
        "config",
        nargs="?",
        type=Path,
        default=ROOT / "config" / "bench.json",
        help="配置文件，默认 config/bench.json",
    )
    parser.add_argument("--check", action="store_true", help="只检查本地工具链")
    parser.add_argument("--run-id")
    parser.add_argument("--tracks", choices=("raw",), default="raw")
    parser.add_argument("--workers", type=int)
    parser.add_argument("--model")
    parser.add_argument("--base-url")
    parser.add_argument("--protocol")
    parser.add_argument("--reasoning-effort")
    args = parser.parse_args(argv)

    command = "check" if args.check else "run"
    forwarded = ["--config", str(args.config)]
    for name in ("model", "base_url", "protocol", "reasoning_effort"):
        value = getattr(args, name)
        if value is not None:
            forwarded.extend([f"--{name.replace('_', '-')}", value])
    forwarded.append(command)
    if command == "run":
        forwarded.extend(["--tracks", args.tracks])
        if args.run_id:
            forwarded.extend(["--run-id", args.run_id])
        if args.workers is not None:
            forwarded.extend(["--workers", str(args.workers)])
    return cli_main(forwarded)


if __name__ == "__main__":
    raise SystemExit(main())
