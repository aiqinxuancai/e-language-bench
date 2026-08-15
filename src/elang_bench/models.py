from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Check:
    name: str
    file: str
    kind: str
    value: str
    points: int
    flags: str = ""


@dataclass(frozen=True)
class Task:
    id: str
    title: str
    category: str
    template: str
    prompt: str
    allowed_files: tuple[str, ...]
    skill_sections: tuple[str, ...]
    checks: tuple[Check, ...]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Task":
        return cls(
            id=data["id"],
            title=data["title"],
            category=data["category"],
            template=data.get("template", "e-console-exe-new-proj.e"),
            prompt=data["prompt"],
            allowed_files=tuple(data["allowed_files"]),
            skill_sections=tuple(data.get("skill_sections", [])),
            checks=tuple(Check(**item) for item in data.get("checks", [])),
        )


@dataclass
class CommandResult:
    argv: list[str]
    exit_code: int | None
    stdout: str = ""
    stderr: str = ""
    elapsed_ms: int = 0
    timed_out: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "argv": self.argv,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "elapsed_ms": self.elapsed_ms,
            "timed_out": self.timed_out,
        }


@dataclass
class Diagnostic:
    stage: str
    code: str
    message: str
    severity: str = "error"
    file: str | None = None
    line: int | None = None
    deduction: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class StageState:
    contract_ok: bool = False
    utf8_ok: bool = True
    paths_ok: bool = False
    validate_ok: bool = False
    pack_attempt_count: int = 0
    pack_failure_count: int = 0
    pack_ok: bool = False
    reunpack_ok: bool = False
    compare_ok: bool = False
    ide_open_ok: bool = False
    compile_ok: bool = False
    semantic_earned: int = 0
    semantic_total: int = 0
    diagnostics: list[Diagnostic] = field(default_factory=list)


@dataclass
class RunPaths:
    root: Path
    records: Path
    artifacts: Path
