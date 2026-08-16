from __future__ import annotations

import dataclasses
import datetime as dt
import json
import os
import platform
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Callable

from .api import (
    AnthropicMessagesClient,
    ApiResponse,
    GeminiGenerateContentClient,
    OpenAIChatClient,
    OpenAIResponsesClient,
)
from .models import Diagnostic, StageState, Task
from .report import write_report
from .scoring import SCORING_VERSION, assign_deductions, score_state
from .workspace import (
    ContractError,
    WorkspaceEvaluator,
    build_prompt,
    parse_strict_response,
    sha256_file,
    write_source,
)


RAW_SYSTEM = """你正在参加易语言代码生成基准测试。请独立完成用户任务。
输出必须严格遵守用户给出的 JSON 契约。不要使用 Markdown 代码围栏，不要输出 JSON 之外的文字。
不要把 C、C++、C#、JavaScript 或 Python 语法混入易语言源码。"""


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)


def load_tasks(path: Path) -> list[Task]:
    data = load_json(path)
    if data.get("version") != "v1-compile":
        raise ValueError(f"unsupported dataset version: {data.get('version')}")
    tasks = [Task.from_dict(item) for item in data["tasks"]]
    ids = [task.id for task in tasks]
    if len(tasks) != 15 or len(ids) != len(set(ids)):
        raise ValueError("v1-compile must contain exactly 15 uniquely identified tasks")
    return tasks


def git_commit(path: Path) -> str | None:
    try:
        completed = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=10,
            check=False,
        )
        if completed.returncode == 0:
            return completed.stdout.decode("ascii", errors="replace").strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return None


def build_manifest(
    config: dict[str, Any],
    run_id: str,
    project_root: Path,
    parallel_workers: int,
) -> dict[str, Any]:
    tools = config["tools"]
    eide = Path(tools["eide"])
    hash_paths = {
        "e_packager": Path(tools["e_packager"]),
        "autolinker_test": Path(tools["autolinker_test"]),
        "autolinker_fne": Path(
            tools.get("autolinker_fne", eide.parent / "lib" / "AutoLinker.fne")
        ),
        "eide": eide,
    }
    template_root = Path(tools["template_root"])
    tool_hashes = {
        name: sha256_file(path) for name, path in hash_paths.items() if path.is_file()
    }
    template_hashes = {
        path.name: sha256_file(path) for path in sorted(template_root.glob("*.e"))
    }
    return {
        "run_id": run_id,
        "benchmark_version": config["benchmark_version"],
        "scoring_version": SCORING_VERSION,
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "model": config["model"],
        "reasoning_effort": config["reasoning_effort"],
        "max_output_tokens": config.get("max_output_tokens"),
        "responses_thinking_type": config.get("responses_thinking_type"),
        "protocol": config["protocol"],
        "wire_protocol": transport_protocol(config),
        "base_url": config["base_url"],
        "parallel_workers": parallel_workers,
        "runtime_available": False,
        "runtime_status": "runtime_unavailable_defender_blocked",
        "python": sys.version,
        "platform": platform.platform(),
        "tool_paths": {name: str(path) for name, path in hash_paths.items()},
        "tool_hashes": tool_hashes,
        "template_hashes": template_hashes,
        "dependency_commits": {
            "e-packager": git_commit(template_root.parent),
            "AutoLinker": git_commit(Path(tools["autolinker_test"]).parents[2]),
            "e-language-skill": git_commit(Path(tools["skill_root"])),
        },
        "dataset_sha256": sha256_file(project_root / config["dataset"]),
        "credential_persisted": False,
    }


MANIFEST_IDENTITY_FIELDS = (
    "benchmark_version",
    "scoring_version",
    "model",
    "reasoning_effort",
    "max_output_tokens",
    "responses_thinking_type",
    "protocol",
    "wire_protocol",
    "base_url",
    "parallel_workers",
    "tool_hashes",
    "template_hashes",
    "dataset_sha256",
)


def manifest_mismatches(existing: dict[str, Any], current: dict[str, Any]) -> list[str]:
    return [
        field
        for field in MANIFEST_IDENTITY_FIELDS
        if existing.get(field) != current.get(field)
    ]


def transport_protocol(config: dict[str, Any]) -> str:
    return str(config.get("responses_transport", config["protocol"]))


def system_prompt(track: str, task: Task, skill_context: dict[str, str]) -> str:
    if track == "raw":
        return RAW_SYSTEM
    sections = []
    for name in task.skill_sections:
        if name not in skill_context:
            raise KeyError(f"missing skill context section: {name}")
        sections.append(f"## {name}\n{skill_context[name]}")
    return RAW_SYSTEM + "\n\n以下是本题可使用的易语言实现规范：\n\n" + "\n\n".join(sections)


