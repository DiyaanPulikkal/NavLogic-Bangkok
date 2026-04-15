"""
tests/test_ontology.py — ontology.pl correctness tests.

Locks in the load-bearing cut semantics of `bind_tag/2`, the
reflexive-transitive closure of `is_a/2`, and the open-vocabulary
surface (`synonym/2`, `active_tag_vocabulary`). These are the rules
that make the audit/relax loops sound; a regression here corrupts
every downstream proof.
"""

from engine.prolog import PrologInterface


# ------------------------------------------------------------------
# bind_tag/2 — three clauses, two cuts, deterministic everywhere.
# ------------------------------------------------------------------


class TestBindTag:
    def test_bind_synonym_resolves_to_canonical(self):
        """Clause 1: a known synonym binds to its canonical tag."""
        p = PrologInterface()
        results = list(p.prolog.query("bind_tag(sweaty, B)"))
        assert len(results) == 1
        assert results[0]["B"] == "weather_exposed"

    def test_bind_self_for_known_canonical(self):
        """Clause 2: a canonical tag binds to itself."""
        p = PrologInterface()
        results = list(p.prolog.query("bind_tag(museum, B)"))
        assert len(results) == 1
        assert results[0]["B"] == "museum"

    def test_bind_unknown_wraps_with_unknown_functor(self):
        """Clause 3: a novel word becomes unknown(Raw)."""
        p = PrologInterface()
        results = list(p.prolog.query("bind_tag(blorpatron, B)"))
        assert len(results) == 1
        assert str(results[0]["B"]) == "unknown(blorpatron)"

    def test_bind_is_deterministic_for_synonym(self):
        """The cut on clause 1 must prevent fallback into clause 2/3.

        This is the regression guard: if the cut were missing, 'sweaty'
        would also yield unknown(sweaty) on backtracking. We assert
        EXACTLY one solution.
        """
        p = PrologInterface()
        results = list(p.prolog.query("bind_tag(sweaty, B)"))
        assert len(results) == 1

    def test_bind_is_deterministic_for_self(self):
        """The cut on clause 2 must prevent fallback into clause 3."""
        p = PrologInterface()
        results = list(p.prolog.query("bind_tag(temple, B)"))
        assert len(results) == 1
        assert results[0]["B"] == "temple"

    def test_bind_aesthetic_resolves_to_photogenic(self):
        """Open-vocabulary: 'aesthetic' is a synonym for photogenic."""
        p = PrologInterface()
        results = list(p.prolog.query("bind_tag(aesthetic, B)"))
        assert len(results) == 1
        assert results[0]["B"] == "photogenic"


# ------------------------------------------------------------------
# is_a/2 — reflexive-transitive closure of subtag/2.
# ------------------------------------------------------------------


class TestIsA:
    def test_reflexive(self):
        p = PrologInterface()
        assert list(p.prolog.query("is_a(temple, temple)")) != []

    def test_direct_subtag(self):
        p = PrologInterface()
        assert list(p.prolog.query("is_a(temple, religious_site)")) != []

    def test_transitive_chain(self):
        """temple → religious_site → cultural — subsumption crosses hops."""
        p = PrologInterface()
        assert list(p.prolog.query("is_a(temple, cultural)")) != []

    def test_transitive_through_market(self):
        """night_market → market → shopping."""
        p = PrologInterface()
        assert list(p.prolog.query("is_a(night_market, shopping)")) != []

    def test_non_subsumption_fails(self):
        """Unrelated tags must not match."""
        p = PrologInterface()
        assert list(p.prolog.query("is_a(temple, nightlife)")) == []

    def test_outdoor_is_weather_exposed(self):
        """The rule that powers the audit-route violation path."""
        p = PrologInterface()
        assert list(p.prolog.query("is_a(outdoor, weather_exposed)")) != []


# ------------------------------------------------------------------
# Vocabulary surface.
# ------------------------------------------------------------------


class TestVocabularyExport:
    def test_canonical_tag_in_vocab(self):
        p = PrologInterface()
        vocab = set(p.active_tag_vocabulary())
        assert "temple" in vocab or "museum" in vocab
        assert "weather_exposed" in vocab

    def test_synonym_target_in_vocab(self):
        """Every synonym's canonical must appear in the exported vocab."""
        p = PrologInterface()
        vocab = set(p.active_tag_vocabulary())
        for _raw, canon in p.active_synonyms().items():
            assert canon in vocab, f"missing canonical {canon!r} in vocab"

    def test_synonym_map_nonempty(self):
        p = PrologInterface()
        syns = p.active_synonyms()
        assert len(syns) > 0
        assert syns.get("sweaty") == "weather_exposed"
        assert syns.get("aesthetic") == "photogenic"
