import builtins

import main as main_module


class StubOrchestrator:
    def __init__(self):
        self.calls = []

    def handle(self, user_input):
        self.calls.append(user_input)
        return "OK"


def make_input(responses, error_on_end=None):
    iterator = iter(responses)

    def _input(_prompt):
        try:
            return next(iterator)
        except StopIteration:
            if error_on_end:
                raise error_on_end
            raise EOFError

    return _input


def test_main_exit_path(monkeypatch, capsys):
    monkeypatch.setattr(main_module, "Orchestrator", StubOrchestrator)
    monkeypatch.setattr(builtins, "input", make_input(["", "exit"]))

    main_module.main()
    output = capsys.readouterr().out
    assert "Bangkok Public Transport Assistant" in output
    assert "Goodbye!" in output


def test_main_normal_flow(monkeypatch, capsys):
    monkeypatch.setattr(main_module, "Orchestrator", StubOrchestrator)
    monkeypatch.setattr(builtins, "input", make_input(["Hello", "exit"]))

    main_module.main()
    output = capsys.readouterr().out
    assert "Assistant:" in output


def test_main_eof_exit(monkeypatch, capsys):
    monkeypatch.setattr(main_module, "Orchestrator", StubOrchestrator)
    monkeypatch.setattr(builtins, "input", make_input([], error_on_end=EOFError()))

    main_module.main()
    output = capsys.readouterr().out
    assert "Goodbye!" in output

