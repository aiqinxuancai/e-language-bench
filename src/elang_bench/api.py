from __future__ import annotations

import json
import random
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any


VERSIONED_BASE_URL = re.compile(r"/v\d+(?:\.\d+)?$", re.IGNORECASE)


def chat_completions_endpoint(base_url: str) -> str:
    url = base_url.strip().rstrip("/")
    lower = url.lower()
    if lower.endswith("/responses"):
        return url[: -len("/responses")] + "/chat/completions"
    if lower.endswith("/chat/completions"):
        return url
    if VERSIONED_BASE_URL.search(lower):
        return url + "/chat/completions"
    return url + "/v1/chat/completions"


def responses_endpoint(base_url: str) -> str:
    url = base_url.strip().rstrip("/")
    lower = url.lower()
    if lower.endswith("/chat/completions"):
        return url[: -len("/chat/completions")] + "/responses"
    if lower.endswith("/responses"):
        return url
    if VERSIONED_BASE_URL.search(lower):
        return url + "/responses"
    return url + "/v1/responses"


def anthropic_messages_endpoint(base_url: str) -> str:
    url = base_url.strip().rstrip("/")
    lower = url.lower()
    if lower.endswith("/v1/messages") or lower.endswith("/messages"):
        return url
    if lower.endswith("/v1"):
        return url + "/messages"
    return url + "/v1/messages"


def gemini_generate_content_endpoint(base_url: str, model: str) -> str:
    url = base_url.strip().rstrip("/")
    if url.lower().endswith(":generatecontent"):
        return url
    encoded_model = urllib.parse.quote(model, safe="")
    if url.lower().endswith("/v1beta"):
        return f"{url}/models/{encoded_model}:generateContent"
    return f"{url}/v1beta/models/{encoded_model}:generateContent"


def chat_response_has_message(raw: dict[str, Any]) -> bool:
    choices = raw.get("choices")
    return bool(
        isinstance(choices, list)
        and choices
        and isinstance(choices[0], dict)
        and isinstance(choices[0].get("message"), dict)
    )


def responses_response_has_output(raw: dict[str, Any]) -> bool:
    return isinstance(raw.get("output"), list) or isinstance(raw.get("output_text"), str)


def anthropic_response_has_content(raw: dict[str, Any]) -> bool:
    return isinstance(raw.get("content"), list)


def gemini_response_has_candidate(raw: dict[str, Any]) -> bool:
    candidates = raw.get("candidates")
    return bool(isinstance(candidates, list) and candidates and isinstance(candidates[0], dict))


@dataclass
class ApiResponse:
    ok: bool
    status: int | None
    content: str
    raw: dict[str, Any] | str | None
    elapsed_ms: int
    attempt_count: int
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


class OpenAIChatClient:
    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        model: str,
        reasoning_effort: str,
        timeout_seconds: int,
        retry_count: int,
    ) -> None:
        self.endpoint = chat_completions_endpoint(base_url)
        self.api_key = api_key
        self.model = model
        self.reasoning_effort = reasoning_effort
        self.timeout_seconds = timeout_seconds
        self.retry_count = retry_count

    def complete(self, system: str, user: str) -> ApiResponse:
        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "reasoning_effort": self.reasoning_effort,
            "stream": False,
        }
        encoded = json.dumps(body, ensure_ascii=False).encode("utf-8")
        started = time.monotonic()
        last_status: int | None = None
        last_error: str | None = None
        last_raw: dict[str, Any] | str | None = None

        for attempt in range(1, self.retry_count + 2):
            request = urllib.request.Request(
                self.endpoint,
                data=encoded,
                method="POST",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json; charset=utf-8",
                    "Accept": "application/json",
                    "User-Agent": "e-language-bench/1.0",
                },
            )
            try:
                with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                    response_bytes = response.read()
                    last_status = response.status
                raw = json.loads(response_bytes.decode("utf-8"))
                content = self._extract_content(raw)
                elapsed = int((time.monotonic() - started) * 1000)
                if not content and not chat_response_has_message(raw):
                    return ApiResponse(False, last_status, "", raw, elapsed, attempt, "empty response content")
                return ApiResponse(True, last_status, content, raw, elapsed, attempt)
            except urllib.error.HTTPError as exc:
                last_status = exc.code
                payload = exc.read().decode("utf-8", errors="replace")
                last_raw = self._maybe_json(payload)
                last_error = f"HTTP {exc.code}: {payload[:1000]}"
                retryable = exc.code == 429 or 500 <= exc.code < 600
                if not retryable or attempt > self.retry_count:
                    break
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                last_error = f"{type(exc).__name__}: {exc}"
                if attempt > self.retry_count:
                    break
            except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
                last_error = f"invalid API response: {exc}"
                break
            time.sleep(min(8.0, (2 ** (attempt - 1)) + random.random()))

        return ApiResponse(
            False,
            last_status,
            "",
            last_raw,
            int((time.monotonic() - started) * 1000),
            min(self.retry_count + 1, attempt),
            last_error,
        )

    @staticmethod
    def _maybe_json(payload: str) -> dict[str, Any] | str:
        try:
            return json.loads(payload)
        except json.JSONDecodeError:
            return payload

    @staticmethod
    def _extract_content(raw: dict[str, Any]) -> str:
        choices = raw.get("choices")
        if not isinstance(choices, list) or not choices:
            return ""
        message = choices[0].get("message", {})
        content = message.get("content", "")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts: list[str] = []
            for item in content:
                if isinstance(item, dict) and isinstance(item.get("text"), str):
                    parts.append(item["text"])
            return "".join(parts)
        return ""


