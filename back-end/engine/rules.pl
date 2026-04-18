/*
====================================================================
rules.pl — The rulebook.

This file contains the IDB (intensional database) of the engine:
the predicates that derive answers from the EDB facts in
knowledge_base.pl. It is consulted from knowledge_base.pl, which
itself first consults ontology.pl. The dependency order is:

    ontology.pl  ──>  rules.pl  ──>  knowledge_base.pl

Three responsibilities live here:

  1. Symbolic name resolution      — match_station/3
  2. Path → ride/transfer steps    — route_steps/2 + helpers
  3. Logical-form reasoning        — satisfies/3, candidates/3,
                                     preference_score/4, relax/4,
                                     audit_route/3, unknown_tags/2

  The third group threads a Time argument (a t(Weekday, Hour, Minute)
  compound) through every tag check, so time-gated POI facts
  (active_tag/3 in knowledge_base.pl) contribute conditionally. The
  time layer is closed-vocabulary (see ontology.pl); the goal grammar
  and tag vocabulary remain open.

The first two are kept because they are genuine symbolic work that
would be ugly in Python. The third is the neuro-symbolic core: the
LLM emits a recursive goal tree over open vocabulary, and Prolog
evaluates it under the open-vocabulary binding established in
ontology.pl.
====================================================================
*/

/* ==================================================================
   1. Station name matching (symbolic classification)

   Three clauses, mutually exclusive by construction. Callers in
   Python rank by match-type priority then string similarity.
================================================================== */

match_station(Input, Station, exact) :-
    downcase_atom(Input, IL),
    station(Station, _),
    downcase_atom(Station, SL),
    IL = SL.

match_station(Input, Station, prefix) :-
    downcase_atom(Input, IL),
    station(Station, _),
    downcase_atom(Station, SL),
    \+ IL = SL,
    sub_atom(SL, 0, _, _, IL).

match_station(Input, Station, substring) :-
    downcase_atom(Input, IL),
    station(Station, _),
    downcase_atom(Station, SL),
    \+ IL = SL,
    \+ sub_atom(SL, 0, _, _, IL),
    sub_atom(SL, _, _, _, IL).

/* ==================================================================
   2. Path → ride/transfer step segmentation

   Given an ordered station list (e.g. from Python's Dijkstra),
   produce a list of step terms that group consecutive stations on
   the same line into a single ride/4 and emit transfer/2 between
   line changes.

   This is genuine structural recursion — the kind of thing Prolog
   does cleanly and Python does messily.
================================================================== */

line_display_name(bts_sukhumvit,    'BTS Sukhumvit Line').
line_display_name(bts_silom,        'BTS Silom Line').
line_display_name(gold,             'BTS Gold Line').
line_display_name(mrt_blue,         'MRT Blue Line').
line_display_name(airport_rail_link,'Airport Rail Link').
line_display_name(transfer_walk,    'Walk').

shared_line(StationA, StationB, Line) :-
    station(StationA, Line),
    station(StationB, Line).

route_steps([], []).
route_steps([_], []).
route_steps([A, B | Rest], Steps) :-
    (   shared_line(A, B, Line)
    ->  extend_ride(Line, A, [A, B], [B | Rest], Steps)
    ;   Steps = [transfer(A, B) | RestSteps],
        route_steps([B | Rest], RestSteps)
    ).

extend_ride(Line, Board, Acc, [Last], [ride(Display, Board, Last, Acc)]) :-
    line_display_name(Line, Display).
extend_ride(Line, Board, Acc, [C, D | Rest], Steps) :-
    (   shared_line(C, D, Line)
    ->  append(Acc, [D], NewAcc),
        extend_ride(Line, Board, NewAcc, [D | Rest], Steps)
    ;   line_display_name(Line, Display),
        Steps = [ride(Display, Board, C, Acc) | RestSteps],
        route_steps([C, D | Rest], RestSteps)
    ).

/* ==================================================================
   3. Logical-form reasoning (the open-vocabulary core)
================================================================== */

/* poi_has_tag/2 — unconditional tag membership respecting subsumption.
   A POI tagged `temple` matches a query for `religious_site` because
   subtag(temple, religious_site) is in the ontology.

   This is the always-on baseline. Time-gated membership goes through
   tag_active_at/3 below, which shadows this predicate when an
   active_tag/3 override exists.
*/
poi_has_tag(Poi, Tag) :-
    tagged(Poi, Tags),
    member(T, Tags),
    is_a(T, Tag).

