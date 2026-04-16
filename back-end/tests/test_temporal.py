"""
tests/test_temporal.py — time-aware ontology, satisfies/3, candidates/3, relax/4.

Locks in the temporal context layer's invariants:

  - time_matches/2 fires correctly for each closed-vocab spec.
  - active_tag/3 facts load as expected.
  - has_temporal_override/2 shadows the unconditional tagged/2 path.
  - satisfies/3 respects time gating.
  - candidates(goal, time_ctx) enumerates only time-valid POIs.
  - relax(goal, time_ctx) drops time-gated conjuncts with a narratable string.

These tests operate directly against the SWI-Prolog engine via pyswip
and exercise the real rulebook (no mocks).
"""

from engine.prolog import PrologInterface


# Concrete time frames used throughout the tests.
SAT_EVENING = {"weekday": "sat", "hour": 20, "minute": 0}
SAT_MORNING = {"weekday": "sat", "hour": 10, "minute": 0}
TUE_MORNING = {"weekday": "tue", "hour": 10, "minute": 0}
FRI_EVENING = {"weekday": "fri", "hour": 19, "minute": 0}
FRI_MORNING = {"weekday": "fri", "hour": 10, "minute": 0}


# ------------------------------------------------------------------
# time_matches/2 — the closed-vocabulary temporal spec layer.
# ------------------------------------------------------------------


class TestTimeMatches:
    """Direct probes of time_matches/2 via the Prolog engine."""

    def _matches(self, spec: str, weekday: str, hour: int, minute: int) -> bool:
        p = PrologInterface()
        safe = spec.replace("'", "\\'")
        query = f"time_matches({safe}, t({weekday},{hour},{minute}))"
        return bool(list(p.prolog.query(query)))

    def test_weekend_only_sat_sun(self):
        assert self._matches("weekend", "sat", 10, 0)
        assert self._matches("weekend", "sun", 10, 0)
        assert not self._matches("weekend", "fri", 23, 0)
        assert not self._matches("weekend", "mon", 0, 0)

    def test_weekday_excludes_sat_sun(self):
        for wd in ("mon", "tue", "wed", "thu", "fri"):
            assert self._matches("weekday", wd, 10, 0)
        assert not self._matches("weekday", "sat", 10, 0)
        assert not self._matches("weekday", "sun", 10, 0)

    def test_after_sunset_wraps_past_midnight(self):
        """`after_sunset` covers [18, 24) AND [0, 4) so "Saturday at 1 AM"
        still falls inside. This is the reason there are two clauses."""
        assert self._matches("after_sunset", "sat", 18, 0)
        assert self._matches("after_sunset", "sat", 23, 59)
        assert self._matches("after_sunset", "sun", 2, 0)
        assert not self._matches("after_sunset", "sat", 17, 59)
        assert not self._matches("after_sunset", "sat", 12, 0)

    def test_before_sunset(self):
        assert self._matches("before_sunset", "sat", 4, 0)
        assert self._matches("before_sunset", "sat", 17, 59)
        assert not self._matches("before_sunset", "sat", 18, 0)
        assert not self._matches("before_sunset", "sat", 2, 0)

    def test_friday_evening_only_fri_after_17(self):
        assert self._matches("friday_evening", "fri", 17, 0)
        assert self._matches("friday_evening", "fri", 23, 0)
        assert not self._matches("friday_evening", "fri", 16, 59)
        assert not self._matches("friday_evening", "sat", 20, 0)
        assert not self._matches("friday_evening", "thu", 20, 0)

    def test_morning_afternoon_evening_partition(self):
        assert self._matches("morning", "mon", 6, 0)
        assert self._matches("morning", "mon", 11, 59)
        assert self._matches("afternoon", "mon", 12, 0)
        assert self._matches("afternoon", "mon", 16, 59)
        assert self._matches("evening", "mon", 17, 0)
        assert self._matches("evening", "mon", 21, 59)
        assert self._matches("late_night", "mon", 22, 0)
        assert self._matches("late_night", "mon", 3, 0)

    def test_per_weekday_atoms(self):
        assert self._matches("monday", "mon", 10, 0)
        assert not self._matches("monday", "tue", 10, 0)
        assert self._matches("saturday", "sat", 23, 0)


# ------------------------------------------------------------------
# active_tag/3 facts and the override-wins shadowing semantics.
# ------------------------------------------------------------------


