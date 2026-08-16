import unittest

from elang_bench.api import (
    AnthropicMessagesClient,
    GeminiGenerateContentClient,
    OpenAIResponsesClient,
    anthropic_messages_endpoint,
    anthropic_response_has_content,
    chat_completions_endpoint,
    chat_response_has_message,
    gemini_generate_content_endpoint,
    gemini_response_has_candidate,
    responses_endpoint,
    responses_response_has_output,
)


class EndpointTests(unittest.TestCase):
    def test_root_url_gets_v1_path(self):
        self.assertEqual(
            chat_completions_endpoint("https://api.example.com/"),
            "https://api.example.com/v1/chat/completions",
        )

    def test_versioned_and_complete_urls_are_preserved(self):
        self.assertEqual(
            chat_completions_endpoint("https://api.example.com/v1"),
            "https://api.example.com/v1/chat/completions",
        )
        self.assertEqual(
            chat_completions_endpoint("https://api.example.com/v1/chat/completions"),
            "https://api.example.com/v1/chat/completions",
        )

    def test_non_v1_versioned_base_url_gets_chat_path_directly(self):
        self.assertEqual(
            chat_completions_endpoint("https://ark.example.com/api/coding/v3"),
            "https://ark.example.com/api/coding/v3/chat/completions",
        )

    def test_responses_url_is_converted(self):
        self.assertEqual(
            chat_completions_endpoint("https://api.example.com/v1/responses"),
            "https://api.example.com/v1/chat/completions",
        )

    def test_responses_endpoint_normalization(self):
        self.assertEqual(
            responses_endpoint("https://api.example.com/"),
            "https://api.example.com/v1/responses",
        )
        self.assertEqual(
            responses_endpoint("https://api.example.com/v1/chat/completions"),
            "https://api.example.com/v1/responses",
        )
        self.assertEqual(
            responses_endpoint("https://ark.example.com/api/v3"),
            "https://ark.example.com/api/v3/responses",
        )

    def test_empty_completed_chat_message_is_a_model_response(self):
        self.assertTrue(
            chat_response_has_message(
                {
                    "choices": [
                        {
                            "finish_reason": "length",
                            "message": {"content": "", "reasoning_content": "unfinished"},
                        }
                    ]
                }
            )
        )
        self.assertFalse(chat_response_has_message({"choices": []}))

    def test_empty_responses_output_is_a_model_response(self):
        self.assertTrue(responses_response_has_output({"output": []}))
        self.assertFalse(responses_response_has_output({}))

    def test_responses_thinking_type_replaces_reasoning_effort(self):
        client = OpenAIResponsesClient(
            base_url="https://api.example.com/v1",
            api_key="secret",
            model="switch-thinking-model",
            reasoning_effort="enabled",
            responses_thinking_type="enabled",
            timeout_seconds=30,
            retry_count=0,
        )
        body = client._request_body("system", "user")
        self.assertEqual(body["thinking"], {"type": "enabled"})
        self.assertNotIn("reasoning", body)

    def test_responses_reasoning_effort_remains_the_default(self):
        client = OpenAIResponsesClient(
            base_url="https://api.example.com/v1",
            api_key="secret",
            model="effort-model",
            reasoning_effort="max",
            timeout_seconds=30,
            retry_count=0,
        )
        body = client._request_body("system", "user")
        self.assertEqual(body["reasoning"], {"effort": "max"})
        self.assertNotIn("thinking", body)

    def test_anthropic_messages_endpoint_and_text_extraction(self):
        self.assertEqual(
            anthropic_messages_endpoint("https://api.example.com/claude-aws"),
            "https://api.example.com/claude-aws/v1/messages",
        )
        raw = {
            "content": [
                {"type": "thinking", "thinking": "hidden"},
                {"type": "text", "text": "visible"},
            ]
        }
        self.assertTrue(anthropic_response_has_content(raw))
        self.assertEqual(AnthropicMessagesClient._extract_anthropic_content(raw), "visible")

    def test_anthropic_request_uses_configured_effort_and_output_budget(self):
        client = AnthropicMessagesClient(
            base_url="https://api.example.com/claude-aws",
            api_key="secret",
            model="claude-opus-5",
            reasoning_effort="max",
            max_output_tokens=65536,
            timeout_seconds=30,
            retry_count=0,
        )
        body = client._request_body("system", "user")
        self.assertEqual(body["output_config"], {"effort": "max"})
        self.assertEqual(body["max_tokens"], 65536)

    def test_gemini_endpoint_and_non_thought_text_extraction(self):
        self.assertEqual(
            gemini_generate_content_endpoint("https://api.example.com/gemini", "gemini-3.6-flash"),
            "https://api.example.com/gemini/v1beta/models/gemini-3.6-flash:generateContent",
        )
        raw = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {"text": "hidden", "thought": True},
                            {"text": "visible"},
                        ]
                    }
                }
            ]
        }
        self.assertTrue(gemini_response_has_candidate(raw))
        self.assertEqual(GeminiGenerateContentClient._extract_gemini_content(raw), "visible")


if __name__ == "__main__":
    unittest.main()
