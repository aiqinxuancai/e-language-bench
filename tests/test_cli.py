import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from elang_bench.cli import main


class CliTests(unittest.TestCase):
    def test_report_does_not_require_local_configuration(self):
        with patch("elang_bench.cli.command_report", return_value=0) as report:
            self.assertEqual(main(["--config", "missing.json", "report", "run-1"]), 0)
        self.assertEqual(report.call_args.args[1], "run-1")

    def test_run_overrides_config_without_changing_file(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "config.json"
            original = json.dumps({"model": "original", "parallel_workers": 2})
            path.write_text(original, encoding="utf-8")
            with patch("elang_bench.cli.BenchmarkRunner") as runner:
                self.assertEqual(main([
                    "--config", str(path), "--model", "override",
                    "run", "--run-id", "trial", "--workers", "3", "--tracks", "raw",
                ]), 0)
                self.assertEqual(runner.call_args.args[1]["model"], "override")
                runner.return_value.run.assert_called_once_with(
                    run_id="trial", tracks=("raw",), workers=3,
                )
            self.assertEqual(path.read_text(encoding="utf-8"), original)