class TestActiveTagFacts:
    def test_active_tag_loaded(self):
        p = PrologInterface()
        # Jodd Fairs has two override facts.
        rows = list(p.prolog.query(
            "active_tag(jodd_fairs, T, S)"
        ))
        pairs = {(str(r["T"]), str(r["S"])) for r in rows}
        assert ("high_density", "after_sunset") in pairs
        assert ("night_market", "after_sunset") in pairs

    def test_has_temporal_override_detects_gated_tag(self):
        p = PrologInterface()
        res = list(p.prolog.query(
            "has_temporal_override(jodd_fairs, high_density)"
        ))
        assert res, "jodd_fairs / high_density has an active_tag row"

    def test_has_temporal_override_absent_for_ungated_tag(self):
        p = PrologInterface()
        # jodd_fairs has budget_friendly in tagged/2 but NO active_tag row.
        res = list(p.prolog.query(
            "has_temporal_override(jodd_fairs, budget_friendly)"
        ))
        assert not res

    def test_override_shadows_unconditional_tag(self):
        """The double-source invariant: if active_tag exists for (Poi, Tag),
        the unconditional tagged/2 path is disabled. Otherwise a time-gated
        tag that ALSO appears in tagged/2 would silently no-op."""
        p = PrologInterface()
        # jodd_fairs has high_density in tagged/2 AND active_tag(..., after_sunset).
        # At TUE_MORNING (10 AM), high_density must NOT match.
        query = (
            "tag_active_at(jodd_fairs, high_density, "
            "t(tue, 10, 0))"
        )
        assert not list(p.prolog.query(query))

    def test_override_fires_when_spec_matches(self):
        p = PrologInterface()
        query = (
            "tag_active_at(jodd_fairs, high_density, "
            "t(sat, 22, 0))"
        )
        assert list(p.prolog.query(query))

    def test_ungated_tag_still_matches(self):
        """budget_friendly on jodd_fairs has NO override and must match
        at any time — the override layer is purely additive."""
        p = PrologInterface()
        for wd, h in (("tue", 10), ("sat", 22), ("mon", 3)):
            query = (
                f"tag_active_at(jodd_fairs, budget_friendly, t({wd}, {h}, 0))"
            )
            assert list(p.prolog.query(query)), \
                f"budget_friendly must match at {wd} {h}:00"


# ------------------------------------------------------------------
# candidates(goal, time_ctx) — the headline temporal query.
# ------------------------------------------------------------------


class TestTimeAwareCandidates:
    def test_jodd_fairs_fires_after_sunset(self):
        p = PrologInterface()
        results = p.candidates({"any_tag": ["night_market"]}, SAT_EVENING)
        names = {c["name"] for c in results}
        assert "Jodd Fairs Night Market" in names

    def test_jodd_fairs_silent_before_sunset(self):
        p = PrologInterface()
        results = p.candidates({"any_tag": ["night_market"]}, SAT_MORNING)
        names = {c["name"] for c in results}
        assert "Jodd Fairs Night Market" not in names
        # asiatique is also after_sunset-gated; ditto.
        assert "Asiatique The Riverfront" not in names

    def test_chatuchak_weekend_only(self):
        p = PrologInterface()
        # Saturday 10 AM: weekend=YES → chatuchak high_density fires.
        sat_results = p.candidates({"any_tag": ["high_density"]}, SAT_MORNING)
        assert "Chatuchak Weekend Market" in {c["name"] for c in sat_results}
        # Tuesday 10 AM: weekend=NO → chatuchak silent.
        tue_results = p.candidates({"any_tag": ["high_density"]}, TUE_MORNING)
        assert "Chatuchak Weekend Market" not in {c["name"] for c in tue_results}

    def test_wat_arun_photogenic_only_after_sunset(self):
        p = PrologInterface()
        # Tuesday 10 AM: wat_arun's photogenic is shadowed → silent.
        day = p.candidates({"any_tag": ["photogenic"]}, TUE_MORNING)
        assert "Wat Arun" not in {c["name"] for c in day}
        # Saturday 20:00: override matches → Wat Arun fires.
        night = p.candidates({"any_tag": ["photogenic"]}, SAT_EVENING)
        assert "Wat Arun" in {c["name"] for c in night}

    def test_rca_friday_evening_only(self):
        p = PrologInterface()
        # Friday 19:00: friday_evening matches → RCA has loud_music.
        fri_pm = p.candidates({"any_tag": ["loud_music"]}, FRI_EVENING)
        assert "RCA" in {c["name"] for c in fri_pm}
        # Friday 10:00: RCA's override fails → RCA silent.
        fri_am = p.candidates({"any_tag": ["loud_music"]}, FRI_MORNING)
        assert "RCA" not in {c["name"] for c in fri_am}

    def test_unconditional_temple_unaffected_by_time(self):
        """Wat Pho has no active_tag overrides; it must match at any time."""
        p = PrologInterface()
        for tc in (SAT_EVENING, SAT_MORNING, TUE_MORNING, FRI_EVENING):
            names = {c["name"] for c in p.candidates({"any_tag": ["temple"]}, tc)}
            assert "Wat Pho" in names


# ------------------------------------------------------------------
# relax(goal, time_ctx) — surfaces time-gated conjuncts.
# ------------------------------------------------------------------


class TestTimeAwareRelax:
    def test_relax_drops_time_gated_conjunct(self):
        """At Tue 10 AM, night_market-gated POIs are all silent. A conjunction
        pairing night_market with shopping must relax by dropping the
        night_market literal and surfacing unconditional shopping POIs."""
        p = PrologInterface()
        goal = {
            "and": [
                {"any_tag": ["night_market"]},
                {"any_tag": ["shopping"]},
            ]
        }
        assert p.candidates(goal, TUE_MORNING) == []
        relaxed = p.relax(goal, TUE_MORNING)
        assert relaxed is not None
        dropped, survivors = relaxed
        assert any("night_market" in d for d in dropped)
        assert len(survivors) > 0
