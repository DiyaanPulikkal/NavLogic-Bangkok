"""
tests/test_relaxation.py — minimal-drop relaxation over conjunctive goals.

When `candidates(goal)` is empty, `relax/3` searches for the smallest
subset of conjuncts to drop such that the remaining conjunction is
satisfied. These tests lock in:

  - The minimal-drop invariant (we never drop more than we must).
  - Non-empty survivor set after a successful drop.
  - `None` return for goals that can't relax into anything.
  - Shape of the returned pair ([dropped-subgoal-strings], [survivors]).
"""

from engine.prolog import PrologInterface
from tests.helpers import DEFAULT_TIME_CTX


class TestRelaxDrops:
    def test_unsatisfiable_conjunction_relaxes(self):
        """temple ∧ nightlife has no candidates — relax must fire."""
        p = PrologInterface()
        goal = {
            "and": [
                {"any_tag": ["temple"]},
                {"any_tag": ["nightlife"]},
            ]
        }
        assert p.candidates(goal, DEFAULT_TIME_CTX) == []
        relaxed = p.relax(goal, DEFAULT_TIME_CTX)
        assert relaxed is not None
        dropped, survivors = relaxed
        assert len(dropped) >= 1
        assert len(survivors) > 0

    def test_dropped_strings_shape(self):
        """Each dropped conjunct comes back as a Prolog-term string."""
        p = PrologInterface()
        goal = {
            "and": [
                {"any_tag": ["temple"]},
                {"any_tag": ["nightlife"]},
            ]
        }
        relaxed = p.relax(goal, DEFAULT_TIME_CTX)
        assert relaxed is not None
        dropped, _ = relaxed
        for d in dropped:
            assert isinstance(d, str)
            # Must name one of the original conjuncts.
            assert "temple" in d or "nightlife" in d

    def test_survivors_have_candidate_shape(self):
        """Survivors use the {name, station, pref_score} shape."""
        p = PrologInterface()
        goal = {
            "and": [
                {"any_tag": ["temple"]},
                {"any_tag": ["nightlife"]},
            ]
        }
        _dropped, survivors = p.relax(goal, DEFAULT_TIME_CTX)
        for s in survivors:
            assert set(s.keys()) == {"name", "station", "pref_score"}
            assert isinstance(s["pref_score"], int)

    def test_minimal_drop_is_single_conjunct(self):
        """If dropping one conjunct satisfies the rest, only one is dropped."""
        p = PrologInterface()
        # Dropping either 'museum' or {nightlife, budget_friendly} should
        # restore candidates. The minimal-drop search should not drop the
        # whole goal.
        goal = {
            "and": [
                {"any_tag": ["museum"]},
                {"all_tag": ["nightlife", "budget_friendly"]},
            ]
        }
        relaxed = p.relax(goal, DEFAULT_TIME_CTX)
        assert relaxed is not None
        dropped, _ = relaxed
        # Minimal drop ⇒ dropped list never contains *both* original conjuncts.
        assert len(dropped) < 2

    def test_time_gated_conjunct_is_relaxable(self):
        """At Tue 10:00, night_market-gated POIs (jodd_fairs, asiatique) are
        silent because after_sunset fails. A goal joining night_market with an
        unconditional shopping filter should relax by dropping the night_market
        conjunct and surfacing unconditional shopping POIs."""
        p = PrologInterface()
        goal = {
            "and": [
                {"any_tag": ["night_market"]},
                {"any_tag": ["shopping"]},
            ]
        }
        tue_morning = {"weekday": "tue", "hour": 10, "minute": 0}
        assert p.candidates(goal, tue_morning) == []
        relaxed = p.relax(goal, tue_morning)
        assert relaxed is not None
        dropped, survivors = relaxed
        assert any("night_market" in d for d in dropped)
        assert len(survivors) > 0


class TestRelaxNone:
    def test_route_to_nonexistent_returns_none(self):
        """route_to can't be relaxed to something meaningful."""
        p = PrologInterface()
        assert p.relax({"route_to": "Narnia (XX)"}, DEFAULT_TIME_CTX) is None

    def test_already_satisfied_goal_still_relaxes_or_noops(self):
        """A goal that already has candidates either returns None or some
        relaxation — both are acceptable. Just assert no crash."""
        p = PrologInterface()
        goal = {"any_tag": ["temple"]}
        # No assertion on result — relax may or may not fire on a satisfied
        # goal; we only verify it doesn't raise and returns a valid shape.
        result = p.relax(goal, DEFAULT_TIME_CTX)
        if result is not None:
            dropped, survivors = result
            assert isinstance(dropped, list)
            assert isinstance(survivors, list)
