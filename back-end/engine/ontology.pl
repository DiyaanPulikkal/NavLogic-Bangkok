/*
====================================================================
ontology.pl — Tag taxonomy + open-vocabulary binding layer.

This is the "thinking" layer of the Prolog rulebook. It contains
three things and three things only:

  1. subtag/2 — directed subsumption edges between tags. The
     reflexive-transitive closure is_a/2 derives the rest.
  2. synonym/2 — alias map from raw natural-language strings (as the
     LLM might emit them) to canonical KB tags. This is the
     open-vocabulary surface: extending the system to understand a
     new colloquialism is one fact, never a rule change.
  3. bind_tag/2 — the binding rule. Cuts here are load-bearing; see
     the comment block above the predicate for the full invariant.

The rulebook (rules.pl) calls bind_tag/2 every time it touches a tag
literal that came from outside the KB. By concentrating all
open-vocabulary handling in one predicate, callers stay free of
ad-hoc string fixups.
====================================================================
*/

:- discontiguous subtag/2.
:- discontiguous synonym/2.

/* ------------------------------------------------------------------
   Tag subsumption (DAG)

   Convention: subtag(Specific, General) — read as "Specific IS-A
   General". So `subtag(temple, religious_site)` says every temple
   is a religious_site, and a query for religious_site matches any
   POI tagged temple.
------------------------------------------------------------------ */

subtag(temple,        religious_site).
subtag(shrine,        religious_site).
subtag(mosque,        religious_site).
subtag(church,        religious_site).

subtag(temple,        cultural).
subtag(museum,        cultural).
subtag(art_gallery,   cultural).
subtag(historic,      cultural).
subtag(religious_site, cultural).

subtag(rooftop_bar,   nightlife).
subtag(club,          nightlife).
subtag(bar_street,    nightlife).
subtag(night_market,  nightlife).

subtag(night_market,  market).
subtag(market,        shopping).
subtag(mall,          shopping).
subtag(street_food,   food).

subtag(park,          outdoor).
subtag(walking_heavy, mobility_demanding).
subtag(stairs,        mobility_demanding).
subtag(outdoor,       weather_exposed).
subtag(open_air,      weather_exposed).
subtag(loud_music,    high_noise).
subtag(crowded,       high_density).

/* Reflexive-transitive closure of subtag/2.
   is_a(T, T) — every tag is itself.
   is_a(T, U) — T is a U if there is a chain T → V → ... → U.
*/
is_a(T, T).
is_a(T, U) :- subtag(T, V), is_a(V, U).

/* ------------------------------------------------------------------
   Synonyms (the open-vocabulary surface)

   Read as: synonym(RawPhrase, CanonicalTag). The first argument is
   what the LLM might output verbatim; the second is the tag the
   rulebook reasons over. Add a row to teach the system a new way
   of saying something — no code change required.
------------------------------------------------------------------ */

synonym('shrine',                 shrine).
synonym('place of worship',       religious_site).
synonym('religious place',        religious_site).
synonym('religious_site',         religious_site).

synonym('hot',                    weather_exposed).
synonym('sweaty',                 weather_exposed).
synonym('in the heat',            weather_exposed).
synonym('sun',                    weather_exposed).
synonym('sunny',                  weather_exposed).

synonym('walking',                mobility_demanding).
synonym('a lot of walking',       mobility_demanding).
synonym('hate walking',           mobility_demanding).
synonym('mobility',               mobility_demanding).

synonym('cheap',                  budget_friendly).
synonym('affordable',             budget_friendly).
synonym('budget',                 budget_friendly).

synonym('quiet',                  low_noise).
synonym('chill',                  low_noise).
synonym('calm',                   low_noise).
synonym('noisy',                  high_noise).
synonym('loud',                   high_noise).

synonym('crowded',                high_density).
synonym('avoid crowds',           high_density).
synonym('packed',                 high_density).
synonym('busy',                   high_density).

synonym('photogenic',             photogenic).
synonym('instagrammable',         photogenic).
synonym('aesthetic',              photogenic).
synonym('pretty',                 photogenic).

synonym('food',                   food).
synonym('eat',                    food).
synonym('eating',                 food).
synonym('drinks',                 nightlife).
synonym('go out',                 nightlife).
synonym('night out',              nightlife).
synonym('nightlife',              nightlife).

synonym('temples',                temple).
synonym('temple',                 temple).
synonym('museums',                museum).
synonym('museum',                 museum).
synonym('shopping',               shopping).
synonym('shop',                   shopping).
synonym('mall',                   mall).
synonym('malls',                  mall).
synonym('park',                   park).
synonym('parks',                  park).
synonym('rooftop',                rooftop_bar).
synonym('rooftop bar',            rooftop_bar).
synonym('night market',           night_market).
synonym('street food',            street_food).
synonym('aircon',                 aircon).
synonym('air-conditioned',        aircon).
synonym('air conditioning',       aircon).
synonym('indoor',                 indoor).
synonym('indoors',                indoor).
synonym('outdoor',                outdoor).
synonym('outdoors',               outdoor).
synonym('historic',               historic).
synonym('historical',             historic).
synonym('cultural',               cultural).
synonym('culture',                cultural).
synonym('art',                    art_gallery).
synonym('art gallery',            art_gallery).
synonym('club',                   club).
synonym('clubbing',               club).
synonym('bars',                   bar_street).
synonym('evening',                evening).
synonym('night',                  evening).
synonym('premium',                premium).
synonym('luxury',                 premium).

