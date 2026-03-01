from types import SimpleNamespace

import engine.llm.llm as llm_module


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
    def __init__(self, response=None, error=None):
        self._response = response
        self._error = error
        self.models = SimpleNamespace(generate_content=self._generate_content)

    def _generate_content(self, **_kwargs):
        if self._error:
            raise self._error
        return self._response


def setup_llm(monkeypatch, response=None, error=None):
    monkeypatch.setattr(llm_module.genai, "Client", lambda: FakeClient(response, error))
    monkeypatch.setattr(llm_module.types, "Tool", lambda **_kwargs: object())
    monkeypatch.setattr(llm_module.types, "GenerateContentConfig", lambda **_kwargs: object())


def test_translate_to_query_function_call(monkeypatch):
    function_call = FakeFunctionCall("line_of", {"station_name": "Siam"})
    response = SimpleNamespace(
        candidates=[FakeCandidate([FakePart(function_call=function_call)])]
    )
    setup_llm(monkeypatch, response=response)

    llm = llm_module.LLMInterface()
    result, history = llm.translate_to_query("line", [])

    assert result == ("line_of", {"station_name": "Siam"})
    assert isinstance(history, list)


def test_translate_to_query_text_response(monkeypatch):
    response = SimpleNamespace(
        candidates=[FakeCandidate([FakePart(text="Hello there!")])]
    )
    setup_llm(monkeypatch, response=response)

    llm = llm_module.LLMInterface()
    result, history = llm.translate_to_query("hello", [])

    assert result == "Hello there!"
    assert isinstance(history, list)


def test_translate_to_query_no_function_call(monkeypatch):
    response = SimpleNamespace(candidates=[FakeCandidate([FakePart()])])
    setup_llm(monkeypatch, response=response)

    llm = llm_module.LLMInterface()
    result, history = llm.translate_to_query("line", [])
    assert result is None


def test_translate_to_query_exception(monkeypatch):
    setup_llm(monkeypatch, error=RuntimeError("boom"))

    llm = llm_module.LLMInterface()
    result, history = llm.translate_to_query("line", [])
    assert result is None
    assert isinstance(history, list)