class AnthropicMessagesClient(OpenAIChatClient):
    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        model: str,
        reasoning_effort: str,
        timeout_seconds: int,
        retry_count: int,
    ) -> None:
        super().__init__(
            base_url=base_url,
            api_key=api_key,
            model=model,
            reasoning_effort=reasoning_effort,
            timeout_seconds=timeout_seconds,
            retry_count=retry_count,
        )
        self.endpoint = anthropic_messages_endpoint(base_url)

    def complete(self, system: str, user: str) -> ApiResponse:
        body = {
            "model": self.model,
            "max_tokens": 32768,
            "system": system,
            "messages": [{"role": "user", "content": user}],
            "output_config": {"effort": self.reasoning_effort},
        }
        encoded = json.dumps(body, ensure_ascii=False).encode("utf-8")
        started = time.monotonic()
        last_status: int | None = None
        last_error: str | None = None
        last_raw: dict[str, Any] | str | None = None
        for attempt in range(1, self.retry_count + 2):
            request = urllib.request.Request(
                self.endpoint,
                data=encoded,
                method="POST",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json; charset=utf-8",
                    "Accept": "application/json",
                    "User-Agent": "e-language-bench/1.0",
                },
            )
            try:
                with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                    response_bytes = response.read()
                    last_status = response.status
                raw = json.loads(response_bytes.decode("utf-8"))
                content = self._extract_anthropic_content(raw)
                elapsed = int((time.monotonic() - started) * 1000)
                if not content and not anthropic_response_has_content(raw):
                    return ApiResponse(False, last_status, "", raw, elapsed, attempt, "empty response content")
                return ApiResponse(True, last_status, content, raw, elapsed, attempt)
            except urllib.error.HTTPError as exc:
                last_status = exc.code
                payload = exc.read().decode("utf-8", errors="replace")
                last_raw = self._maybe_json(payload)
                last_error = f"HTTP {exc.code}: {payload[:1000]}"
                retryable = exc.code == 429 or 500 <= exc.code < 600
                if not retryable or attempt > self.retry_count:
                    break
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                last_error = f"{type(exc).__name__}: {exc}"
                if attempt > self.retry_count:
                    break
            except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
                last_error = f"invalid API response: {exc}"
                break
            time.sleep(min(8.0, (2 ** (attempt - 1)) + random.random()))
        return ApiResponse(
            False,
            last_status,
            "",
            last_raw,
            int((time.monotonic() - started) * 1000),
            min(self.retry_count + 1, attempt),
            last_error,
        )

    @staticmethod
    def _extract_anthropic_content(raw: dict[str, Any]) -> str:
        content = raw.get("content")
        if not isinstance(content, list):
            return ""
        return "".join(
            item["text"]
            for item in content
            if isinstance(item, dict) and item.get("type") == "text" and isinstance(item.get("text"), str)
        )


