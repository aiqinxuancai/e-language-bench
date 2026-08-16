import unittest

from elang_bench.models import Diagnostic, StageState
from elang_bench.scoring import SCORING_VERSION, assign_deductions, rescore_record, score_state


class ScoringTests(unittest.TestCase):
    def valid_state(self):
        return StageState(
            contract_ok=True,
            paths_ok=True,
            validate_ok=True,
            pack_attempt_count=1,
            pack_ok=True,
            reunpack_ok=True,
            compare_ok=True,
            ide_open_ok=True,
            compile_ok=True,
            semantic_earned=20,
            semantic_total=20,
        )

    def test_perfect_score(self):
        result = score_state(self.valid_state())
        self.assertEqual(result["total_score"], 100.0)
        self.assertEqual(result["precompile_format_score"], 100.0)
        self.assertTrue(result["passed"])

    def test_validation_failure_retains_only_precompile_diagnostics(self):
        state = self.valid_state()
        state.validate_ok = False
        state.pack_ok = False
        state.reunpack_ok = False
        state.compare_ok = False
        state.ide_open_ok = False
        state.compile_ok = False
        state.diagnostics.append(
            Diagnostic("validate", "declaration_field_count", "bad declaration", file="src/a.txt", line=2)
        )
        result = score_state(state)
        assign_deductions(state, result)
        self.assertGreater(result["precompile_format_score"], 0)
        self.assertEqual(result["format_score"], 0)
        self.assertEqual(result["semantic_score"], 0)
        self.assertEqual(result["total_score"], 0)
        self.assertGreater(state.diagnostics[0].deduction, 0)

    def test_pack_failure_has_stricter_cap(self):
        state = self.valid_state()
        state.pack_attempt_count = 1
        state.pack_failure_count = 1
        state.pack_ok = False
        state.reunpack_ok = False
        state.compare_ok = False
        state.ide_open_ok = False
        state.compile_ok = False
        result = score_state(state)
        self.assertEqual(result["score_cap"], 0.0)
        self.assertEqual(result["cap_reason"], "pack_failed")
        self.assertEqual(result["pack_failure_count"], 1)
        self.assertEqual(result["pack_failure_deduction"], 15.0)

    def test_each_pack_failure_deducts_another_fifteen_format_points(self):
        once = self.valid_state()
        once.pack_attempt_count = 1
        once.pack_failure_count = 1
        once.pack_ok = False
        once.reunpack_ok = False
        once.compare_ok = False
        once.ide_open_ok = False
        once.compile_ok = False

        twice = self.valid_state()
        twice.pack_attempt_count = 2
        twice.pack_failure_count = 2
        twice.pack_ok = False
        twice.reunpack_ok = False
        twice.compare_ok = False
        twice.ide_open_ok = False
        twice.compile_ok = False

        once_score = score_state(once)
        twice_score = score_state(twice)
        self.assertEqual(
            once_score["precompile_format_score"]
            - twice_score["precompile_format_score"],
            15.0,
        )
        self.assertEqual(once_score["format_score"], 0.0)
        self.assertEqual(twice_score["format_score"], 0.0)
        self.assertEqual(twice_score["pack_failure_deduction"], 30.0)

    def test_failed_pack_before_success_still_costs_format_points_and_pass_at_1(self):
        state = self.valid_state()
        state.pack_attempt_count = 2
        state.pack_failure_count = 1
        result = score_state(state)
        self.assertEqual(result["format_score"], 85.0)
        self.assertEqual(result["format_components"]["pack_failure_attempts"], -15.0)
        self.assertFalse(result["passed"])

    def test_compile_failure_zeroes_effective_format_semantic_and_total(self):
        state = self.valid_state()
        state.compile_ok = False
        result = score_state(state)
        self.assertEqual(result["scoring_version"], SCORING_VERSION)
        self.assertEqual(result["precompile_format_score"], 100.0)
        self.assertEqual(result["precompile_semantic_score"], 100.0)
        self.assertEqual(result["format_score"], 0.0)
        self.assertEqual(result["semantic_score"], 0.0)
        self.assertEqual(result["total_score"], 0.0)
        self.assertEqual(result["cap_reason"], "compile_failed")

    def test_rescore_record_replaces_old_score_diagnostics(self):
        state = self.valid_state()
        state.compile_ok = False
        record = {
            "state": {
                **state.__dict__,
                "diagnostics": [
                    {
                        "stage": "score",
                        "code": "compile_failed",
                        "message": "old score",
                        "severity": "error",
                        "file": None,
                        "line": None,
                        "deduction": 4.0,
                    }
                ],
            },
            "score": {"total_score": 65.0},
        }
        updated = rescore_record(record)
        self.assertEqual(updated["score"]["total_score"], 0.0)
        score_diagnostics = [
            item for item in updated["state"]["diagnostics"] if item["stage"] == "score"
        ]
        self.assertEqual(len(score_diagnostics), 1)

    def test_pack_diagnostic_deduction_is_per_attempt_not_per_error_message(self):
        state = self.valid_state()
        state.pack_failure_count = 1
        state.pack_ok = False
        state.reunpack_ok = False
        state.compare_ok = False
        state.ide_open_ok = False
        state.compile_ok = False
        state.diagnostics.extend(
            [
                Diagnostic("pack", "first_error", "first"),
                Diagnostic("pack", "second_error", "second"),
            ]
        )
        result = score_state(state)
        assign_deductions(state, result)
        self.assertEqual(sum(item.deduction for item in state.diagnostics[:2]), 0.0)
        summaries = [item for item in state.diagnostics if item.code == "pack_failure_attempts"]
        self.assertEqual(len(summaries), 1)
        self.assertEqual(summaries[0].deduction, 15.0)

    def test_contract_failure_is_zero(self):
        result = score_state(StageState(semantic_earned=20, semantic_total=20))
        self.assertEqual(result["total_score"], 0.0)


if __name__ == "__main__":
    unittest.main()
