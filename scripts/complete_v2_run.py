from __future__ import annotations

import argparse
import copy
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from elang_bench.runner import BenchmarkRunner, build_manifest, load_json, load_tasks, write_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Retry failed API records, then recheck with current toolchain")
    parser.add_argument("source_run")
    parser.add_argument("--api-key", required=True)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()

    source = ROOT / "results" / args.source_run
    destination = ROOT / "results" / args.run_id
    if destination.exists():
        raise SystemExit(f"destination already exists: {destination}")
    source_manifest = load_json(source / "manifest.json")
    base_config = load_json(ROOT / "config" / "bench.json")
    config = {
        **base_config,
        "benchmark_version": source_manifest["benchmark_version"],
        "base_url": source_manifest["base_url"],
        "protocol": source_manifest["protocol"],
        "model": source_manifest["model"],
        "reasoning_effort": source_manifest["reasoning_effort"],
        "parallel_workers": args.workers,
        "responses_thinking_type": source_manifest.get("responses_thinking_type"),
        "responses_streaming": source_manifest.get("responses_streaming", False),
        "max_output_tokens": source_manifest.get("max_output_tokens"),
    }
    destination.mkdir(parents=True)
    shutil.copytree(source / "records", destination / "records")
    shutil.copytree(source / "cases", destination / "cases")
    write_json(destination / "manifest.json", build_manifest(config, args.run_id, ROOT, args.workers))

    import os

    os.environ["ELANG_BENCH_API_KEY"] = args.api_key
    runner = BenchmarkRunner(ROOT, config)
    runner.run(run_id=args.run_id, tracks=("raw",), workers=args.workers)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
