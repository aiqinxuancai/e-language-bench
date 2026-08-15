from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


CATEGORY_LABELS = {
    "format": "格式与工程",
    "core": "核心库指令",
    "flow": "流程控制",
    "abstraction": "子程序与数据结构",
    "repair": "修复与综合",
}


def _pack_counts(record: dict[str, Any]) -> tuple[int, int]:
    state = record.get("state") or {}
    failures = state.get("pack_failure_count")
    if failures is None:
        failures = int(bool(state.get("contract_ok") and not state.get("pack_ok")))
    attempts = state.get("pack_attempt_count")
    if attempts is None:
        attempts = failures + int(bool(state.get("pack_ok")))
    return max(0, int(attempts)), max(0, int(failures))


def summarize(records: list[dict[str, Any]], manifest: dict[str, Any]) -> dict[str, Any]:
    valid = [
        item
        for item in records
        if item.get("score") and (item.get("response") or {}).get("ok")
    ]
    infrastructure_failures = [
        {
            "task_id": item.get("task_id"),
            "track": item.get("track"),
            "status": (item.get("response") or {}).get("status"),
            "error": (item.get("response") or {}).get("error"),
        }
        for item in records
        if item.get("response") and not item["response"].get("ok")
    ]
    tracks: dict[str, list[dict[str, Any]]] = defaultdict(list)
    categories: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in valid:
        tracks[record["track"]].append(record)
        categories[record["category"]].append(record)

    track_scores: dict[str, Any] = {}
    for track, items in tracks.items():
        pack_attempts = sum(_pack_counts(item)[0] for item in items)
        pack_failures = sum(_pack_counts(item)[1] for item in items)
        track_scores[track] = {
            "score": round(mean(item["score"]["total_score"] for item in items), 2),
            "format_score": round(mean(item["score"]["format_score"] for item in items), 2),
            "compile_rate": round(sum(item["state"]["compile_ok"] for item in items) / len(items), 4),
            "pass_at_1": round(sum(item["score"]["passed"] for item in items) / len(items), 4),
            "pack_attempt_count": pack_attempts,
            "pack_failure_count": pack_failures,
            "count": len(items),
        }
    raw_score = track_scores.get("raw", {}).get("score", 0.0)
    skill_score = track_scores.get("skill", {}).get("score", 0.0)
    complete = len(valid) == 30 and all(track in track_scores for track in ("raw", "skill"))
    total_score = round((raw_score + skill_score) / 2.0, 2) if complete else None

    category_scores = {
        category: {
            "label": CATEGORY_LABELS.get(category, category),
            "score": round(mean(item["score"]["total_score"] for item in items), 2),
            "format_score": round(mean(item["score"]["format_score"] for item in items), 2),
            "pass_at_1": round(sum(item["score"]["passed"] for item in items) / len(items), 4),
        }
        for category, items in categories.items()
    }
    cap_reasons: dict[str, int] = defaultdict(int)
    pack_failure_reasons: dict[str, int] = defaultdict(int)
    pack_attempt_count = sum(_pack_counts(item)[0] for item in valid)
    pack_failure_count = sum(_pack_counts(item)[1] for item in valid)
    observed_models = sorted(
        {
            item["response"]["model"]
            for item in valid
            if isinstance((item.get("response") or {}).get("model"), str)
            and item["response"]["model"]
        }
    )
    for item in valid:
        cap_reasons[item["score"].get("cap_reason") or "none"] += 1
        if item["state"].get("pack_ok"):
            continue
        pack_error = str(((item.get("commands") or {}).get("pack") or {}).get("stderr", ""))
        if "function_not_found" in pack_error:
            pack_failure_reasons["function_not_found"] += 1
        elif "source_preflight_failed" in pack_error:
            pack_failure_reasons["source_preflight_failed"] += 1
        elif "semantic_method_rebuild_failed" in pack_error:
            pack_failure_reasons["semantic_method_rebuild_failed"] += 1
        else:
            pack_failure_reasons["other"] += 1
    return {
        "benchmark_version": manifest["benchmark_version"],
        "scoring_version": manifest.get("scoring_version", "v1.0"),
        "run_id": manifest["run_id"],
        "model": manifest["model"],
        "reasoning_effort": manifest["reasoning_effort"],
        "protocol": manifest.get("protocol"),
        "wire_protocol": manifest.get("wire_protocol", manifest.get("protocol")),
        "observed_models": observed_models,
        "runtime_available": False,
        "runtime_status": "runtime_unavailable_defender_blocked",
        "run_status": "complete" if complete else ("blocked_api" if infrastructure_failures else "incomplete"),
        "total_score": total_score,
        "track_scores": track_scores,
        "skill_gain": (
            round(skill_score - raw_score, 2)
            if all(track in track_scores for track in ("raw", "skill"))
            else None
        ),
        "category_scores": category_scores,
        "cap_reason_counts": dict(cap_reasons),
        "pack_failure_reason_counts": dict(pack_failure_reasons),
        "pack_attempt_count": pack_attempt_count,
        "pack_failure_count": pack_failure_count,
        "pack_failure_format_deduction": 15.0 * pack_failure_count,
        "completed_records": len(valid),
        "expected_records": 30,
        "infrastructure_failures": infrastructure_failures,
    }


