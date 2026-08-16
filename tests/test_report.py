import contextlib
import dataclasses
import io
import json
import tempfile
import unittest
from pathlib import Path

from elang_bench.cli import command_report
from elang_bench.models import StageState
from elang_bench.report import summarize
from elang_bench.scoring import SCORING_VERSION


class ReportTests(unittest.TestCase):
    def test_api_failure_is_not_counted_as_model_score(self):
        manifest = {
            "benchmark_version": "v1-compile",
            "run_id": "test",
            "model": "gpt-5.6-luna",
            "reasoning_effort": "max",
        }
        records = [
            {
                "task_id": "fmt-01",
                "track": "raw",
                "category": "format",
                "response": {"ok": False, "status": 503, "error": "model unavailable"},
                "score": {"total_score": 0, "format_score": 0, "passed": False},
                "state": {"compile_ok": False},
            }
        ]
        result = summarize(records, manifest)
        self.assertEqual(result["run_status"], "blocked_api")
        self.assertIsNone(result["total_score"])
        self.assertEqual(result["completed_records"], 0)
        self.assertEqual(len(result["infrastructure_failures"]), 1)
        self.assertEqual(result["pack_attempt_count"], 0)
        self.assertEqual(result["pack_failure_count"], 0)

    def test_pack_failure_attempts_are_counted_separately_from_api_attempts(self):
        manifest = {
            "benchmark_version": "v1-compile",
            "scoring_version": "v1.1-pack-failure-count",
            "run_id": "test",
            "model": "gpt-5.6-sol",
            "reasoning_effort": "max",
        }
        records = [
            {
                "task_id": "fmt-01",
                "track": "raw",
                "category": "format",
                "response": {"ok": True, "attempt_count": 3},
                "score": {"total_score": 29, "format_score": 25, "passed": False},
                "state": {
                    "contract_ok": True,
                    "pack_ok": False,
                    "compile_ok": False,
                    "pack_attempt_count": 2,
                    "pack_failure_count": 2,
                },
                "commands": {"pack": {"stderr": "pack failed"}},
            }
        ]
        result = summarize(records, manifest)
        self.assertEqual(result["pack_attempt_count"], 2)
        self.assertEqual(result["pack_failure_count"], 2)
        self.assertEqual(result["pack_failure_precompile_deduction"], 30.0)

    def test_report_rescore_persists_current_scoring_version(self):
        state = StageState(
            contract_ok=True,
            paths_ok=True,
            validate_ok=True,
            pack_attempt_count=1,
            pack_ok=True,
            reunpack_ok=True,
            compare_ok=True,
            ide_open_ok=True,
            compile_ok=False,
            semantic_earned=20,
            semantic_total=20,
        )
        manifest = {
            "benchmark_version": "v1-compile",
            "scoring_version": "v1.1-pack-failure-count",
            "run_id": "rescore-test",
            "model": "model",
            "reasoning_effort": "max",
        }
        record = {
            "task_id": "fmt-01",
            "title": "test",
            "track": "raw",
            "category": "format",
            "response": {"ok": True, "status": 200},
            "state": dataclasses.asdict(state),
            "score": {"total_score": 65.0, "format_score": 100.0, "passed": False},
            "commands": {},
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            run_root = root / "results" / "rescore-test"
            records_root = run_root / "records"
            records_root.mkdir(parents=True)
            (run_root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            record_path = records_root / "fmt-01-raw.json"
            record_path.write_text(json.dumps(record), encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(command_report(root, "rescore-test", rescore=True), 0)
            persisted_manifest = json.loads(
                (run_root / "manifest.json").read_text(encoding="utf-8")
            )
            persisted_record = json.loads(record_path.read_text(encoding="utf-8"))
        self.assertEqual(persisted_manifest["scoring_version"], SCORING_VERSION)
        self.assertEqual(persisted_record["score"]["precompile_format_score"], 100.0)
        self.assertEqual(persisted_record["score"]["format_score"], 0.0)
        self.assertEqual(persisted_record["score"]["total_score"], 0.0)


if __name__ == "__main__":
    unittest.main()