class BenchmarkRunner:
    def __init__(self, project_root: Path, config: dict[str, Any]) -> None:
        self.project_root = project_root
        self.config = config
        self.tasks = load_tasks(project_root / config["dataset"])
        context_doc = load_json(project_root / "benchmarks/v1/skill-context.json")
        self.skill_context: dict[str, str] = context_doc["sections"]
        self.evaluator = WorkspaceEvaluator(config)

    def run(
        self,
        *,
        run_id: str | None = None,
        tracks: tuple[str, ...] = ("raw", "skill"),
        workers: int = 1,
        response_provider: Callable[[str, str, Task, str], ApiResponse] | None = None,
    ) -> dict[str, Any]:
        if any(track not in {"raw", "skill"} for track in tracks):
            raise ValueError("tracks must be raw and/or skill")
        if workers < 1:
            raise ValueError("workers must be at least 1")
        missing = self.evaluator.check_environment()
        if missing:
            raise FileNotFoundError("missing benchmark dependencies: " + ", ".join(map(str, missing)))
        if run_id is None:
            run_id = dt.datetime.now().strftime("%Y%m%d-%H%M%S") + f"-{self.config['model']}"
        run_root = self.project_root / "results" / run_id
        records_dir = run_root / "records"
        cases_root = run_root / "cases"
        run_root.mkdir(parents=True, exist_ok=True)
        records_dir.mkdir(parents=True, exist_ok=True)
        cases_root.mkdir(parents=True, exist_ok=True)

        manifest_path = run_root / "manifest.json"
        current_manifest = build_manifest(self.config, run_id, self.project_root, workers)
        if manifest_path.exists():
            manifest = load_json(manifest_path)
            mismatches = manifest_mismatches(manifest, current_manifest)
            if mismatches:
                raise ValueError(
                    "resume manifest does not match the current run identity: "
                    + ", ".join(mismatches)
                )
        else:
            manifest = current_manifest
            write_json(manifest_path, manifest)

        if response_provider is None:
            api_key = os.environ.get("ELANG_BENCH_API_KEY", "")
            if not api_key:
                raise RuntimeError("ELANG_BENCH_API_KEY is required")
            client_types = {
                "openai_chat": OpenAIChatClient,
                "openai_responses": OpenAIResponsesClient,
                "anthropic_messages": AnthropicMessagesClient,
                "gemini_generate_content": GeminiGenerateContentClient,
            }
            try:
                client_type = client_types[transport_protocol(self.config)]
            except KeyError as exc:
                raise ValueError(
                    f"unsupported API transport: {transport_protocol(self.config)}"
                ) from exc
            client_args: dict[str, Any] = {
                "base_url": self.config["base_url"],
                "api_key": api_key,
                "model": self.config["model"],
                "reasoning_effort": self.config["reasoning_effort"],
                "timeout_seconds": int(self.config["request_timeout_seconds"]),
                "retry_count": int(self.config["retry_count"]),
            }
            if client_type is OpenAIResponsesClient:
                client_args["responses_thinking_type"] = self.config.get(
                    "responses_thinking_type"
                )
            if client_type is AnthropicMessagesClient:
                client_args["max_output_tokens"] = int(
                    self.config.get("max_output_tokens", 32768)
                )
            client = client_type(
                **client_args
            )
            response_provider = lambda system, user, _task, _track: client.complete(system, user)

        total = len(self.tasks) * len(tracks)
        position = 0
        pending: list[tuple[int, Task, str, Path]] = []
        for task in self.tasks:
            for track in tracks:
                position += 1
                record_path = records_dir / f"{task.id}-{track}.json"
                if record_path.exists():
                    existing = load_json(record_path)
                    existing_response = existing.get("response") or {}
                    if existing_response.get("ok"):
                        print(f"[{position}/{total}] resume {task.id} {track}", flush=True)
                        continue
                    print(f"[{position}/{total}] retry infrastructure failure {task.id} {track}", flush=True)
                print(f"[{position}/{total}] queue {task.id} {track}", flush=True)
                pending.append((position, task, track, record_path))

        worker_errors: list[str] = []
        if pending:
            with ThreadPoolExecutor(max_workers=min(workers, len(pending))) as executor:
                futures = {
                    executor.submit(
                        self._execute_case,
                        task,
                        track,
                        cases_root / f"{task.id}-{track}",
                        response_provider,
                    ): (item_position, task, track, record_path)
                    for item_position, task, track, record_path in pending
                }
                for future in as_completed(futures):
                    item_position, task, track, record_path = futures[future]
                    try:
                        record = future.result()
                    except Exception as exc:  # pragma: no cover - defensive boundary
                        message = f"{task.id}/{track}: {type(exc).__name__}: {exc}"
                        worker_errors.append(message)
                        print(f"[{item_position}/{total}] worker failed {message}", flush=True)
                        continue
                    write_json(record_path, record)
                    self._refresh_report(run_root, manifest, records_dir)
                    response = record.get("response") or {}
                    status = "done" if response.get("ok") else "api failed"
                    print(f"[{item_position}/{total}] {status} {task.id} {track}", flush=True)

        final_identity = build_manifest(self.config, run_id, self.project_root, workers)
        final_mismatches = manifest_mismatches(manifest, final_identity)
        if final_mismatches:
            raise RuntimeError(
                "benchmark toolchain or configuration changed during the run: "
                + ", ".join(final_mismatches)
            )

        records = [load_json(path) for path in sorted(records_dir.glob("*.json"))]
        scorecard = write_report(run_root, manifest, records)
        if worker_errors:
            raise RuntimeError("benchmark workers failed: " + "; ".join(worker_errors))
        if scorecard["infrastructure_failures"]:
            failures = ", ".join(
                f"{item['task_id']}/{item['track']}"
                for item in scorecard["infrastructure_failures"]
            )
            raise RuntimeError(
                f"API requests failed at {failures}; rerun with --run-id {run_id} to resume"
            )
        print(f"complete: {run_root}", flush=True)
        print(f"score: {scorecard['total_score']:.2f}", flush=True)
        return scorecard

    def _execute_case(
        self,
        task: Task,
        track: str,
        case_root: Path,
        response_provider: Callable[[str, str, Task, str], ApiResponse],
    ) -> dict[str, Any]:
        if case_root.exists():
            shutil.rmtree(case_root)
        case_root.mkdir(parents=True, exist_ok=True)
        workspace, prepare = self.evaluator.prepare(task, case_root)
        if prepare.exit_code != 0:
            state = StageState()
            state.diagnostics.append(
                Diagnostic("prepare", "template_unpack_failed", prepare.stderr or prepare.stdout)
            )
            return self._finalize_record(task, track, state, {}, None, prepare.to_dict())

        user_prompt = build_prompt(task, workspace)
        prompt_system = system_prompt(track, task, self.skill_context)
        write_json(
            case_root / "request.json",
            {"system": prompt_system, "user": user_prompt, "model": self.config["model"]},
        )
        response = response_provider(prompt_system, user_prompt, task, track)
        write_json(case_root / "api-response.json", response.to_dict())
        state = StageState()
        commands: dict[str, Any] = {"prepare": prepare.to_dict()}
        if not response.ok:
            state.diagnostics.append(
                Diagnostic("api", "api_request_failed", response.error or "API request failed")
            )
            return self._finalize_record(task, track, state, commands, response, prepare.to_dict())
        try:
            files = parse_strict_response(response.content, task.allowed_files)
            state.contract_ok = True
            state.paths_ok = True
        except ContractError as exc:
            state.diagnostics.append(Diagnostic("contract", exc.code, str(exc)))
            return self._finalize_record(task, track, state, commands, response, prepare.to_dict())
        for relative, source in files.items():
            write_source(workspace / Path(relative), source)
        state, evaluated = self.evaluator.evaluate(task, workspace, case_root)
        commands.update(evaluated)
        return self._finalize_record(task, track, state, commands, response, prepare.to_dict())

    @staticmethod
    def _finalize_record(
        task: Task,
        track: str,
        state: StageState,
        commands: dict[str, Any],
        response: ApiResponse | None,
        prepare: dict[str, Any],
    ) -> dict[str, Any]:
        score = score_state(state)
        assign_deductions(state, score)
        return {
            "task_id": task.id,
            "title": task.title,
            "category": task.category,
            "track": track,
            "response": None
            if response is None
            else {
                "ok": response.ok,
                "status": response.status,
                "elapsed_ms": response.elapsed_ms,
                "attempt_count": response.attempt_count,
                "error": response.error,
                "model": (
                    response.raw.get("model")
                    if isinstance(response.raw, dict) and isinstance(response.raw.get("model"), str)
                    else None
                ),
            },
            "state": dataclasses.asdict(state),
            "score": score,
            "commands": commands,
            "prepare": prepare,
        }

    @staticmethod
    def _refresh_report(run_root: Path, manifest: dict[str, Any], records_dir: Path) -> None:
        records = [load_json(path) for path in sorted(records_dir.glob("*.json"))]
        write_report(run_root, manifest, records)
