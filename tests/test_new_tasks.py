import json
import os
import tempfile
import unittest
from pathlib import Path

from elang_bench.runner import load_tasks
from elang_bench.workspace import WorkspaceEvaluator, evaluate_semantics, write_source


ROOT = Path(__file__).resolve().parents[1]
HEADER = ".版本 2\n\n.程序集 程序集1\n\n"
SOURCES = {
    "fmt-04": """.子程序 _启动子程序, 整数型

机器码加法 (7, 5)
机器码加法 (-9, 4)
返回 (0)

.子程序 机器码加法, 整数型, 公开
.参数 甲, 整数型
.参数 乙, 整数型

' mov eax,[ebp+8]; add eax,[ebp+12]; leave; ret 8
置入代码 ({ 139, 69, 8, 3, 69, 12, 201, 194, 8, 0 })
""",
    "core-04": """.子程序 _启动子程序, 整数型
.局部变量 键, 文本型
.局部变量 值, 文本型

解析键值 (“ name = Alice=admin ”, 键, 值)
返回 (0)

.子程序 解析键值, 逻辑型, 公开
.参数 输入, 文本型
.参数 键, 文本型, 参考
.参数 值, 文本型, 参考
.局部变量 位置, 整数型

键 ＝ “”
值 ＝ “”
位置 ＝ 寻找文本 (输入, “=”, 1, 假)
.如果真 (位置 ＝ -1)
    返回 (假)
.如果真结束
键 ＝ 删首尾空 (取文本左边 (输入, 位置 － 1))
.如果真 (键 ＝ “”)
    返回 (假)
.如果真结束
值 ＝ 删首尾空 (取文本中间 (输入, 位置 ＋ 1, 取文本长度 (输入) － 位置))
返回 (真)
""",
    "abs-04": """.子程序 _启动子程序, 整数型
.局部变量 输入, 整数型, , "0"
.局部变量 输出, 整数型, , "0"

加入成员 (输入, 3)
加入成员 (输入, -1)
加入成员 (输入, 3)
加入成员 (输入, 0)
加入成员 (输入, -1)
加入成员 (输入, 2)
稳定去重 (输入, 输出)
返回 (0)

.子程序 稳定去重, 整数型, 公开
.参数 输入, 整数型, 数组
.参数 输出, 整数型, 参考 数组
.局部变量 i, 整数型
.局部变量 j, 整数型
.局部变量 已存在, 逻辑型

清除数组 (输出)
.计次循环首 (取数组成员数 (输入), i)
    已存在 ＝ 假
    .计次循环首 (取数组成员数 (输出), j)
        .如果真 (输入[i] ＝ 输出[j])
            已存在 ＝ 真
            跳出循环 ()
        .如果真结束
    .计次循环尾 ()
    .如果真 (已存在 ＝ 假)
        加入成员 (输出, 输入[i])
    .如果真结束
.计次循环尾 ()
返回 (取数组成员数 (输出))
""",
    "flow-04": """.子程序 _启动子程序, 整数型

最大公约数 (48, 18)
最大公约数 (0, 7)
最大公约数 (0, 0)
返回 (0)

.子程序 最大公约数, 整数型, 公开
.参数 a, 整数型
.参数 b, 整数型
.局部变量 r, 整数型

.判断循环首 (b ≠ 0)
    r ＝ a % b
    a ＝ b
    b ＝ r
.判断循环尾 ()
返回 (a)
""",
    "repair-04": """.子程序 _启动子程序, 整数型
.局部变量 文本数据, 字节集
.局部变量 整数数据, 字节集

转换往返 (“-00123”, 文本数据, 整数数据)
到文本 (文本数据)
取字节集长度 (整数数据)
转换往返 (“0”, 文本数据, 整数数据)
返回 (0)

.子程序 转换往返, 文本型, 公开
.参数 输入, 文本型
.参数 文本数据, 字节集, 参考
.参数 整数数据, 字节集, 参考
.局部变量 数值, 整数型

文本数据 ＝ 到字节集 (输入)
数值 ＝ 到整数 (输入)
整数数据 ＝ 到字节集 (数值)
返回 (到文本 (到整数 (取字节集数据 (整数数据, #整数型, 1))))
""",
}


class NewTaskTests(unittest.TestCase):
    def setUp(self):
        self.tasks = {task.id: task for task in load_tasks(ROOT / "benchmarks/v2/tasks.json")}

    def test_reference_sources_satisfy_all_static_checks(self):
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            for task_id, source in SOURCES.items():
                with self.subTest(task_id=task_id):
                    write_source(workspace / "src/程序集1.txt", HEADER + source)
                    earned, total, checks = evaluate_semantics(self.tasks[task_id], workspace)
                    self.assertEqual((earned, total), (20, 20), checks)

    def test_machine_code_check_rejects_mixed_language_body(self):
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            write_source(workspace / "src/程序集1.txt", HEADER + SOURCES["fmt-04"] + "返回 (甲 ＋ 乙)\n")
            _, _, checks = evaluate_semantics(self.tasks["fmt-04"], workspace)
            pure = next(check for check in checks if check["name"] == "纯机器码执行体")
            self.assertFalse(pure["passed"])

    @unittest.skipUnless(os.environ.get("ELANG_BENCH_INTEGRATION") == "1", "set ELANG_BENCH_INTEGRATION=1")
    def test_new_task_references_compile_with_real_toolchain(self):
        config = json.loads((ROOT / "config/bench.json").read_text(encoding="utf-8"))
        evaluator = WorkspaceEvaluator(config)
        self.assertEqual(evaluator.check_environment(), [])
        with tempfile.TemporaryDirectory() as temporary:
            for task_id, source in SOURCES.items():
                with self.subTest(task_id=task_id):
                    case_root = Path(temporary) / task_id
                    case_root.mkdir()
                    task = self.tasks[task_id]
                    workspace, prepare = evaluator.prepare(task, case_root)
                    self.assertEqual(prepare.exit_code, 0, prepare.to_dict())
                    write_source(workspace / "src/程序集1.txt", HEADER + source)
                    state, commands = evaluator.evaluate(task, workspace, case_root)
                    self.assertTrue(state.validate_ok, commands.get("validate"))
                    self.assertTrue(state.pack_ok, commands.get("pack"))
                    self.assertTrue(state.reunpack_ok, commands.get("reunpack"))
                    self.assertTrue(state.compare_ok, commands.get("compare"))
                    self.assertTrue(state.compile_ok, commands.get("compile_result"))
                    self.assertEqual(state.semantic_earned, 20, commands.get("semantic_checks"))
