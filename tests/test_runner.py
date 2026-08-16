import threading
import time
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from elang_bench.api import ApiResponse
from elang_bench.runner import BenchmarkRunner, manifest_mismatches, transport_protocol


class DummyEvaluator:
    @staticmethod
    def check_environment():
        return []


class RunnerTests(unittest.TestCase):
    def test_manifest_identity_detects_toolchain_and_worker_changes(self):
        base = {
            "benchmark_version": "v1-compile",
            "scoring_version": "v1.1-pack-failure-count",
            "model": "model",
            "reasoning_effort": "max",
            "max_output_tokens": 32768,
            "protocol": "openai_responses",
            "wire_protocol": "openai_responses",
            "base_url": "https://api.example.com/v1",
            "parallel_workers": 2,
            "tool_hashes": {"autolinker_fne": "old"},
            "template_hashes": {"template.e": "same"},
            "dataset_sha256": "same",
        }
        current = dict(base)
        current["parallel_workers"] = 4
        current["tool_hashes"] = {"autolinker_fne": "new"}
        self.assertEqual(
            manifest_mismatches(base, current),
            ["parallel_workers", "tool_hashes"],
        )

    def test_manifest_identity_detects_output_budget_changes(self):
        base = {
            "benchmark_version": "v1-compile",
            "scoring_version": "v1.2-compile-gated",
            "model": "claude-opus-5",
            "reasoning_effort": "max",
            "max_output_tokens": 32768,
            "protocol": "openai_responses",
            "wire_protocol": "anthropic_messages",
            "base_url": "https://api.example.com/claude-aws",
            "parallel_workers": 2,
            "tool_hashes": {},
            "template_hashes": {},
            "dataset_sha256": "same",
        }
        current = dict(base)
        current["max_output_tokens"] = 65536
        self.assertEqual(manifest_mismatches(base, current), ["max_output_tokens"])

    def test_responses_transport_can_bridge_to_anthropic(self):
        self.assertEqual(
            transport_protocol(
                {
                    "protocol": "openai_responses",
                    "responses_transport": "anthropic_messages",
                }
            ),
            "anthropic_messages",
        )

    def test_manifest_identity_detects_responses_thinking_changes(self):
        base = {
            "benchmark_version": "v1-compile",
            "scoring_version": "v1.1-pack-failure-count",
            "model": "model",
            "reasoning_effort": "enabled",
            "responses_thinking_type": "enabled",
            "protocol": "openai_responses",
            "wire_protocol": "openai_responses",
            "base_url": "https://api.example.com/v1",
            "parallel_workers": 2,
            "tool_hashes": {},
            "template_hashes": {},
            "dataset_sha256": "same",
        }
        current = dict(base)
        current["responses_thinking_type"] = "disabled"
        self.assertEqual(
            manifest_mismatches(base, current),
            ["responses_thinking_type"],
        )

    def test_cases_execute_concurrently_and_reports_remain_complete(self):
        active = 0
        max_active = 0
        guard = threading.Lock()

        def execute_case(task, track, _case_root, _response_provider):
            nonlocal active, max_active
            with guard:
                active += 1
                max_active = max(max_active, active)
            time.sleep(0.02)
            with guard:
                active -= 1
            return {
                "task_id": task.id,
                "title": task.title,
                "category": task.category,
                "track": track,
                "response": {"ok": True, "status": 200, "attempt_count": 1},
                "state": {
                    "compile_ok": True,
                    "pack_ok": True,
                    "pack_attempt_count": 1,
                    "pack_failure_count": 0,
                },
                "score": {
                    "total_score": 100.0,
                    "format_score": 100.0,
                    "compile_score": 100.0,
                    "semantic_score": 100.0,
                    "passed": True,
                    "cap_reason": None,
                },
                "commands": {},
            }

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            runner = object.__new__(BenchmarkRunner)
            runner.project_root = root
            runner.config = {
                "benchmark_version": "v1-compile",
                "model": "parallel-model",
                "reasoning_effort": "max",
                "protocol": "openai_responses",
                "wire_protocol": "openai_responses",
                "base_url": "https://api.example.com/v1",
            }
            runner.tasks = [
                SimpleNamespace(id=f"task-{index:02d}", title="task", category="format")
                for index in range(15)
            ]
            runner.evaluator = DummyEvaluator()
            runner.skill_context = {}
            runner._execute_case = execute_case
            manifest = {
                "run_id": "parallel-run",
                "benchmark_version": "v1-compile",
                "scoring_version": "v1.1-pack-failure-count",
                "model": "parallel-model",
                "reasoning_effort": "max",
                "protocol": "openai_responses",
                "base_url": "https://api.example.com/v1",
                "parallel_workers": 4,
                "tool_hashes": {"autolinker_fne": "same"},
                "template_hashes": {"template.e": "same"},
                "dataset_sha256": "same",
            }
            provider = lambda *_args: ApiResponse(True, 200, "", {}, 1, 1)
            with patch("elang_bench.runner.build_manifest", return_value=manifest):
                scorecard = runner.run(
                    run_id="parallel-run",
                    workers=4,
                    response_provider=provider,
                )

            self.assertGreaterEqual(max_active, 2)
            self.assertEqual(scorecard["run_status"], "complete")
            self.assertEqual(scorecard["completed_records"], 30)
            self.assertEqual(len(list((root / "results/parallel-run/records").glob("*.json"))), 30)


if __name__ == "__main__":
    unittest.main()
