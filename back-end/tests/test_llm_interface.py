"""
tests/test_llm_interface.py — unit tests for the Gemini wrapper.

Gemini calls are mocked at the client layer (FakeClient.models.generate_content).
These tests cover:

  - Function-call extraction for the single `plan` tool.
  - Recursive coercion of nested `goal` protobuf → plain Python dict/list.
  - Text-only responses (when Gemini replies without a function call).
  - Vocab + synonym injection into the per-call system instruction.
  - `format_result` round-trip (answer written into data).
  - Error paths: empty candidates, missing parts, None args, raised exception.
"""

from types import SimpleNamespace

import engine.llm.llm as llm_module


# ------------------------------------------------------------------
# Test doubles — stand in for the google.genai response object.
# ------------------------------------------------------------------


class FakeFunctionCall:
    def __init__(self, name, args):
        self.name = name
        self.args = args


class FakePart:
    def __init__(self, function_call=None, text=None):
        self.function_call = function_call
        self.text = text


class FakeCandidate:
    def __init__(self, parts):
        self.content = SimpleNamespace(parts=parts)


class FakeClient:
    def __init__(self, response=None, error=None, capture=None):
        self._response = response
        self._error = error
        self._capture = capture if capture is not None else {}
        self.models = SimpleNamespace(generate_content=self._generate_content)

    def _generate_content(self, **kwargs):
        self._capture.update(kwargs)
        if self._error:
            raise self._error
        return self._response


def _install_fake_client(monkeypatch, response=None, error=None, capture=None):
    monkeypatch.setattr(
        llm_module,
        "_create_genai_client",
        lambda: FakeClient(response, error, capture),
    )
    # types.Tool and GenerateContentConfig need to be constructible with
    # our real arguments but otherwise opaque — they're only passed through.
    monkeypatch.setattr(llm_module.types, "Tool", lambda **_kw: object())

    def fake_config(**kwargs):
        ns = SimpleNamespace(**kwargs)
        if capture is not None:
            capture.setdefault("_config_calls", []).append(kwargs)
        return ns

    monkeypatch.setattr(
        llm_module.types, "GenerateContentConfig", fake_config,
    )


# ------------------------------------------------------------------
# translate_to_query: function-call extraction.
# ------------------------------------------------------------------


def test_translate_extracts_plan_call_with_nested_goal(monkeypatch):
    goal = {"and": [{"any_tag": ["temple"]}, {"none_tag": ["weather_exposed"]}]}
    function_call = FakeFunctionCall("plan", {"origin": "Siam", "goal": goal})
    response = SimpleNamespace(
        candidates=[FakeCandidate([FakePart(function_call=function_call)])]
    )
    _install_fake_client(monkeypatch, response=response)

    llm = llm_module.LLMInterface()
    result, history = llm.translate_to_query("temples no heat", [], [], {})

    assert result == ("plan", {"origin": "Siam", "goal": goal})
    assert isinstance(history, list) and len(history) == 2


def test_translate_coerces_protobuf_goal_to_python(monkeypatch):
    """Nested MapComposite/RepeatedComposite values must be coerced."""

    class MapComposite(dict):
        """Stand-in that mimics the protobuf nested-dict surface."""

    inner = MapComposite({"any_tag": ["temple"]})
    outer_goal = MapComposite({"and": [inner, MapComposite({"none_tag": ["weather_exposed"]})]})
    function_call = FakeFunctionCall("plan", {"origin": "Siam", "goal": outer_goal})
    response = SimpleNamespace(
        candidates=[FakeCandidate([FakePart(function_call=function_call)])]
    )
    _install_fake_client(monkeypatch, response=response)

    llm = llm_module.LLMInterface()
    (fn, args), _ = llm.translate_to_query("x", [], [], {})

    assert fn == "plan"
    assert args["goal"]["and"][0]["any_tag"] == ["temple"]
    assert args["goal"]["and"][1]["none_tag"] == ["weather_exposed"]


def test_translate_text_response_when_no_function_call(monkeypatch):
    response = SimpleNamespace(
        candidates=[FakeCandidate([FakePart(text="Which station?")])]
    )
    _install_fake_client(monkeypatch, response=response)

    llm = llm_module.LLMInterface()
    result, history = llm.translate_to_query("ambiguous", [], [], {})

    assert result == "Which station?"
    assert any(
        getattr(p, "text", None) == "Which station?"
        for c in history
        for p in getattr(c, "parts", [])
    )


def test_translate_function_call_priority_over_text(monkeypatch):
    function_call = FakeFunctionCall("plan", {"origin": "Asok", "goal": {"route_to": "Siam"}})
    response = SimpleNamespace(
        candidates=[FakeCandidate([
            FakePart(function_call=function_call),
            FakePart(text="Ignore me"),
        ])]
    )
    _install_fake_client(monkeypatch, response=response)

    llm = llm_module.LLMInterface()
    result, _ = llm.translate_to_query("route", [], [], {})

    assert result == ("plan", {"origin": "Asok", "goal": {"route_to": "Siam"}})


