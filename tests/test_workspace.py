import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from elang_bench.models import CommandResult
from elang_bench.workspace import (
    compile_result_ok,
    compile_temp_directory,
    parse_preflight_diagnostics,
    run_command,
)


class WorkspaceTests(unittest.TestCase):
    def test_compile_temp_directory_is_stable_unique_and_outside_case(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = compile_temp_directory(root / "case-a")
            repeated = compile_temp_directory(root / "case-a")
            second = compile_temp_directory(root / "case-b")

        self.assertEqual(first, repeated)
        self.assertNotEqual(first, second)
        self.assertNotIn(root, first.parents)

    @patch("elang_bench.workspace.subprocess.run")
    def test_run_command_applies_environment_overrides(self, mocked_run):
        mocked_run.return_value = subprocess.CompletedProcess(["tool"], 0, b"", b"")
        with patch.dict(os.environ, {"ELANG_BENCH_PARENT_ENV": "preserved"}):
            result = run_command(
                ["tool"],
                10,
                env_overrides={"TEMP": "case-temp", "TMP": "case-temp"},
            )

        self.assertEqual(result.exit_code, 0)
        environment = mocked_run.call_args.kwargs["env"]
        self.assertEqual(environment["ELANG_BENCH_PARENT_ENV"], "preserved")
        self.assertEqual(environment["TEMP"], "case-temp")
        self.assertEqual(environment["TMP"], "case-temp")

    def test_preflight_diagnostics_are_parsed_and_deduplicated(self):
        line = (
            "source_preflight_error: file=src/程序集1.txt, line=7, "
            "code=flow_mismatch, detail=wrong terminator"
        )
        result = CommandResult(["validate"], 255, stdout=line + "\n" + line)
        diagnostics = parse_preflight_diagnostics(result)
        self.assertEqual(len(diagnostics), 1)
        self.assertEqual(diagnostics[0].code, "flow_mismatch")
        self.assertEqual(diagnostics[0].line, 7)

    def test_compile_failure_marker_overrides_success_json(self):
        with tempfile.TemporaryDirectory() as temporary:
            result_path = Path(temporary) / "result.json"
            result_path.write_text(
                json.dumps(
                    {
                        "ok": True,
                        "compile_result": {
                            "ok": True,
                            "artifact_verified": True,
                            "output_file_exists": True,
                            "output_file_modified_after_compile": True,
                            "output_window_text": "程序代码编译成功\n静态连接失败",
                        },
                        "eide_info": {"source_open": True, "source_state": "source_open"},
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            ok, source_open, _, diagnostics = compile_result_ok(
                CommandResult(["compile"], 0), result_path
            )
            self.assertFalse(ok)
            self.assertTrue(source_open)
            self.assertIn("failure_marker", {item.code for item in diagnostics})


if __name__ == "__main__":
    unittest.main()
