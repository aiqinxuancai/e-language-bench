import json
import unittest

from elang_bench.workspace import ContractError, parse_strict_response


class ContractTests(unittest.TestCase):
    def response(self, files=None):
        return json.dumps(
            {
                "files": files or {"src/程序集1.txt": ".版本 2"},
                "explanation": "说明",
                "expected_behavior": "行为",
            },
            ensure_ascii=False,
        )

    def test_accepts_json_whitespace(self):
        parsed = parse_strict_response(self.response() + "\n", ("src/程序集1.txt",))
        self.assertEqual(parsed["src/程序集1.txt"], ".版本 2")

    def test_rejects_markdown_fence(self):
        with self.assertRaisesRegex(ContractError, "fences"):
            parse_strict_response("```json\n{}\n```", ("src/程序集1.txt",))

    def test_requires_exact_file_set(self):
        with self.assertRaises(ContractError) as context:
            parse_strict_response(self.response(), ("src/另一个文件.txt",))
        self.assertEqual(context.exception.code, "file_set_mismatch")

    def test_rejects_path_traversal(self):
        value = self.response({"src/../secret.txt": "bad"})
        with self.assertRaises(ContractError) as context:
            parse_strict_response(value, ("src/../secret.txt",))
        self.assertEqual(context.exception.code, "unsafe_path")


if __name__ == "__main__":
    unittest.main()