class GeminiGenerateContentClient(OpenAIChatClient):
    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        model: str,
        reasoning_effort: str,
        timeout_seconds: int,
        retry_count: int,
    ) -> None:
        super().__init__(
            base_url=base_url,
            api_key=api_key,
            model=model,
            reasoning_effort=reasoning_effort,
            timeout_seconds=timeout_seconds,
            retry_count=retry_count,
        )
        self.endpoint = gemini_generate_content_endpoint(base_url, model)

    def complete(self, system: str, user: str) -> ApiResponse:
        body = {
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": user}]}],
            "generationConfig": {
                "maxOutputTokens": 16384,
                "thinkingConfig": {"thinkingLevel": self.reasoning_effort.upper()},
            },
        }
        encoded = json.dumps(body, ensure_ascii=False).encode("utf-8")
        started = time.monotonic()
        last_status: int | None = None
        last_error: str | None = None
        last_raw: dict[str, Any] | str | None = None
        for attempt in range(1, self.retry_count + 2):
            request = urllib.request.Request(
                self.endpoint,
                data=encoded,
                method="POST",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "x-goog-api-key": self.api_key,
                    "Content-Type": "application/json; charset=utf-8",
                    "Accept": "application/json",
                    "User-Agent": "e-language-bench/1.0",
                },
            )
            try:
                with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                    response_bytes = response.read()
                    last_status = response.status
                raw = json.loads(response_bytes.decode("utf-8"))
                content = self._extract_gemini_content(raw)
                elapsed = int((time.monotonic() - started) * 1000)
                if not content and not gemini_response_has_candidate(raw):
                    return ApiResponse(False, last_status, "", raw, elapsed, attempt, "empty response content")
                return ApiResponse(True, last_status, content, raw, elapsed, attempt)
            except urllib.error.HTTPError as exc:
                last_status = exc.code
                payload = exc.read().decode("utf-8", errors="replace")
                last_raw = self._maybe_json(payload)
                last_error = f"HTTP {exc.code}: {payload[:1000]}"
                retryable = exc.code == 429 or 500 <= exc.code < 600
                if not retryable or attempt > self.retry_count:
                    break
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                last_error = f"{type(exc).__name__}: {exc}"
                if attempt > self.retry_count:
                    break
            except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
                last_error = f"invalid API response: {exc}"
                break
            time.sleep(min(8.0, (2 ** (attempt - 1)) + random.random()))
        return ApiResponse(
            False,
            last_status,
            "",
            last_raw,
            int((time.monotonic() - started) * 1000),
            min(self.retry_count + 1, attempt),
            last_error,
        )

    @staticmethod
    def _extract_gemini_content(raw: dict[str, Any]) -> str:
        candidates = raw.get("candidates")
        if not isinstance(candidates, list) or not candidates:
            return ""
        content = candidates[0].get("content")
        if not isinstance(content, dict) or not isinstance(content.get("parts"), list):
            return ""
        return "".join(
            part["text"]
            for part in content["parts"]
            if isinstance(part, dict)
            and not part.get("thought")
            and isinstance(part.get("text"), str)
        )


class OpenAIResponsesClient(OpenAIChatClient):
    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        model: str,
        reasoning_effort: str,
        responses_thinking_type: str | None = None,
        timeout_seconds: int,
        retry_count: int,
    ) -> None:
        super().__init__(
            base_url=base_url,
            api_key=api_key,
            model=model,
            reasoning_effort=reasoning_effort,
            timeout_seconds=timeout_seconds,
            retry_count=retry_count,
        )
        self.endpoint = responses_endpoint(base_url)
        self.responses_thinking_type = responses_thinking_type

    def _request_body(self, system: str, user: str) -> dict[str, Any]:
        body = {
            "model": self.model,
            "instructions": system,
            "input": [
                {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": user}],
                }
            ],
            "stream": False,
            "store": False,
        }
        if self.responses_thinking_type is not None:
            body["thinking"] = {"type": self.responses_thinking_type}
        else:
            body["reasoning"] = {"effort": self.reasoning_effort}
        return body

    def complete(self, system: str, user: str) -> ApiResponse:
        body = self._request_body(system, user)
        encoded = json.dumps(body, ensure_ascii=False).encode("utf-8")
        started = time.monotonic()
        last_status: int | None = None
        last_error: str | None = None
        last_raw: dict[str, Any] | str | None = None
        for attempt in range(1, self.retry_count + 2):
            request = urllib.request.Request(
                self.endpoint,
                data=encoded,
                method="POST",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json; charset=utf-8",
                    "Accept": "application/json",
                    "User-Agent": "e-language-bench/1.0",
                },
            )
            try:
                with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                    response_bytes = response.read()
                    last_status = response.status
                raw = json.loads(response_bytes.decode("utf-8"))
                content = self._extract_responses_content(raw)
                elapsed = int((time.monotonic() - started) * 1000)
                if not content and not responses_response_has_output(raw):
                    return ApiResponse(False, last_status, "", raw, elapsed, attempt, "empty response content")
                return ApiResponse(True, last_status, content, raw, elapsed, attempt)
            except urllib.error.HTTPError as exc:
                last_status = exc.code
                payload = exc.read().decode("utf-8", errors="replace")
                last_raw = self._maybe_json(payload)
                last_error = f"HTTP {exc.code}: {payload[:1000]}"
                retryable = exc.code == 429 or 500 <= exc.code < 600
                if not retryable or attempt > self.retry_count:
                    break
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                last_error = f"{type(exc).__name__}: {exc}"
                if attempt > self.retry_count:
                    break
            except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
                last_error = f"invalid API response: {exc}"
                break
            time.sleep(min(8.0, (2 ** (attempt - 1)) + random.random()))
        return ApiResponse(
            False,
            last_status,
            "",
            last_raw,
            int((time.monotonic() - started) * 1000),
            min(self.retry_count + 1, attempt),
            last_error,
        )

    @staticmethod
    def _extract_responses_content(raw: dict[str, Any]) -> str:
        if isinstance(raw.get("output_text"), str):
            return raw["output_text"]
        parts: list[str] = []
        output = raw.get("output")
        if not isinstance(output, list):
            return ""
        for item in output:
            if not isinstance(item, dict) or item.get("type") != "message":
                continue
            for content in item.get("content", []):
                if not isinstance(content, dict):
                    continue
                if content.get("type") in {"output_text", "text"} and isinstance(content.get("text"), str):
                    parts.append(content["text"])
        return "".join(parts)
