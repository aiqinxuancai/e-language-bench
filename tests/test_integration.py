import json
import os
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from elang_bench.models import Task
from elang_bench.runner import load_tasks
from elang_bench.workspace import WorkspaceEvaluator, write_source


@unittest.skipUnless(os.environ.get("ELANG_BENCH_INTEGRATION") == "1", "set ELANG_BENCH_INTEGRATION=1")
class ToolchainIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[1]
        self.config = json.loads((self.root / "bench.json").read_text(encoding="utf-8"))
        self.tasks = load_tasks(self.root / self.config["dataset"])
        self.evaluator = WorkspaceEvaluator(self.config)

    def test_minimal_template_roundtrip_and_compile(self):
        task: Task = self.tasks[0]
        with tempfile.TemporaryDirectory() as temporary:
            case_root = Path(temporary)
            workspace, prepare = self.evaluator.prepare(task, case_root)
            self.assertEqual(prepare.exit_code, 0, prepare.stderr or prepare.stdout)
            write_source(
                workspace / "src/程序集1.txt",
                ".版本 2\n\n.程序集 程序集1\n\n.子程序 _启动子程序, 整数型\n\n' 基线\n返回 (0)\n",
            )
            state, commands = self.evaluator.evaluate(task, workspace, case_root)
            self.assertTrue(state.validate_ok, commands.get("validate"))
            self.assertEqual(state.pack_attempt_count, 1)
            self.assertEqual(state.pack_failure_count, 0)
            self.assertTrue(state.pack_ok, commands.get("pack"))
            self.assertTrue(state.reunpack_ok, commands.get("reunpack"))
            self.assertTrue(state.compare_ok, commands.get("compare"))
            self.assertTrue(state.ide_open_ok, commands.get("compile_result"))
            self.assertTrue(state.compile_ok, commands.get("compile_result"))

    def test_new_class_page_can_be_packed_and_compiled(self):
        task = next(item for item in self.tasks if item.id == "abs-03")
        with tempfile.TemporaryDirectory() as temporary:
            case_root = Path(temporary)
            workspace, prepare = self.evaluator.prepare(task, case_root)
            self.assertEqual(prepare.exit_code, 0, prepare.stderr or prepare.stdout)
            write_source(
                workspace / "src/计数器.txt",
                ".版本 2\n\n.程序集 计数器, , 公开\n.程序集变量 当前值, 整数型\n\n"
                ".子程序 _初始化\n\n.子程序 _销毁\n\n.子程序 增加, , 公开\n.参数 增量, 整数型\n\n"
                "当前值 ＝ 当前值 ＋ 增量\n\n.子程序 取当前值, 整数型, 公开\n\n返回 (当前值)\n",
            )
            write_source(
                workspace / "src/程序集1.txt",
                ".版本 2\n\n.程序集 程序集1\n\n.子程序 _启动子程序, 整数型\n\n返回 (0)\n",
            )
            state, commands = self.evaluator.evaluate(task, workspace, case_root)
            self.assertTrue(state.validate_ok, commands.get("validate"))
            self.assertTrue(state.pack_ok, commands.get("pack"))
            self.assertTrue(state.reunpack_ok, commands.get("reunpack"))
            self.assertTrue(state.ide_open_ok, commands.get("compile_result"))
            self.assertTrue(state.compile_ok, commands.get("compile_result"))

    def test_fixed_tables_can_be_packed_and_compiled(self):
        task = next(item for item in self.tasks if item.id == "fmt-03")
        with tempfile.TemporaryDirectory() as temporary:
            case_root = Path(temporary)
            workspace, prepare = self.evaluator.prepare(task, case_root)
            self.assertEqual(prepare.exit_code, 0, prepare.stderr or prepare.stdout)
            write_source(
                workspace / "src/.数据类型.txt",
                ".版本 2\n\n.数据类型 坐标记录, 公开, 二维坐标\n"
                "    .成员 X, 整数型\n    .成员 Y, 整数型\n    .成员 标签, 文本型, , , 标签说明\n",
            )
            write_source(
                workspace / "src/.全局变量.txt",
                ".版本 2\n\n.全局变量 默认坐标, 坐标记录, , , 默认坐标说明\n",
            )
            write_source(
                workspace / "src/程序集1.txt",
                ".版本 2\n\n.程序集 程序集1\n\n.子程序 _启动子程序, 整数型\n\n返回 (0)\n",
            )
            state, commands = self.evaluator.evaluate(task, workspace, case_root)
            self.assertTrue(state.validate_ok, commands.get("validate"))
            self.assertTrue(state.pack_ok, commands.get("pack"))
            self.assertTrue(state.reunpack_ok, commands.get("reunpack"))
            self.assertTrue(state.ide_open_ok, commands.get("compile_result"))
            self.assertTrue(state.compile_ok, commands.get("compile_result"))

    def test_distinct_projects_can_compile_in_parallel(self):
        task: Task = self.tasks[0]

        def evaluate(case_root: Path):
            workspace, prepare = self.evaluator.prepare(task, case_root)
            if prepare.exit_code != 0:
                return None, {"prepare": prepare.to_dict()}
            write_source(
                workspace / "src/程序集1.txt",
                ".版本 2\n\n.程序集 程序集1\n\n.子程序 _启动子程序, 整数型\n\n返回 (0)\n",
            )
            return self.evaluator.evaluate(task, workspace, case_root)

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with ThreadPoolExecutor(max_workers=2) as executor:
                results = list(executor.map(evaluate, (root / "case-a", root / "case-b")))
            for state, commands in results:
                self.assertIsNotNone(state, commands)
                self.assertTrue(state.pack_ok, commands.get("pack"))
                self.assertTrue(state.ide_open_ok, commands.get("compile_result"))
                self.assertTrue(state.compile_ok, commands.get("compile_result"))


if __name__ == "__main__":
    unittest.main()