/* ------------------------------------------------------------------
   Temporal tag gating — the override-wins binding layer.

   has_temporal_override(Poi, Tag) is true iff any active_tag/3 row
   exists for the (Poi, Tag) pair (across any spec). When true, the
   unconditional poi_has_tag/2 path is shadowed: ONLY the time-gated
   clauses count. Without this guard, a POI that has both
   `tagged(p, [photogenic])` and `active_tag(p, photogenic, after_sunset)`
   would silently satisfy `photogenic` at 10 AM through the fallback
   branch, making the time-gate a no-op.

   tag_active_at(Poi, Tag, Time) is the predicate every satisfies/3
   tag clause calls. The first clause handles overridden tags (spec
   must match Time); the second delegates to poi_has_tag/2 for tags
   that are not temporally gated.

   Note on subsumption: active_tag/3 is matched at the canonical
   (post-bind_tag) tag level, not propagated up the is_a/2 chain.
   A query for `cultural` against a POI whose only override is
   active_tag(p, temple, evening) will resolve through the
   unconditional poi_has_tag path — the temple-specific time gate
   does not propagate to cultural. All demo overrides target leaf-ish
   tags (high_density, night_market, photogenic, loud_music) so this
   is a deliberate scoping choice, not a bug.
------------------------------------------------------------------ */

has_temporal_override(Poi, Tag) :- active_tag(Poi, Tag, _), !.

tag_active_at(Poi, Tag, Time) :-
    has_temporal_override(Poi, Tag),
    !,
    active_tag(Poi, Tag, Spec),
    time_matches(Spec, Time).
tag_active_at(Poi, Tag, _) :-
    \+ has_temporal_override(Poi, Tag),
    poi_has_tag(Poi, Tag).

/* satisfies/3 — recursive evaluator for goal terms under a Time context.

   Goal grammar (mirrors the JSON the LLM emits, serialized to
   Prolog terms by Python):

     and(Gs)         conjunction
     or(Gs)          disjunction
     not(G)          negation
     any_tag(Ts)     POI has at least one of Ts   (time-gated)
     all_tag(Ts)     POI has every tag in Ts      (time-gated)
     none_tag(Ts)    POI has none of Ts           (time-gated, HARD)
     prefer_tag(Ts)  soft preference              (time-gated scoring)
     route_to(_)     handled by orchestrator, not by candidate filter

   Time is a t(Weekday, Hour, Minute) compound threaded by callers.
   Tags pass through bind_tag/2 (defined in ontology.pl) so synonyms
   and unknown vocabulary are handled uniformly; presence is checked
   via tag_active_at/3 so time-gated overrides take effect.
*/

satisfies(_,   any_tag([]), _) :- fail.
satisfies(Poi, any_tag([T | _Ts]), Time) :-
    bind_tag(T, B),
    \+ B = unknown(_),
    tag_active_at(Poi, B, Time),
    !.
satisfies(Poi, any_tag([_ | Ts]), Time) :-
    satisfies(Poi, any_tag(Ts), Time).

satisfies(_,   all_tag([]), _).
satisfies(Poi, all_tag(Ts), Time) :-
    forall(member(T, Ts),
           ( bind_tag(T, B),
             \+ B = unknown(_),
             tag_active_at(Poi, B, Time) )).

satisfies(_,   none_tag([]), _).
satisfies(Poi, none_tag(Ts), Time) :-
    forall(member(T, Ts),
           ( bind_tag(T, B),
             ( B = unknown(_)
             -> true
             ;  \+ tag_active_at(Poi, B, Time) ) )).

satisfies(Poi, and(Gs), Time) :-
    forall(member(G, Gs), satisfies(Poi, G, Time)).

satisfies(Poi, or(Gs), Time) :-
    member(G, Gs),
    satisfies(Poi, G, Time).

satisfies(Poi, not(G), Time) :-
    \+ satisfies(Poi, G, Time).

satisfies(_, prefer_tag(_), _).   /* preferences never block; scored separately */
satisfies(_, route_to(_),   _).   /* orchestrator handles routing intent */

/* ------------------------------------------------------------------
   Soft preference scoring.

   sub_goal/2 walks a goal AST; preference_score/3 counts how many
   prefer_tag literals across the whole goal a given POI matches.
   Higher is better; orchestrator uses this for ranking.
------------------------------------------------------------------ */

