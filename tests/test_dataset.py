import unittest
from pathlib import Path

from elang_bench.runner import load_tasks


class DatasetTests(unittest.TestCase):
    def test_v1_has_fifteen_tasks_and_five_categories(self):
        root = Path(__file__).resolve().parents[1]
        tasks = load_tasks(root / "benchmarks/v1/tasks.json")
        self.assertEqual(len(tasks), 15)
        self.assertEqual(
            {task.category for task in tasks},
            {"format", "core", "flow", "abstraction", "repair"},
        )
        self.assertTrue(all(sum(check.points for check in task.checks) == 20 for task in tasks))


if __name__ == "__main__":
    unittest.main()

