from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .report import write_report
from .runner import BenchmarkRunner, load_json, write_json
from .scoring import SCORING_VERSION, rescore_record
from .workspace import WorkspaceEvaluator, sha256_file


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_config(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def command_check(config: dict) -> int:
    evaluator = WorkspaceEvaluator(config)
    missing = evaluator.check_environment()
    if missing:
        for path in missing:
            print(f"missing: {path}")
        return 1
    print("environment: ok")
    for name in ("e_packager", "autolinker_test", "eide"):
        path = Path(config["tools"][name])
        print(f"{name}: {path} sha256={sha256_file(path)}")
    return 0


def command_report(root: Path, run_id: str, *, rescore: bool = False) -> int:
    run_root = root / "results" / run_id
    manifest_path = run_root / "manifest.json"
    manifest = load_json(manifest_path)
    record_paths = sorted((run_root / "records").glob("*.json"))
    records = [load_json(path) for path in record_paths]
    if rescore:
        records = [rescore_record(record) for record in records]
        for path, record in zip(record_paths, records, strict=True):
            write_json(path, record)
        manifest["scoring_version"] = SCORING_VERSION
        write_json(manifest_path, manifest)
    scorecard = write_report(run_root, manifest, records)
    print(json.dumps(scorecard, ensure_ascii=False, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    root = project_root()
    parser = argparse.ArgumentParser(description="易语言大模型编译基准")
    parser.add_argument("--config", type=Path, default=root / "bench.json")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("check", help="检查本地工具链")
    run_parser = subparsers.add_parser("run", help="执行基准")
    run_parser.add_argument("--run-id")
    run_parser.add_argument("--tracks", default="raw,skill")
    run_parser.add_argument("--workers", type=int)
    report_parser = subparsers.add_parser("report", help="重新生成报告")
    report_parser.add_argument("run_id")
    report_parser.add_argument("--rescore", action="store_true", help="按当前评分规则重算记录")
    args = parser.parse_args(argv)
    config = load_config(args.config)
    if args.command == "check":
        return command_check(config)
    if args.command == "report":
        return command_report(root, args.run_id, rescore=args.rescore)
    if args.command == "run":
        tracks = tuple(item.strip() for item in args.tracks.split(",") if item.strip())
        runner = BenchmarkRunner(root, config)
        workers = args.workers if args.workers is not None else int(config.get("parallel_workers", 1))
        runner.run(run_id=args.run_id, tracks=tracks, workers=workers)
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