def render_markdown(scorecard: dict[str, Any], records: list[dict[str, Any]]) -> str:
    lines = [
        "# 易语言大模型基准测试报告",
        "",
        f"- 运行编号：`{scorecard['run_id']}`",
        f"- 模型：`{scorecard['model']}`",
        f"- 推理等级：`{scorecard['reasoning_effort']}`",
        f"- 统一协议：`{scorecard.get('protocol') or 'unknown'}`",
        f"- 外部传输协议：`{scorecard.get('wire_protocol') or 'unknown'}`",
        "- 服务端模型标识："
        + (
            ", ".join(f"`{item}`" for item in scorecard.get("observed_models", []))
            if scorecard.get("observed_models")
            else "`未返回`"
        ),
        f"- 基准版本：`{scorecard['benchmark_version']}`",
        f"- 评分版本：`{scorecard['scoring_version']}`",
        f"- 运行状态：`{scorecard['run_status']}`",
        (
            f"- 总分：**{scorecard['total_score']:.2f} / 100**"
            if scorecard["total_score"] is not None
            else "- 总分：**N/A（尚无完整有效跑分）**"
        ),
        f"- 运行期验证：`{scorecard['runtime_status']}`",
        "",
        "## 轨道成绩",
        "",
        "| 轨道 | 得分 | 格式分 | 回包失败/尝试 | 编译率 | pass@1 |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for track in ("raw", "skill"):
        data = scorecard["track_scores"].get(track, {})
        if data:
            lines.append(
                f"| {track} | {data['score']:.2f} | {data['format_score']:.2f} | "
                f"{data['pack_failure_count']}/{data['pack_attempt_count']} | "
                f"{data['compile_rate'] * 100:.1f}% | {data['pass_at_1'] * 100:.1f}% |"
            )
        else:
            lines.append(f"| {track} | N/A | N/A | N/A | N/A | N/A |")
    skill_gain = (
        f"{scorecard['skill_gain']:+.2f}" if scorecard["skill_gain"] is not None else "N/A"
    )
    lines.extend(
        [
            "",
            f"Skill 增益：**{skill_gain}**",
            "",
            "## 能力分项",
            "",
            "| 能力 | 得分 | 格式分 | pass@1 |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for category in ("format", "core", "flow", "abstraction", "repair"):
        data = scorecard["category_scores"].get(category, {})
        if data:
            lines.append(
                f"| {data['label']} | {data['score']:.2f} | "
                f"{data['format_score']:.2f} | {data['pass_at_1'] * 100:.1f}% |"
            )
        else:
            lines.append(f"| {CATEGORY_LABELS[category]} | N/A | N/A | N/A |")
    if scorecard["infrastructure_failures"]:
        lines.extend(["", "## 基础设施失败", ""])
        for failure in scorecard["infrastructure_failures"]:
            lines.append(
                f"- `{failure['task_id']}/{failure['track']}` HTTP {failure['status']}：{failure['error']}"
            )
    if scorecard["cap_reason_counts"]:
        lines.extend(["", "## 失败分布", ""])
        lines.append(
            f"- 回包尝试：`{scorecard['pack_attempt_count']}` 次，失败 "
            f"`{scorecard['pack_failure_count']}` 次，累计格式原始分扣除 "
            f"`{scorecard['pack_failure_format_deduction']:.0f}` 分。"
        )
        lines.append(
            "- 总分上限原因："
            + "，".join(f"`{key}` {value}" for key, value in scorecard["cap_reason_counts"].items())
        )
        if scorecard["pack_failure_reason_counts"]:
            lines.append(
                "- 回包失败根因："
                + "，".join(
                    f"`{key}` {value}"
                    for key, value in scorecard["pack_failure_reason_counts"].items()
                )
            )
    lines.extend(
        [
            "",
            "## 逐题结果",
            "",
            "| 题目 | 轨道 | 类别 | 总分 | 格式 | 编译 | 语义 | 状态 |",
            "| --- | --- | --- | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    valid_records = [item for item in records if (item.get("response") or {}).get("ok")]
    for item in sorted(valid_records, key=lambda row: (row["task_id"], row["track"])):
        score = item["score"]
        status = "PASS" if score["passed"] else (score["cap_reason"] or "FAIL")
        lines.append(
            f"| {item['task_id']} {item['title']} | {item['track']} | {CATEGORY_LABELS.get(item['category'], item['category'])} | "
            f"{score['total_score']:.2f} | {score['format_score']:.2f} | {score['compile_score']:.0f} | "
            f"{score['semantic_score']:.2f} | {status} |"
        )
    lines.extend(
        [
            "",
            "## 说明",
            "",
            "本机 Defender 阻止新编译的易语言 EXE 启动，因此本报告不包含运行断言。"
            "格式分已经覆盖严格响应、声明与流程格式、回包、再次解包、一致性比较和 IDE 打开。",
            "",
        ]
    )
    return "\n".join(lines)


def write_report(run_root: Path, manifest: dict[str, Any], records: list[dict[str, Any]]) -> dict[str, Any]:
    scorecard = summarize(records, manifest)
    (run_root / "scorecard.json").write_text(
        json.dumps(scorecard, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (run_root / "report.md").write_text(render_markdown(scorecard, records), encoding="utf-8")
    return scorecard