def test_translate_empty_candidates_returns_none(monkeypatch):
    response = SimpleNamespace(candidates=[])
    _install_fake_client(monkeypatch, response=response)

    llm = llm_module.LLMInterface()
    result, history = llm.translate_to_query("x", [], [], {})

    assert result is None
    assert isinstance(history, list)


def test_translate_candidate_no_parts_returns_none(monkeypatch):
    response = SimpleNamespace(
        candidates=[SimpleNamespace(content=SimpleNamespace(parts=[]))]
    )
    _install_fake_client(monkeypatch, response=response)

    llm = llm_module.LLMInterface()
    result, _ = llm.translate_to_query("x", [], [], {})

    assert result is None


def test_translate_exception_returns_none_with_original_history(monkeypatch):
    _install_fake_client(monkeypatch, error=RuntimeError("boom"))

    llm = llm_module.LLMInterface()
    history = [SimpleNamespace(role="user", parts=[])]
    result, out_history = llm.translate_to_query("x", history, [], {})

    assert result is None
    assert out_history is history  # original history returned, not a new list


def test_translate_none_args_survives_coercion(monkeypatch):
    """Gemini can emit a function call with args=None; we must not crash."""
    fc = FakeFunctionCall("plan", None)
    response = SimpleNamespace(
        candidates=[FakeCandidate([FakePart(function_call=fc)])]
    )
    _install_fake_client(monkeypatch, response=response)

    llm = llm_module.LLMInterface()
    result, _ = llm.translate_to_query("x", [], [], {})

    # _args_to_python on None raises AttributeError in the caller; the
    # wrapper swallows exceptions and returns None.
    assert result is None


# ------------------------------------------------------------------
# Vocab + synonym rendering into the system instruction.
# ------------------------------------------------------------------


def test_system_prompt_includes_vocab_and_synonyms(monkeypatch):
    response = SimpleNamespace(
        candidates=[FakeCandidate([FakePart(text="hi")])]
    )
    capture: dict = {}
    _install_fake_client(monkeypatch, response=response, capture=capture)

    llm = llm_module.LLMInterface()
    llm.translate_to_query(
        "hi",
        [],
        vocab=["temple", "museum", "weather_exposed"],
        synonyms={"sweaty": "weather_exposed", "cheap": "budget_friendly"},
    )

    cfg_calls = capture.get("_config_calls", [])
    assert cfg_calls, "GenerateContentConfig was not constructed"
    system_instruction = cfg_calls[-1]["system_instruction"]
    assert "[Active tag vocabulary]" in system_instruction
    assert "temple" in system_instruction
    assert "weather_exposed" in system_instruction
    assert "[Active synonyms" in system_instruction
    assert "sweaty" in system_instruction
    assert "budget_friendly" in system_instruction


def test_system_prompt_omits_vocab_section_when_empty(monkeypatch):
    response = SimpleNamespace(
        candidates=[FakeCandidate([FakePart(text="hi")])]
    )
    capture: dict = {}
    _install_fake_client(monkeypatch, response=response, capture=capture)

    llm = llm_module.LLMInterface()
    llm.translate_to_query("hi", [], vocab=None, synonyms=None)

    cfg_calls = capture.get("_config_calls", [])
    system_instruction = cfg_calls[-1]["system_instruction"]
    # With no vocab/synonyms to append, the system instruction should be
    # exactly the static prompt — no dynamic render suffix.
    assert system_instruction == llm.static_prompt


# ------------------------------------------------------------------
# format_result: narrate a structured result.
# ------------------------------------------------------------------


def test_format_result_injects_answer(monkeypatch):
    response = SimpleNamespace(
        candidates=[FakeCandidate([FakePart(text="From Asok to Siam: ~6 min.")])],
        text="From Asok to Siam: ~6 min.",
    )
    _install_fake_client(monkeypatch, response=response)

    llm = llm_module.LLMInterface()
    result_in = {
        "type": "plan",
        "data": {
            "origin": "Asok (E4)",
            "destination": "Siam (CEN)",
            "total_time": 6,
            "steps": [],
        },
    }
    result_out, history = llm.format_result(result_in, [], [], {})

    assert result_out["data"]["answer"] == "From Asok to Siam: ~6 min."
    assert isinstance(history, list)


def test_format_result_exception_sets_answer_none(monkeypatch):
    _install_fake_client(monkeypatch, error=RuntimeError("boom"))

    llm = llm_module.LLMInterface()
    result_out, _ = llm.format_result({"type": "plan", "data": {}}, [], [], {})

    assert result_out["data"]["answer"] is None
