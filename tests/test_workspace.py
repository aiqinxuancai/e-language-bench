import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from elang_bench.models import CommandResult
from elang_bench.workspace import (
    compile_temp_directory,
    parse_preflight_diagnostics,
    run_command,
    WorkspaceEvaluator,
)


class WorkspaceTests(unittest.TestCase):
    def test_environment_requires_exact_packager_release(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            tool = root / "tool.exe"
            tool.touch()
            evaluator = WorkspaceEvaluator({"tools": {
                "e_packager": str(tool), "template_root": str(root),
            }})
            for output, exit_code, accepted in (
                ("e-packager v1.2.7\n", 0, True),
                ("e-packager v1.2.6", 0, False),
                ("e-packager v1.2.8", 0, False),
                ("e-packager dev", 0, True),
                ("", 0, False),
                ("e-packager v1.2.7", 1, False),
            ):
                with self.subTest(output=output, exit_code=exit_code), patch(
                    "elang_bench.workspace.run_command",
                    return_value=CommandResult([str(tool), "--version"], exit_code, stdout=output),
                ):
                    if accepted:
                        self.assertEqual(evaluator.check_environment(), [])
                    else:
                        with self.assertRaisesRegex(ValueError, "requires e-packager v1.2.7"):
                            evaluator.check_environment()

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


if __name__ == "__main__":
    unittest.main()