sub_goal(G, G).
sub_goal(and(Gs), Sub) :- member(G, Gs), sub_goal(G, Sub).
sub_goal(or(Gs),  Sub) :- member(G, Gs), sub_goal(G, Sub).
sub_goal(not(G),  Sub) :- sub_goal(G, Sub).

preference_score(Poi, Goal, Time, Score) :-
    findall(1,
            ( sub_goal(Goal, prefer_tag(Ts)),
              member(T, Ts),
              bind_tag(T, B),
              \+ B = unknown(_),
              tag_active_at(Poi, B, Time) ),
            Hits),
    length(Hits, Score).

/* ------------------------------------------------------------------
   candidates/3 — the headline query, time-aware.

   Returns Name-Station-Score for every POI satisfying Goal under
   Time, with its preference score. Empty result triggers relax/4
   in the orchestrator.
------------------------------------------------------------------ */

candidates(Goal, Time, Cands) :-
    findall(Name-Station-Score,
            ( poi(Id, Name, Station),
              satisfies(Id, Goal, Time),
              preference_score(Id, Goal, Time, Score) ),
            Cands).

/* ------------------------------------------------------------------
   Vocabulary check — surfaces unknowns to the orchestrator before
   any reasoning runs. The orchestrator uses this to ask the LLM
   to re-emit the goal with bound vocabulary.

   collect_tags/2 walks a goal AST and gathers every raw tag literal.
   unknown_tags/2 keeps only the ones that bind to unknown(_).
------------------------------------------------------------------ */

collect_tags(any_tag(Ts),    Ts).
collect_tags(all_tag(Ts),    Ts).
collect_tags(none_tag(Ts),   Ts).
collect_tags(prefer_tag(Ts), Ts).
collect_tags(and(Gs), All) :-
    maplist(collect_tags, Gs, Lists),
    append(Lists, All).
collect_tags(or(Gs), All) :-
    maplist(collect_tags, Gs, Lists),
    append(Lists, All).
collect_tags(not(G), Ts) :-
    collect_tags(G, Ts).
collect_tags(route_to(_), []).

/* Note on call shape:
   We call bind_tag/2 with a fresh variable Bound, then test the
   result. Calling bind_tag(Raw, unknown(Raw)) directly with a ground
   second argument would bypass the cuts in clauses 1 and 2 — those
   cuts only fire when the head AND the body unify, so a ground
   `unknown(Raw)` would slide through to clause 3 and falsely report
   bound vocabulary as unknown. The fresh-variable form respects the
   determinism of bind_tag/2 in mode (+, ?).
*/
unknown_tags(Goal, Unknowns) :-
    collect_tags(Goal, AllRaw),
    findall(Raw,
            ( member(Raw, AllRaw),
              bind_tag(Raw, Bound),
              Bound = unknown(_) ),
            Unknowns).

/* ------------------------------------------------------------------
   Constraint relaxation — the "reasoning about incompleteness" move.

   When candidates(Goal, []) holds (no POI satisfies the full goal),
   the orchestrator calls relax/3 to find the smallest set of
   conjuncts whose removal yields at least one candidate. This is
   the closed-world equivalent of "I tried hard, here's what I would
   have to ignore to give you anything."

   Implementation: try dropping one conjunct first; if still empty,
   try dropping pairs. Bounded at two drops to keep the search
   space sane for the demo.
------------------------------------------------------------------ */

relax(and(Gs), Time, [Drop], Survivors) :-
    select(Drop, Gs, Rest),
    candidates(and(Rest), Time, Survivors),
    Survivors \= [].

relax(and(Gs), Time, [D1, D2], Survivors) :-
    select(D1, Gs, R1),
    select(D2, R1, R2),
    candidates(and(R2), Time, Survivors),
    Survivors \= [].

/* ------------------------------------------------------------------
   Route audit — the symbolic-supervises-numeric feedback hook.

   After Python's Dijkstra picks a route and route_steps/2 segments
   it, the orchestrator hands (Steps, Goal) back to Prolog. This
   audit checks the proposed route against the goal's hard
   constraints and reports violations the orchestrator must replan
   around.

   Currently audits two constraint families:

     - none_tag([weather_exposed]) — fires when a transfer step
       walks through a station tagged open_air.
     - none_tag([mobility_demanding]) — fires on any transfer step,
       since transfers always involve walking between platforms.

   New audits are added by extending step_violates/3, not by
   touching audit_route/3.
------------------------------------------------------------------ */

