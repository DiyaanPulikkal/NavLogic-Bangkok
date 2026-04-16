"""
llm.py — Gemini wrapper.

Two responsibilities:

  1. translate_to_query — extract intent. The system prompt is REBUILT
     EACH CALL with the active tag vocabulary + synonym table from
     Prolog appended. This is the bridge that keeps the LLM's
     vocabulary in sync with the KB without code changes: add a
     synonym/2 fact in ontology.pl, the next call sees it.
  2. format_result — narrate the orchestrator's structured result back
     to the user. The static prompt teaches the result schema and the
     audit/relaxation narration rules; we just hand the result through.

The GenerateContentConfig is built per-call (not once at __init__) so
the dynamic vocabulary section is always current.
"""

from __future__ import annotations

import logging
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from engine.config import MODEL
from engine.llm.tools import FUNCTION_DECLARATIONS

load_dotenv()

logger = logging.getLogger("llm")


def _create_genai_client():
    if not os.environ.get("GOOGLE_API_KEY"):
        raise RuntimeError(
            "GOOGLE_API_KEY is not set. "
            "Create a back-end/.env file with: GOOGLE_API_KEY=your-key-here"
        )
    return genai.Client()


class LLMInterface:
    def __init__(self):
        self.client = _create_genai_client()
        self.model = MODEL
        self.tools = types.Tool(function_declarations=FUNCTION_DECLARATIONS)

        prompt_path = os.path.join(os.path.dirname(__file__), "system_prompt.txt")
        with open(prompt_path, "r") as f:
            self.static_prompt = f.read()

    def translate_to_query(
        self,
        user_input: str,
        history: list,
        vocab: list[str] | None = None,
        synonyms: dict[str, str] | None = None,
        time_hint: dict | None = None,
    ):
        """Send `user_input` to Gemini with vocab-aware system prompt.

        `time_hint` is the default Bangkok wall-clock the orchestrator
        passes in so the LLM can reason about "tonight" / "tomorrow
        morning" even when the user does not pin a time. It is rendered
        into the system prompt; the LLM may override by emitting its
        own time_context in the function call.

        Returns:
          ((function_name, args_dict), new_history) when Gemini emits a function call,
          (text_response, new_history) when Gemini replies in plain text,
          (None, history) on error.
        """
        try:
            new_history = list(history)
            new_history.append(
                types.Content(role="user", parts=[types.Part(text=user_input)])
            )
            config = self._build_config(vocab, synonyms, time_hint)
            logger.info("Sending query to Gemini...")
            response = self.client.models.generate_content(
                model=self.model,
                config=config,
                contents=new_history,
            )
            if not response.candidates:
                logger.info("Gemini returned no candidates")
                return None, new_history

            new_history.append(response.candidates[0].content)
            for part in response.candidates[0].content.parts:
                if part.function_call:
                    function_name = part.function_call.name
                    arguments = self._args_to_python(part.function_call.args)
                    logger.info(
                        "Gemini function call: %s(%s)",
                        function_name,
                        ", ".join(f"{k}={v!r}" for k, v in arguments.items()),
                    )
                    return (function_name, arguments), new_history

            text_response = None
            for part in response.candidates[0].content.parts:
                if part.text:
                    text_response = part.text
                    break
            logger.info("Gemini returned text response (no function call)")
            return text_response, new_history
        except Exception as e:
            logger.error("Error during model generation: %s", e)
            return None, history

    def format_result(
        self,
        result: dict,
        history: list,
        vocab: list[str] | None = None,
        synonyms: dict[str, str] | None = None,
    ):
        """Send the orchestrator's structured result back through Gemini for narration.

        The static system prompt's "Job 2: Narration" section teaches the
        model the result schema (relaxation_note, audit_trail, etc.).
        Returns the result dict augmented with `data.answer` plus the
        updated history.
        """
        try:
            function_response_part = types.Part.from_function_response(
                name="plan",
                response={"result": result},
            )
            new_history = list(history)
            new_history.append(
                types.Content(role="user", parts=[function_response_part])
            )
            config = self._build_config(vocab, synonyms)
            response = self.client.models.generate_content(
                model=self.model,
                config=config,
                contents=new_history,
            )
            if response.candidates:
                new_history.append(response.candidates[0].content)
            answer = response.text if response.candidates else None
            result.setdefault("data", {})["answer"] = answer
            return result, new_history
        except Exception as e:
            logger.error("Error during result formatting: %s", e)
            result.setdefault("data", {})["answer"] = None
            return result, history

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_config(
        self,
        vocab: list[str] | None,
        synonyms: dict[str, str] | None,
        time_hint: dict | None = None,
    ) -> types.GenerateContentConfig:
        prompt = (
            self.static_prompt
            + self._render_vocab(vocab, synonyms)
            + self._render_time_hint(time_hint)
        )
        return types.GenerateContentConfig(
            system_instruction=prompt,
            tools=[self.tools],
        )

    @staticmethod
    def _render_vocab(
        vocab: list[str] | None,
        synonyms: dict[str, str] | None,
    ) -> str:
        if not vocab and not synonyms:
            return ""
        out = ["\n\n---\n"]
        if vocab:
            out.append(
                "[Active tag vocabulary]: " + ", ".join(sorted(vocab)) + "\n"
            )
        if synonyms:
            pairs = sorted(synonyms.items())
            out.append(
                "[Active synonyms (raw → canonical)]: "
                + "; ".join(f'"{k}" → {v}' for k, v in pairs)
                + "\n"
            )
        return "".join(out)

    @staticmethod
    def _render_time_hint(time_hint: dict | None) -> str:
        """Inject the current Bangkok wall-clock into the system prompt.

        The orchestrator always passes a time_hint, so the LLM has a
        ground frame for relative phrases ("tonight", "tomorrow") even
        when the user doesn't mention time. If the user *does* pin a
        time, the LLM overrides by emitting its own time_context in the
        function call.
        """
        if not time_hint:
            return ""
        wd = time_hint.get("weekday", "?")
        hour = time_hint.get("hour", 0)
        minute = time_hint.get("minute", 0)
        return (
            f"\n[Current time in Bangkok]: weekday={wd}, "
            f"{hour:02d}:{minute:02d} "
            f"(emit time_context={{weekday, hour, minute}} when the user "
            f"pins a time; omit it to default to this frame)\n"
        )

    @staticmethod
    def _args_to_python(args) -> dict:
        """Recursively convert Gemini's protobuf args (Struct/MapComposite) to plain Python.

        Gemini returns nested dicts and lists for our recursive `goal`
        field as protobuf MapComposite / RepeatedComposite. dict() on
        the top level only flattens one layer, leaving inner structures
        as protobuf objects that don't survive JSON serialization or
        the goal serializer downstream.
        """
        return {k: LLMInterface._coerce(v) for k, v in args.items()}

    @staticmethod
    def _coerce(v):
        if isinstance(v, dict):
            return {k: LLMInterface._coerce(x) for k, x in v.items()}
        if isinstance(v, (list, tuple)):
            return [LLMInterface._coerce(x) for x in v]
        if hasattr(v, "items") and callable(v.items):
            return {k: LLMInterface._coerce(x) for k, x in v.items()}
        if hasattr(v, "__iter__") and not isinstance(v, (str, bytes)):
            try:
                return [LLMInterface._coerce(x) for x in v]
            except TypeError:
                return v
        return v