/* ------------------------------------------------------------------
   Tag binding (the open-to-closed bridge)

   known_tag/1: a tag is "known" if it appears anywhere in subtag/2
   (as either argument) or as the canonical of some synonym. This
   lets us recognize tags that have no IS-A children but are still
   first-class (e.g., `aircon`, `indoor`, `evening`, `premium`).
------------------------------------------------------------------ */

known_tag(T) :- subtag(T, _).
known_tag(T) :- subtag(_, T).
known_tag(T) :- synonym(_, T).

/* Atom/string normalization.
   pyswip can pass either an atom or a string depending on the
   serialization path. We normalize once at the boundary so every
   downstream lookup (synonym/known_tag) sees an atom.
*/
to_atom(X, X) :- atom(X), !.
to_atom(X, A) :- string(X), !, atom_string(A, X).

/* ------------------------------------------------------------------
   bind_tag/2 — the load-bearing predicate.

   Three clauses. Two cuts. Determinism is the invariant.

   Clause 1 — synonym binding.
     If the raw tag has a synonym entry, bind through it. The cut
     commits this branch and prevents Prolog from ever falling
     through to clauses 2 or 3 on backtracking, even if a downstream
     caller fails. This is what makes the audit/relax loops sound:
     "weather_exposed" must ALWAYS bind the same way for a given
     raw input across the whole proof.

   Clause 2 — self binding.
     If the raw tag is already in the ontology, it binds to itself.
     The cut prevents fallback into the unknown(_) clause.

   Clause 3 — unknown wrapping.
     Reachable only when both prior clauses' guards fail
     deterministically. Returns unknown(Raw) so the orchestrator's
     pre-flight (unknown_tags/2 in rules.pl) can surface the
     missing vocabulary back to the LLM rather than silently
     dropping it.

   Because of the cuts, bind_tag/2 is deterministic in every
   reachable mode. once/1 at call sites is redundant.
------------------------------------------------------------------ */

bind_tag(Raw, Bound) :- to_atom(Raw, A), synonym(A, Bound), !.
bind_tag(Raw, A)     :- to_atom(Raw, A), known_tag(A), !.
bind_tag(Raw, unknown(Raw)).

/* ==================================================================
   Temporal specs (closed-vocabulary time layer)

   time_matches(Spec, Time) succeeds when the given concrete Time
   term — a compound t(Weekday, Hour, Minute) emitted by Python —
   falls within the temporal window named by Spec.

   Why a closed vocabulary: temporal specs are a finite taxonomy
   (morning/afternoon/weekend/…) the LLM chooses from, not a free
   surface the user types. Keeping the list closed lets the prompt
   teach the LLM every option. Tags remain open-vocabulary; only
   the temporal layer is enumerated.

   Adding a new spec is one or more rules here. satisfies/3 never
   changes when the temporal vocabulary grows.
================================================================== */

:- discontiguous time_matches/2.

/* Coarse dayparts */
time_matches(morning,        t(_, H, _)) :- H >= 6,  H < 12.
time_matches(afternoon,      t(_, H, _)) :- H >= 12, H < 17.
time_matches(evening,        t(_, H, _)) :- H >= 17, H < 22.
time_matches(late_night,     t(_, H, _)) :- H >= 22.
time_matches(late_night,     t(_, H, _)) :- H >= 0, H < 4.

/* Sunset-anchored (Bangkok is roughly 18:00 year-round) */
time_matches(after_sunset,   t(_, H, _)) :- H >= 18.
time_matches(after_sunset,   t(_, H, _)) :- H >= 0, H < 4.
time_matches(before_sunset,  t(_, H, _)) :- H >= 4, H < 18.

/* Mealtime windows */
time_matches(lunch,          t(_, H, _)) :- H >= 11, H =< 14.

/* Weekday pivots */
time_matches(weekend, t(sat, _, _)).
time_matches(weekend, t(sun, _, _)).
time_matches(weekday, t(mon, _, _)).
time_matches(weekday, t(tue, _, _)).
time_matches(weekday, t(wed, _, _)).
time_matches(weekday, t(thu, _, _)).
time_matches(weekday, t(fri, _, _)).

/* Per-weekday atoms (for queries like "on Saturday") */
time_matches(monday,    t(mon, _, _)).
time_matches(tuesday,   t(tue, _, _)).
time_matches(wednesday, t(wed, _, _)).
time_matches(thursday,  t(thu, _, _)).
time_matches(friday,    t(fri, _, _)).
time_matches(saturday,  t(sat, _, _)).
time_matches(sunday,    t(sun, _, _)).

/* Compound windows */
time_matches(friday_evening, t(fri, H, _)) :- H >= 17.
time_matches(saturday_night, t(sat, H, _)) :- H >= 20.
time_matches(saturday_night, t(sun, H, _)) :- H >= 0, H < 4.

/* Vocabulary export — enumerated so Python's active_time_specs/0
   helper returns a stable list without needing distinct/2 or
   setof/3 on rule heads.
*/
time_spec_vocab([morning, afternoon, evening, late_night,
                 after_sunset, before_sunset, lunch,
                 weekend, weekday,
                 monday, tuesday, wednesday, thursday, friday, saturday, sunday,
                 friday_evening, saturday_night]).

known_time_spec(S) :- time_spec_vocab(V), member(S, V).
