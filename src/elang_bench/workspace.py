from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import tempfile
import time
from pathlib import Path, PurePosixPath
from typing import Any

from .models import CommandResult, Diagnostic, StageState, Task


FAILURE_MARKERS = (
    "编译失败",
    "连接失败",
    "链接失败",
    "静态连接失败",
    "静态链接失败",
    "打开可执行文件失败",
    "程序代码编译失败",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def decode_output(data: bytes) -> str:
    if not data:
        return ""
    for encoding in ("utf-8-sig", "gb18030"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def run_command(
    argv: list[str],
    timeout_seconds: int,
    cwd: Path | None = None,
    env_overrides: dict[str, str] | None = None,
) -> CommandResult:
    started = time.monotonic()
    safe_argv = [str(item) for item in argv]
    environment = os.environ.copy()
    if env_overrides:
        environment.update(env_overrides)
    try:
        completed = subprocess.run(
            safe_argv,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_seconds,
            check=False,
            env=environment,
        )
        return CommandResult(
            argv=safe_argv,
            exit_code=completed.returncode,
            stdout=decode_output(completed.stdout),
            stderr=decode_output(completed.stderr),
            elapsed_ms=int((time.monotonic() - started) * 1000),
        )
    except subprocess.TimeoutExpired as exc:
        return CommandResult(
            argv=safe_argv,
            exit_code=None,
            stdout=decode_output(exc.stdout or b""),
            stderr=decode_output(exc.stderr or b""),
            elapsed_ms=int((time.monotonic() - started) * 1000),
            timed_out=True,
        )


def compile_temp_directory(case_root: Path) -> Path:
    identity = hashlib.sha256(str(case_root.resolve()).encode("utf-8")).hexdigest()[:24]
    return Path(tempfile.gettempdir()) / "e-language-bench" / "compile" / identity


class ContractError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def parse_strict_response(content: str, allowed_files: tuple[str, ...]) -> dict[str, str]:
    if content.startswith("\ufeff"):
        raise ContractError("json_bom", "response begins with a UTF-8 BOM")
    if content.startswith("```") or "```" in content:
        raise ContractError("markdown_fence", "Markdown code fences are forbidden")
    try:
        value = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ContractError("invalid_json", f"line {exc.lineno}, column {exc.colno}: {exc.msg}") from exc
    if not isinstance(value, dict):
        raise ContractError("json_not_object", "top-level response must be an object")
    expected_keys = {"files", "explanation", "expected_behavior"}
    actual_keys = set(value)
    if actual_keys != expected_keys:
        raise ContractError(
            "json_fields",
            f"expected fields {sorted(expected_keys)}, got {sorted(actual_keys)}",
        )
    if not isinstance(value["files"], dict):
        raise ContractError("files_not_object", "files must be a path-to-content object")
    if not isinstance(value["explanation"], str) or not isinstance(value["expected_behavior"], str):
        raise ContractError("metadata_not_string", "explanation and expected_behavior must be strings")
    if set(value["files"]) != set(allowed_files):
        raise ContractError(
            "file_set_mismatch",
            f"expected exactly {sorted(allowed_files)}, got {sorted(value['files'])}",
        )
    result: dict[str, str] = {}
    for raw_path, source in value["files"].items():
        if not isinstance(raw_path, str) or not isinstance(source, str):
            raise ContractError("file_type", "file paths and contents must be strings")
        path = PurePosixPath(raw_path)
        if path.is_absolute() or ".." in path.parts or not raw_path.startswith("src/"):
            raise ContractError("unsafe_path", f"unsafe file path: {raw_path}")
        if path.suffix.lower() != ".txt":
            raise ContractError("unsupported_file", f"only src/*.txt is writable: {raw_path}")
        if "\x00" in source:
            raise ContractError("nul_byte", f"source contains NUL: {raw_path}")
        result[raw_path] = source
    return result


def write_source(path: Path, source: str) -> None:
    normalized = source.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "\r\n")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(normalized, encoding="utf-8-sig", newline="")


def read_source(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def build_prompt(task: Task, workspace: Path) -> str:
    chunks = [
        f"任务编号：{task.id}",
        f"任务名称：{task.title}",
        task.prompt.strip(),
        "",
        "请返回修改后的完整文件内容。只能修改下面列出的文件，且 files 必须恰好包含全部路径。",
    ]
    for relative in task.allowed_files:
        path = workspace / Path(relative)
        content = read_source(path) if path.exists() else "（新文件，当前不存在）"
        chunks.extend(["", f"--- {relative} ---", content, f"--- end {relative} ---"])
    chunks.extend(
        [
            "",
            "输出必须是单个 JSON 对象，不要使用 Markdown 代码围栏或添加 JSON 外文字。",
            '格式：{"files":{"src/文件.txt":"完整源码"},"explanation":"简短说明","expected_behavior":"预期行为"}',
        ]
    )
    return "\n".join(chunks)


def parse_preflight_diagnostics(result: CommandResult, stage: str = "validate") -> list[Diagnostic]:
    text = result.stdout + "\n" + result.stderr
    pattern = re.compile(
        r"source_preflight_(error|warning): file=(.*?), line=(\d+), code=([^,\r\n]+)(?:, detail=([^\r\n]*))?"
    )
    diagnostics: list[Diagnostic] = []
    seen: set[tuple[str, str, int]] = set()
    for match in pattern.finditer(text):
        severity, file, line_text, code, detail = match.groups()
        key = (code.strip(), file.strip(), int(line_text))
        if key in seen:
            continue
        seen.add(key)
        diagnostics.append(
            Diagnostic(
                stage=stage,
                code=code.strip(),
                message=(detail or code).strip(),
                severity=severity,
                file=file.strip(),
                line=int(line_text),
            )
        )
    if result.exit_code not in (0, None) and not diagnostics:
        message = (result.stderr or result.stdout or "command failed").strip()[:2000]
        diagnostics.append(Diagnostic(stage, f"{stage}_failed", message))
    if result.timed_out:
        diagnostics.append(Diagnostic(stage, f"{stage}_timeout", "command timed out"))
    return diagnostics


def evaluate_semantics(task: Task, workspace: Path) -> tuple[int, int, list[dict[str, Any]]]:
    earned = 0
    total = sum(check.points for check in task.checks)
    details: list[dict[str, Any]] = []
    for check in task.checks:
        path = workspace / Path(check.file)
        source = read_source(path) if path.exists() else ""
        flags = 0
        if "i" in check.flags:
            flags |= re.IGNORECASE
        if "m" in check.flags:
            flags |= re.MULTILINE
        if "s" in check.flags:
            flags |= re.DOTALL
        passed = False
        if check.kind == "regex":
            passed = re.search(check.value, source, flags) is not None
        elif check.kind == "not_regex":
            passed = re.search(check.value, source, flags) is None
        elif check.kind == "contains":
            passed = check.value in source
        elif check.kind == "not_contains":
            passed = check.value not in source
        elif check.kind == "count_regex":
            pattern, expected = check.value.rsplit("::", 1)
            passed = len(re.findall(pattern, source, flags)) == int(expected)
        if passed:
            earned += check.points
        details.append({"name": check.name, "passed": passed, "points": check.points})
    return earned, total, details


class WorkspaceEvaluator:
    def __init__(self, config: dict[str, Any]) -> None:
        tools = config["tools"]
        self.e_packager = Path(tools["e_packager"])
        self.template_root = Path(tools["template_root"])
        self.blackmoon_x86_dir = Path(tools["blackmoon_x86_dir"]) if tools.get("blackmoon_x86_dir") else None
        self.temp_root = Path(config.get("temp_root", ".temp"))
        self.compile_timeout = int(config.get("compile_timeout_seconds", 120))

    def check_environment(self) -> list[Path]:
        paths = [self.e_packager, self.template_root]
        if self.blackmoon_x86_dir:
            paths.append(self.blackmoon_x86_dir)
        missing = [path for path in paths if not path.exists()]
        if not missing:
            version = run_command([str(self.e_packager), "--version"], 15)
            if version.exit_code != 0 or version.timed_out or version.stdout.strip() not in {
                "e-packager v1.2.7", "e-packager dev"
            }:
                raise ValueError(
                    "V2 requires e-packager v1.2.7; got: "
                    + (version.stdout or version.stderr or "no version output").strip()
                )
        return missing

    def prepare(self, task: Task, case_root: Path) -> tuple[Path, CommandResult]:
        workspace = case_root / "workspace"
        template = self.template_root / "e-console-exe-new-proj.e"
        result = run_command(
            [str(self.e_packager), "unpack", str(template), str(workspace), "--main-only"],
            60,
        )
        return workspace, result

    def evaluate(self, task: Task, workspace: Path, case_root: Path) -> tuple[StageState, dict[str, Any]]:
        state = StageState(contract_ok=True, paths_ok=True)
        commands: dict[str, Any] = {}

        validate = run_command([str(self.e_packager), "validate", str(workspace)], 60)
        commands["validate"] = validate.to_dict()
        state.diagnostics.extend(parse_preflight_diagnostics(validate))
        state.validate_ok = validate.exit_code == 0 and not any(
            item.severity == "error" and item.stage == "validate" for item in state.diagnostics
        )

        packed = case_root / "candidate.e"
        state.pack_attempt_count += 1
        pack = run_command([str(self.e_packager), "pack", str(workspace), str(packed)], 90)
        commands["pack"] = pack.to_dict()
        state.pack_ok = pack.exit_code == 0 and packed.exists() and packed.stat().st_size > 0
        if not state.pack_ok:
            state.pack_failure_count += 1
            state.diagnostics.extend(parse_preflight_diagnostics(pack, "pack"))

        reunpacked = case_root / "reunpacked"
        if state.pack_ok:
            reunpack = run_command(
                [str(self.e_packager), "unpack", str(packed), str(reunpacked), "--main-only"],
                90,
            )
            commands["reunpack"] = reunpack.to_dict()
            revalidate = run_command([str(self.e_packager), "validate", str(reunpacked)], 60)
            commands["revalidate"] = revalidate.to_dict()
            state.reunpack_ok = reunpack.exit_code == 0 and revalidate.exit_code == 0
            if not state.reunpack_ok:
                state.diagnostics.extend(parse_preflight_diagnostics(reunpack, "reunpack"))
                state.diagnostics.extend(parse_preflight_diagnostics(revalidate, "revalidate"))

            compare = run_command(
                [str(self.e_packager), "compare-bundle", str(packed), str(workspace)],
                90,
            )
            commands["compare"] = compare.to_dict()
            state.compare_ok = compare.exit_code == 0
            if not state.compare_ok:
                state.diagnostics.append(
                    Diagnostic("compare", "bundle_mismatch", (compare.stderr or compare.stdout).strip()[:2000])
                )

        if state.pack_ok:
            self.temp_root.mkdir(parents=True, exist_ok=True)
            # e-packager writes companion .cpp/.obj/.res files next to the EXE.
            # Include the case identity so concurrent model runs cannot collide.
            case_identity = hashlib.sha256(str(case_root.resolve()).encode("utf-8")).hexdigest()[:16]
            artifact = self.temp_root / f"{case_root.name}-{case_identity}.exe"
            compile_argv = [str(self.e_packager), "compile", str(workspace), str(artifact),
                            "--arch", "x86", "--subsystem", "console"]
            if self.blackmoon_x86_dir:
                compile_argv.extend(["--blackmoon-x86-dir", str(self.blackmoon_x86_dir)])
            compile = run_command(
                compile_argv,
                self.compile_timeout + 60,
            )
            commands["compile"] = compile.to_dict()
            state.compile_ok = compile.exit_code == 0 and artifact.is_file() and artifact.stat().st_size > 0
            state.compile_tool_ok = state.compile_ok
            commands["compile_result"] = {"ok": state.compile_ok, "artifact": str(artifact),
                                           "output_file_exists": artifact.is_file(),
                                           "compiler": "e-packager compile"}
            if not state.compile_ok:
                state.diagnostics.extend(parse_preflight_diagnostics(compile, "compile"))

        state.semantic_earned, state.semantic_total, semantic_details = evaluate_semantics(task, workspace)
        commands["semantic_checks"] = semantic_details
        return state, commands