step_violates(transfer(A, _), Goal, weather_exposed) :-
    sub_goal(Goal, none_tag(Ts)),
    member(T, Ts),
    bind_tag(T, weather_exposed),
    station_property(A, open_air).

step_violates(transfer(_, B), Goal, weather_exposed) :-
    sub_goal(Goal, none_tag(Ts)),
    member(T, Ts),
    bind_tag(T, weather_exposed),
    station_property(B, open_air).

step_violates(transfer(_, _), Goal, mobility_demanding) :-
    sub_goal(Goal, none_tag(Ts)),
    member(T, Ts),
    bind_tag(T, mobility_demanding).

audit_route(Steps, Goal, Violations) :-
    findall(violation(Step, Reason),
            ( member(Step, Steps),
              step_violates(Step, Goal, Reason) ),
            Violations).

/* ==================================================================
   4. Fiscal reasoning — per-agency fare model.

   Transit fare in Bangkok is billed per agency journey, not per
   ride segment. A trip that stays within BTS from tap-in to tap-out
   incurs ONE fare regardless of whether it crosses the Siam
   interchange between Sukhumvit and Silom lines. Crossing to a
   DIFFERENT agency (BTS↔MRT at Asok↔Sukhumvit, for example) forces
   a second tap-in and a second fare.

   The model here partitions the station path into maximal same-
   agency runs ("segments"), looks up one fare per run from fares.pl,
   and sums them. Inter-agency crossings become the boundaries on
   which symbolic repair (Section 5) reasons.
================================================================== */

line_agency(bts_sukhumvit,     bts).
line_agency(bts_silom,         bts).
line_agency(mrt_blue,          bem).
line_agency(airport_rail_link, srtet).

station_agency(Station, Agency) :-
    station(Station, Line),
    line_agency(Line, Agency).

/* path_segments(+Path, -Segments)
   Segments = list of segment(Agency, TapIn, TapOut). A segment spans
   the maximal run of consecutive stations sharing an agency. A path
   that only touches an agency at a single boundary station yields a
   degenerate segment(Agency, S, S) that charges 0 via segment_fare/2.
*/
path_segments([], []).
path_segments([S], [segment(A, S, S)]) :-
    station_agency(S, A), !.
path_segments([A | Rest], [segment(Agency, A, End) | More]) :-
    station_agency(A, Agency),
    extend_segment(Agency, A, Rest, End, Tail),
    path_segments(Tail, More).

extend_segment(_, Cur, [], Cur, []).
extend_segment(Agency, _, [Next | Rest], End, Tail) :-
    station_agency(Next, Agency), !,
    extend_segment(Agency, Next, Rest, End, Tail).
extend_segment(_, Cur, Remainder, Cur, Remainder).

/* segment_fare(+Segment, -PriceTHB)
   Degenerate (tap-in == tap-out) segments charge 0.
   Real segments consult fare/4 in either direction. Missing data
   is a hard error: throw fare_unknown/3 so the Python bridge can
   surface it rather than silently under-reporting.
*/
segment_fare(segment(_, S, S), 0) :- !.
segment_fare(segment(Agency, A, B), P) :- fare(Agency, A, B, P), !.
segment_fare(segment(Agency, A, B), P) :- fare(Agency, B, A, P), !.
segment_fare(segment(Agency, A, B), _) :- throw(fare_unknown(Agency, A, B)).

trip_fare(Path, Segments, Total) :-
    path_segments(Path, Segments),
    segments_total(Segments, 0, Total).

segments_total([], Acc, Acc).
segments_total([Seg | Rest], A0, Total) :-
    segment_fare(Seg, P),
    A1 is A0 + P,
    segments_total(Rest, A1, Total).

within_budget(Path, Max) :-
    trip_fare(Path, _, F),
    F =< Max.

/* ==================================================================
   5. Symbolic repair — Prolog diagnoses why a path busted the budget,
   then synthesises a structured constraint to guide Python's next
   Dijkstra iteration. This is the active, deductive counterpart of
   audit_route/3: that one blacklists a POI; this one blacklists an
   edge or an entire agency crossing.

   The repair loop runs in Python (see _budget_repair in
   orchestrator.py); here we supply its three Prolog oracles:
     diagnose_budget/3    — structural failure analysis
     propose_repair/3     — new ground constraint, one of four tiers
     explain_infeasibility/3 — proof-carrying certificate
================================================================== */

