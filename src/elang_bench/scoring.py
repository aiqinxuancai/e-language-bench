from __future__ import annotations

import copy
import dataclasses
import re
from typing import Any

from .models import Diagnostic, StageState


SCORING_VERSION = "v1.2-compile-gated"
PACK_FAILURE_DEDUCTION = 15.0


DECLARATION_CODES = re.compile(
    r"declar|field|slot|argument|parameter|local|variable|array|quote|assignment|directive|"
    r"assembly_header|data_type|dll|constant|syntax|parenth|property|dimension",
    re.IGNORECASE,
)
FLOW_NAME_CODES = re.compile(
    r"flow|if|else|loop|judg|duplicate|name|symbol|unknown|conflict|member|call|return|"
    r"readonly|scope|type|expression|statement",
    re.IGNORECASE,
)


def _pack_failure_count(state: StageState) -> int:
    count = max(0, state.pack_failure_count)
    # Preserve the expected score for callers constructing legacy StageState values.
    if count == 0 and state.contract_ok and not state.pack_ok:
        return 1
    return count


def _format_components(state: StageState) -> dict[str, float]:
    if not state.contract_ok:
        return {
            "contract_utf8": 0.0,
            "declarations_syntax": 0.0,
            "flow_names": 0.0,
            "pack": 0.0,
            "pack_failure_attempts": 0.0,
            "roundtrip": 0.0,
            "ide_open": 0.0,
        }

    contract = 10.0 if state.paths_ok and state.utf8_ok else 5.0
    declarations = 25.0
    flow_names = 20.0
    errors = [item for item in state.diagnostics if item.severity == "error" and item.stage == "validate"]
    for item in errors:
        matched = False
        if DECLARATION_CODES.search(item.code):
            declarations -= 5.0
            matched = True
        if FLOW_NAME_CODES.search(item.code):
            flow_names -= 4.0
            matched = True
        if not matched:
            declarations -= 2.5
            flow_names -= 2.0
    if not state.validate_ok and not errors:
        declarations = 0.0
        flow_names = 0.0

    pack_failures = _pack_failure_count(state)
    # A final failed pack already loses the 15-point pack component. Earlier failed
    # attempts are deducted separately so every failed invocation costs 15 points.
    additional_pack_failures = max(0, pack_failures - (0 if state.pack_ok else 1))
    return {
        "contract_utf8": max(0.0, contract),
        "declarations_syntax": max(0.0, declarations),
        "flow_names": max(0.0, flow_names),
        "pack": PACK_FAILURE_DEDUCTION if state.pack_ok else 0.0,
        "pack_failure_attempts": -PACK_FAILURE_DEDUCTION * additional_pack_failures,
        "roundtrip": (7.5 if state.reunpack_ok else 0.0) + (7.5 if state.compare_ok else 0.0),
        "ide_open": 15.0 if state.ide_open_ok else 0.0,
    }


def score_state(state: StageState) -> dict[str, Any]:
    components = _format_components(state)
    precompile_format_score = round(max(0.0, sum(components.values())), 2)
    pack_failure_count = _pack_failure_count(state)
    compile_score = 100.0 if state.compile_ok else 0.0
    precompile_semantic_score = (
        round(100.0 * state.semantic_earned / state.semantic_total, 2)
        if state.semantic_total
        else 0.0
    )
    # Compiler rejection is definitive evidence that the Easy Language source is
    # unusable. Preserve structural diagnostics, but do not award effective format
    # or semantic credit to a sample that cannot compile.
    format_score = precompile_format_score if state.compile_ok else 0.0
    semantic_score = precompile_semantic_score if state.compile_ok else 0.0
    uncapped = 0.45 * format_score + 0.35 * compile_score + 0.20 * semantic_score

    cap = 100.0
    cap_reason: str | None = None
    if not state.contract_ok:
        cap, cap_reason = 0.0, "contract_invalid"
    elif not state.validate_ok:
        cap, cap_reason = 0.0, "validation_failed"
    elif not state.pack_ok:
        cap, cap_reason = 0.0, "pack_failed"
    elif not state.reunpack_ok or not state.compare_ok or not state.ide_open_ok:
        cap, cap_reason = 0.0, "packed_project_unusable"
    elif not state.compile_ok:
        cap, cap_reason = 0.0, "compile_failed"
    total = round(min(uncapped, cap), 2)
    passed = (
        state.contract_ok
        and state.validate_ok
        and state.pack_ok
        and state.reunpack_ok
        and state.compare_ok
        and state.ide_open_ok
        and state.compile_ok
        and state.semantic_total > 0
        and state.semantic_earned == state.semantic_total
        and pack_failure_count == 0
    )
    return {
        "scoring_version": SCORING_VERSION,
        "format_score": format_score,
        "precompile_format_score": precompile_format_score,
        "format_components": components,
        "pack_failure_count": pack_failure_count,
        "pack_failure_deduction": PACK_FAILURE_DEDUCTION * pack_failure_count,
        "compile_score": compile_score,
        "semantic_score": semantic_score,
        "precompile_semantic_score": precompile_semantic_score,
        "uncapped_total": round(uncapped, 2),
        "score_cap": cap,
        "cap_reason": cap_reason,
        "total_score": total,
        "passed": passed,
    }


def rescore_record(record: dict[str, Any]) -> dict[str, Any]:
    updated = copy.deepcopy(record)
    raw_state = updated.get("state") or {}
    diagnostics = []
    diagnostic_fields = {field.name for field in dataclasses.fields(Diagnostic)}
    for item in raw_state.get("diagnostics", []):
        if not isinstance(item, dict) or item.get("stage") == "score":
            continue
        values = {key: value for key, value in item.items() if key in diagnostic_fields}
        values["deduction"] = 0.0
        diagnostics.append(Diagnostic(**values))
    state_fields = {
        field.name
        for field in dataclasses.fields(StageState)
        if field.name != "diagnostics"
    }
    state = StageState(
        **{key: value for key, value in raw_state.items() if key in state_fields},
        diagnostics=diagnostics,
    )
    score = score_state(state)
    assign_deductions(state, score)
    updated["state"] = dataclasses.asdict(state)
    updated["score"] = score
    return updated


def assign_deductions(state: StageState, scoring: dict[str, Any]) -> None:
    validate_errors = [
        item for item in state.diagnostics if item.stage == "validate" and item.severity == "error"
    ]
    for item in validate_errors:
        deduction = 0.0
        if DECLARATION_CODES.search(item.code):
            deduction += 5.0
        if FLOW_NAME_CODES.search(item.code):
            deduction += 4.0
        item.deduction = deduction or 2.5
    stage_deductions = {
        "reunpack": 7.5,
        "revalidate": 7.5,
        "compare": 7.5,
        "ide_open": 15.0,
    }
    for item in state.diagnostics:
        if item.deduction == 0.0 and item.stage in stage_deductions:
            item.deduction = stage_deductions[item.stage]
    if scoring["pack_failure_deduction"]:
        state.diagnostics.append(
            Diagnostic(
                stage="score",
                code="pack_failure_attempts",
                message=(
                    f"{scoring['pack_failure_count']} e-packager pack attempts failed; "
                    "precompile structure deduction is "
                    f"{scoring['pack_failure_deduction']}"
                ),
                deduction=scoring["pack_failure_deduction"],
            )
        )
    if scoring["cap_reason"]:
        state.diagnostics.append(
            Diagnostic(
                stage="score",
                code=scoring["cap_reason"],
                message=f"total score capped at {scoring['score_cap']}",
                deduction=max(0.0, scoring["uncapped_total"] - scoring["total_score"]),
            )
        )
