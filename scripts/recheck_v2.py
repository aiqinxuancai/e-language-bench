from __future__ import annotations

import argparse
import copy
import datetime as dt
import json
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from elang_bench.report import write_report
from elang_bench.runner import build_manifest, load_json, load_tasks, write_json
from elang_bench.scoring import SCORING_VERSION, assign_deductions, score_state
from elang_bench.models import Diagnostic, StageState
from elang_bench.workspace import WorkspaceEvaluator, sha256_file


def current_toolchain(config: dict) -> tuple[str, str | None]:
    tool = Path(config["tools"]["e_packager"])
    commit = None
    try:
        completed = subprocess.run(
            ["git", "-C", str(Path(config["tools"]["template_root"]).parent), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode == 0:
            commit = completed.stdout.strip()
    except OSError:
        pass
    return sha256_file(tool), commit


def copy_workspace_sources(source: Path, destination: Path, allowed_files: tuple[str, ...]) -> None:
    for relative in allowed_files:
        source_file = source / Path(relative)
        destination_file = destination / Path(relative)
        if not source_file.is_file():
            raise FileNotFoundError(f"missing source file: {source_file}")
        destination_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_file, destination_file)


def rebuild_record(
    source_run: Path,
    destination_run: Path,
    record: dict,
    tasks: dict,
    evaluator: WorkspaceEvaluator,
) -> dict:
    updated = copy.deepcopy(record)
    response = record.get("response") or {}
    task = tasks[record["task_id"]]
    if record.get("track") != "raw" or not response.get("ok") or not (record.get("state") or {}).get("contract_ok"):
        return updated

    source_case = source_run / "cases" / f"{record['task_id']}-{record['track']}"
    source_workspace = source_case / "workspace"
    if not source_workspace.is_dir():
        updated.setdefault("state", {})["diagnostics"] = [
            Diagnostic("recheck", "workspace_missing", str(source_workspace)).to_dict()
        ]
        return updated

    case_root = destination_run / "cases" / f"{record['task_id']}-{record['track']}"
    if case_root.exists():
        shutil.rmtree(case_root)
    case_root.mkdir(parents=True, exist_ok=True)
    workspace, prepare = evaluator.prepare(task, case_root)
    if prepare.exit_code != 0:
        state = StageState(contract_ok=True, paths_ok=True)
        state.diagnostics.append(Diagnostic("prepare", "template_unpack_failed", prepare.stderr or prepare.stdout))
        score = score_state(state)
        assign_deductions(state, score)
        updated["state"] = state_to_json(state)
        updated["score"] = score
        updated["commands"] = {"prepare": prepare.to_dict()}
        return updated

    copy_workspace_sources(source_workspace, workspace, task.allowed_files)
    for filename in ("request.json", "api-response.json"):
        original = source_case / filename
        if original.is_file():
            shutil.copy2(original, case_root / filename)
    state = StageState(
        contract_ok=True,
        utf8_ok=bool((record.get("state") or {}).get("utf8_ok", True)),
        paths_ok=True,
    )
    state, commands = evaluator.evaluate(task, workspace, case_root)
    score = score_state(state)
    assign_deductions(state, score)
    updated["state"] = state_to_json(state)
    updated["score"] = score
    updated["commands"] = {"prepare": prepare.to_dict(), **commands}
    updated["rechecked_with"] = "current e-packager toolchain"
    return updated


def state_to_json(state: StageState) -> dict:
    return {
        "contract_ok": state.contract_ok,
        "utf8_ok": state.utf8_ok,
        "paths_ok": state.paths_ok,
        "validate_ok": state.validate_ok,
        "pack_attempt_count": state.pack_attempt_count,
        "pack_failure_count": state.pack_failure_count,
        "pack_ok": state.pack_ok,
        "reunpack_ok": state.reunpack_ok,
        "compare_ok": state.compare_ok,
        "compile_tool_ok": state.compile_tool_ok,
        "compile_ok": state.compile_ok,
        "semantic_earned": state.semantic_earned,
        "semantic_total": state.semantic_total,
        "diagnostics": [item.to_dict() for item in state.diagnostics],
    }


def recheck_run(source_run: Path, config: dict, tasks: dict, workers: int, stamp: str) -> Path:
    destination_run = ROOT / "results" / f"{stamp}-recheck-{source_run.name[9:]}"
    if destination_run.exists():
        raise FileExistsError(destination_run)
    destination_run.mkdir(parents=True)
    (destination_run / "records").mkdir()
    (destination_run / "cases").mkdir()

    source_manifest = load_json(source_run / "manifest.json")
    manifest = copy.deepcopy(source_manifest)
    manifest.update(
        {
            "run_id": destination_run.name,
            "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "e_packager_version": "1.2.7",
            "scoring_version": SCORING_VERSION,
            "rechecked_from": source_run.name,
            "parallel_workers": workers,
        }
    )
    tool_hash, commit = current_toolchain(config)
    manifest["tool_paths"] = {"e_packager": config["tools"]["e_packager"]}
    manifest["tool_hashes"] = {"e_packager": tool_hash}
    manifest["dependency_commits"] = {"e-packager": commit}
    write_json(destination_run / "manifest.json", manifest)

    evaluator = WorkspaceEvaluator(config)
    records = [load_json(path) for path in sorted((source_run / "records").glob("*.json"))]
    output: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=min(workers, max(1, len(records)))) as executor:
        futures = {
            executor.submit(rebuild_record, source_run, destination_run, record, tasks, evaluator): record
            for record in records
        }
        for future in as_completed(futures):
            record = futures[future]
            updated = future.result()
            output[f"{record['task_id']}-{record['track']}.json"] = updated
            print(f"{source_run.name}: rechecked {record['task_id']}", flush=True)
    for filename, record in sorted(output.items()):
        write_json(destination_run / "records" / filename, record)
    final_records = [load_json(path) for path in sorted((destination_run / "records").glob("*.json"))]
    write_report(destination_run, manifest, final_records)
    return destination_run


def main() -> int:
    parser = argparse.ArgumentParser(description="Re-run V2 toolchain evaluation for existing model responses")
    parser.add_argument("--config", type=Path, default=ROOT / "config" / "bench.json")
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--stamp", default=dt.datetime.now().strftime("%Y%m%d"))
    parser.add_argument("--run", action="append", help="source run id; defaults to all 20260909-*v2 runs")
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8-sig"))
    if config.get("benchmark_version") != "v2-compile":
        raise SystemExit("V2 configuration required")
    evaluator = WorkspaceEvaluator(config)
    missing = evaluator.check_environment()
    if missing:
        raise SystemExit("missing dependencies: " + ", ".join(map(str, missing)))
    tasks = {task.id: task for task in load_tasks(ROOT / config["dataset"]) }
    source_ids = args.run or sorted(path.name for path in (ROOT / "results").glob("20260909-*v2") if path.is_dir())
    for source_id in source_ids:
        recheck_run(ROOT / "results" / source_id, config, tasks, args.workers, args.stamp)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
