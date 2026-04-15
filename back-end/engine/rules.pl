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
  3. Logical-form reasoning        — satisfies/2, candidates/2,
                                     preference_score/3, relax/3,
                                     audit_route/3, unknown_tags/2

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

/* poi_has_tag/2 — tag membership respecting subsumption.
   A POI tagged `temple` matches a query for `religious_site` because
   subtag(temple, religious_site) is in the ontology.
*/
poi_has_tag(Poi, Tag) :-
    tagged(Poi, Tags),
    member(T, Tags),
    is_a(T, Tag).

/* satisfies/2 — recursive evaluator for goal terms.

   Goal grammar (mirrors the JSON the LLM emits, serialized to
   Prolog terms by Python):

     and(Gs)         conjunction
     or(Gs)          disjunction
     not(G)          negation
     any_tag(Ts)     POI has at least one of Ts
     all_tag(Ts)     POI has every tag in Ts
     none_tag(Ts)    POI has none of Ts (HARD constraint)
     prefer_tag(Ts)  soft preference (always satisfies; scored later)
     route_to(_)     handled by orchestrator, not by candidate filter

   Tags pass through bind_tag/2 (defined in ontology.pl) so synonyms
   and unknown vocabulary are handled uniformly.
*/

satisfies(_,   any_tag([])) :- fail.
satisfies(Poi, any_tag([T | _Ts])) :-
    bind_tag(T, B),
    \+ B = unknown(_),
    poi_has_tag(Poi, B),
    !.
satisfies(Poi, any_tag([_ | Ts])) :-
    satisfies(Poi, any_tag(Ts)).

satisfies(_,   all_tag([])).
satisfies(Poi, all_tag(Ts)) :-
    forall(member(T, Ts),
           ( bind_tag(T, B),
             \+ B = unknown(_),
             poi_has_tag(Poi, B) )).

satisfies(_,   none_tag([])).
satisfies(Poi, none_tag(Ts)) :-
    forall(member(T, Ts),
           ( bind_tag(T, B),
             ( B = unknown(_)
             -> true
             ;  \+ poi_has_tag(Poi, B) ) )).

satisfies(Poi, and(Gs)) :-
    forall(member(G, Gs), satisfies(Poi, G)).

satisfies(Poi, or(Gs)) :-
    member(G, Gs),
    satisfies(Poi, G).

satisfies(Poi, not(G)) :-
    \+ satisfies(Poi, G).

satisfies(_, prefer_tag(_)).   /* preferences never block; scored separately */
satisfies(_, route_to(_)).     /* orchestrator handles routing intent */

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

preference_score(Poi, Goal, Score) :-
    findall(1,
            ( sub_goal(Goal, prefer_tag(Ts)),
              member(T, Ts),
              bind_tag(T, B),
              \+ B = unknown(_),
              poi_has_tag(Poi, B) ),
            Hits),
    length(Hits, Score).

/* ------------------------------------------------------------------
   candidates/2 — the headline query.

   Returns Name-Station-Score for every POI satisfying Goal, with
   its preference score. Empty result triggers relax/3 in the
   orchestrator.
------------------------------------------------------------------ */

candidates(Goal, Cands) :-
    findall(Name-Station-Score,
            ( poi(Id, Name, Station),
              satisfies(Id, Goal),
              preference_score(Id, Goal, Score) ),
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

relax(and(Gs), [Drop], Survivors) :-
    select(Drop, Gs, Rest),
    candidates(and(Rest), Survivors),
    Survivors \= [].

relax(and(Gs), [D1, D2], Survivors) :-
    select(D1, Gs, R1),
    select(D2, R1, R2),
    candidates(and(R2), Survivors),
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
