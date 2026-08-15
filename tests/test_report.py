import unittest

from elang_bench.report import summarize


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
        self.assertEqual(result["pack_failure_format_deduction"], 30.0)


if __name__ == "__main__":
    unittest.main()