/* path_boundaries(+Path, -Boundaries)
   Boundaries = list of boundary(StA, StB, AgencyA, AgencyB), one
   entry per consecutive inter-agency transition along the path.
*/
path_boundaries([], []).
path_boundaries([_], []).
path_boundaries([A, B | Rest], [boundary(A, B, AA, AB) | More]) :-
    station_agency(A, AA),
    station_agency(B, AB),
    AA \= AB, !,
    path_boundaries([B | Rest], More).
path_boundaries([_, B | Rest], More) :-
    path_boundaries([B | Rest], More).

/* diagnose_budget(+Path, +BudgetTHB, -Diagnosis)

   Diagnosis = within_budget(Total)
             | over_budget(Total, Overage, Segments, Boundaries)

   Within-budget paths commit via the cut on the first clause. Over-
   budget paths carry the full structural breakdown so propose_repair/3
   can reason about which boundary to drop first.
*/
diagnose_budget(Path, Budget, within_budget(Total)) :-
    trip_fare(Path, _, Total),
    Total =< Budget, !.
diagnose_budget(Path, Budget, over_budget(Total, Overage, Segs, Bounds)) :-
    trip_fare(Path, Segs, Total),
    Overage is Total - Budget,
    path_boundaries(Path, Bounds).

/* boundary_cost(+Boundary, +Segments, -Contribution)
   The fare of the segment that begins AT this boundary's destination
   station — i.e. how much money this crossing "admitted" into the
   trip. Zero for degenerate segments. Used to rank boundaries so the
   most-expensive crossing is repaired first.
*/
boundary_cost(boundary(_, B, _, AgencyB), Segments, Cost) :-
    member(Seg, Segments),
    Seg = segment(AgencyB, B, _),
    segment_fare(Seg, Cost), !.
boundary_cost(_, _, 0).

rank_boundaries(Bounds, Segs, Sorted) :-
    findall(C-B,
            ( member(B, Bounds),
              boundary_cost(B, Segs, C) ),
            Pairs),
    sort(0, @>=, Pairs, Sorted).

/* propose_repair(+Diagnosis, +AlreadyTried, -Repair)

   Four-tier hierarchy, local-to-global:
     1. avoid_specific_boundary(A, B)    — drop THIS station-pair
     2. avoid_agency_pair(AgencyA, AgencyB) — drop EVERY crossing
                                              of this operator pair
     3. force_single_agency(Agency)      — stay entirely inside one
                                            agency
     4. infeasible(Reason)               — proof-carrying failure

   AlreadyTried is the list of repair terms Python has already applied.
   Each clause skips its repair if the equivalent term is in that list,
   so the loop advances monotonically through the hierarchy.
*/
propose_repair(over_budget(_, _, Segs, Bounds), Tried, Repair) :-
    rank_boundaries(Bounds, Segs, [_-boundary(A, B, _, _) | _]),
    \+ member(avoid_specific_boundary(A, B), Tried),
    Repair = avoid_specific_boundary(A, B), !.

propose_repair(over_budget(_, _, _, Bounds), Tried, Repair) :-
    member(boundary(_, _, AA, AB), Bounds),
    \+ member(avoid_agency_pair(AA, AB), Tried),
    Repair = avoid_agency_pair(AA, AB), !.

propose_repair(over_budget(_, _, Segs, _), Tried, Repair) :-
    member(segment(Agency, _, _), Segs),
    \+ member(force_single_agency(Agency), Tried),
    Repair = force_single_agency(Agency), !.

propose_repair(over_budget(Total, _, _, _), _,
               infeasible(structurally_over_budget(Total))).

/* explain_infeasibility(+RepairTrail, +LastDiagnosis, -Certificate)

   A Certificate is a ground term packaging the reason-chain that
   Python surfaces to the user. Two constructions:
     - over_budget tail          — we exhausted the repair hierarchy
                                   and the last numeric attempt was
                                   still over by Overage baht.
     - graph_disconnected tail   — a repair pruned the graph enough
                                   that no O→D path survives.
*/
explain_infeasibility(Trail,
                      over_budget(Total, Overage, _, _),
                      certificate(repairs_exhausted(Trail),
                                  final_over_by(Overage),
                                  min_seen(Total))).
explain_infeasibility(Trail,
                      graph_disconnected,
                      certificate(repairs_exhausted(Trail),
                                  graph_disconnected)).
