# Under the Hood: How NavLogic Actually Reasons

A deep-dive study guide — with real Prolog, not just metaphors.

---

## 0 · The one-breath pitch

The whole engine is three specialists passing notes:

```
natural language  →  [LLM]  →  structured goal
structured goal   →  [Python orchestrator]  →  candidates, routes, loops
everything else   →  [Prolog rulebook]  →  truth, tags, audits, relaxations
```

The LLM **translates** (messy text → logical form). Python **orchestrates** (runs the pipeline, handles the map math, bounds the loops). Prolog **reasons** (every "does this match?", "is A-a-kind-of-B?", "does this route break a rule?" question lives here).

The hard invariant is: **the LLM never decides anything important**. It converts words to logic at the front, and converts logic to words at the back. The middle is deterministic — and that's the whole thesis. If you let the neural layer reason past the front door, your answers stop being reproducible, inspectable, or defensible. So we don't.

Here's what that looks like in code.

---

## 1 · The query we'll follow the whole way

```
"I want to visit a temple, but I hate the heat."
```

Keep that sentence in your head. We're going to watch it mutate through seven stages.

---

## 2 · Stage 1 — LLM turns mush into a term

Gemini is called with a system prompt that teaches it an operator grammar: `and / or / not / any_tag / all_tag / none_tag`. It emits a **function call**, not prose. For our sentence, it produces something like:

```python
{
  "origin": "Asok",
  "goal": {
    "op": "and",
    "args": [
      {"op": "any_tag",  "tags": ["temple"]},
      {"op": "none_tag", "tags": ["weather_exposed"]}
    ]
  }
}
```

Python reads that dict and converts it into a Prolog term:

```prolog
and([ any_tag([temple]),
      none_tag([weather_exposed]) ])
```

That's it. That's the LLM's entire contribution on the input side. No routes, no rankings, no filtering. A clean logical form — the handoff point between neural and symbolic.

> 💡 **Why a term and not JSON?** Because Prolog is about to *recurse through this structure* using unification. A nested term is a first-class citizen of the language. JSON would just be a string we'd have to re-parse.

---

## 3 · Stage 2 — The ontology: `is_a/2` and synonyms

Before we can evaluate anything, the rulebook needs to know what words mean. Two mechanisms do the work.

### 3.1 Synonyms — map human noise onto canonical tags

```prolog
synonym(sweaty,   weather_exposed).
synonym(hot,      weather_exposed).
synonym(outdoors, weather_exposed).
synonym(shrine,   religious).
```

Simple lookup. If the user typed "sweaty," we want the engine to see `weather_exposed` — because that's the canonical tag on POIs. Synonyms are the phrasebook.

### 3.2 `bind_tag/2` — the gatekeeper with the cut

Every incoming tag goes through this:

```prolog
bind_tag(Tag, Bound) :- tag(Tag), !, Bound = Tag.            % known
bind_tag(Syn, Bound) :- synonym(Syn, Tag), !, Bound = Tag.   % alias
bind_tag(Tag, unknown(Tag)).                                 % fall-through
```

Three clauses, two cuts. Known tag → itself. Known synonym → its canonical form. Anything else → wrapped as `unknown(Tag)` so the system can surface it to the user ("I didn't recognise *aesthetic* — here are some tags I do know…") instead of silently dropping it.

> 🔥 **The cuts matter.** Without them, a known tag would *also* match the third clause on backtracking, producing `Tag ; unknown(Tag)` — ambiguous garbage downstream. The cut commits. This is one of those tiny details where Prolog's evaluation model buys you correctness for free, if you know what you're doing.

### 3.3 `is_a/2` — the recursive family tree

Here's where Prolog genuinely shines. We keep a small hand-authored hierarchy of direct subsumption edges (`subtag/2`), and derive the full tree from them recursively.

```prolog
subtag(buddhist_temple,  temple).
subtag(chinese_temple,   temple).
subtag(hindu_shrine,     shrine).
subtag(temple,           cultural).
subtag(shrine,           cultural).
subtag(cultural,         sightseeing).

is_a(X, X).                           % reflexive — everything is-a itself
is_a(X, Y) :- subtag(X, Y).           % direct edge
is_a(X, Z) :- subtag(X, Y), is_a(Y, Z).   % transitive closure
```

Three lines. That's the whole transitive closure of a taxonomy.

Ask Prolog `?- is_a(buddhist_temple, cultural).` and it walks:

```
buddhist_temple → temple → cultural   ✓
```

Ask `?- is_a(buddhist_temple, food).` and it exhausts every path, fails. Deterministic, inspectable, and — critically — **you didn't write a single `if` statement**. Compare that to the Python version you'd otherwise need: a dictionary of sets, a transitive-closure function, a cache, error handling for cycles… Prolog's unification + backtracking gives you all of that as an emergent property of three Horn clauses. That's the reason this layer is Prolog.

---

## 4 · Stage 3 — The goal evaluator: `satisfies/3`

Now the big one. The LLM emitted:

```prolog
and([ any_tag([temple]), none_tag([weather_exposed]) ])
```

How does Prolog evaluate "does POI X satisfy this arbitrarily nested logical form"? Not with an `if/elif/elif/elif` chain. With **pattern-matched recursion down the term**. Here's the simplified heart of it:

```prolog
% A POI satisfies a conjunction iff it satisfies every conjunct.
satisfies(POI, and(Conjuncts), _) :-
    forall(member(C, Conjuncts), satisfies(POI, C, _)).

% A POI satisfies a disjunction iff it satisfies at least one.
satisfies(POI, or(Disjuncts), _) :-
    member(C, Disjuncts),
    satisfies(POI, C, _).

% Negation as failure.
satisfies(POI, not(G), _) :-
    \+ satisfies(POI, G, _).

% Tag operators — these delegate to the ontology.
satisfies(POI, any_tag(Tags), _) :-
    member(Tag, Tags),
    poi_has_tag(POI, Tag).

satisfies(POI, all_tag(Tags), _) :-
    forall(member(Tag, Tags), poi_has_tag(POI, Tag)).

satisfies(POI, none_tag(Tags), _) :-
    forall(member(Tag, Tags), \+ poi_has_tag(POI, Tag)).
```

And — this is the clever bit — `poi_has_tag/2` goes through `is_a/2`:

```prolog
poi_has_tag(POI, QueryTag) :-
    tagged(POI, ActualTag),
    is_a(ActualTag, QueryTag).
```

So when we ask "does Wat Mangkon satisfy `any_tag([temple])`?":

1. `tagged(wat_mangkon, chinese_temple)` — yes, it's tagged `chinese_temple`.
2. `is_a(chinese_temple, temple)` — yes, via the taxonomy.
3. Therefore `poi_has_tag(wat_mangkon, temple)` holds.
4. Therefore `any_tag([temple])` is satisfied.

**Take a moment to appreciate this.** The user said "temple." Wat Mangkon is tagged `chinese_temple`. Nobody wrote a rule saying "a chinese_temple counts as a temple." The subsumption rule did it automatically. Add a new subtype — say, `jain_temple` — by writing one fact: `subtag(jain_temple, temple).` Everything upstream keeps working. **That's closed-world reasoning with open-world extensibility**, and it's very hard to replicate in an imperative codebase without a growing mess of helper classes.

### 4.1 Collecting the candidates

Python asks a single query:

```prolog
candidates(Goal, Cs) :-
    findall(POI,
            ( poi(POI, _, _),
              satisfies(POI, Goal, _) ),
            Cs).
```

`findall/3` is Prolog's "gather every solution." It runs `satisfies` against every `poi` fact and collects the ones that hold. For our query, the list comes back:

```
[wat_mangkon_kamalawat, erawan_shrine]
```

Wat Pho and Wat Arun — beautiful temples, both — are excluded because they're tagged `weather_exposed`, and our goal has a `none_tag([weather_exposed])` conjunct.

---

## 5 · Stage 4 — When the list is empty: `relax/4`

What if the user asked for something no POI satisfies? Something like:

```prolog
and([ any_tag([temple]),
      none_tag([weather_exposed]),
      any_tag([michelin_star]) ])
```

A Michelin-starred indoor temple? No such thing. A naive engine returns an empty list and the user gets a shrug.

The rulebook does better. It drops one conjunct at a time and retries. Schematically:

```prolog
relax(and(Conjuncts), Dropped, RelaxedGoal, Survivors) :-
    select(Dropped, Conjuncts, Remaining),     % pick one to drop
    RelaxedGoal = and(Remaining),
    candidates(RelaxedGoal, Survivors),
    Survivors \= [].                           % must produce results
```

`select/3` is the standard "remove one element from a list" predicate. Backtracking means it tries dropping *each* conjunct in turn. Combined with `Survivors \= []`, you get: **find the minimal single-conjunct drop that unblocks results.** If no single drop works, the orchestrator asks again with two drops, and so on.

The surfaced `relaxation_note` in the response then tells the user *what was dropped*: "I couldn't find a Michelin-starred indoor temple — dropped the Michelin requirement and found two indoor temples." The user isn't confused; they're told exactly what bent.

This is **constraint weakening** — a classical KRR move — and it falls out of three lines of Prolog. Try writing that in Python without accidentally reinventing backtracking. You'll be three hundred lines in before you realise you've written a worse Prolog.

---

## 6 · Stage 5 — Python draws the map

Prolog handed back two candidates. Now Python earns its keep. For each survivor, the orchestrator runs a shortest-path search over the station graph:

```python
for poi in candidates:
    station = poi_station(poi)
    path    = dijkstra(origin="Asok", target=station)
    steps   = build_route_steps(path)  # Prolog again, actually —
                                       # turns a bare station list into
                                       # ride(Line, Board, Alight, …) / transfer(…)
```

Dijkstra is numeric work. It's fast, it's well-understood, and Prolog has nothing to add here. **This is the division of labour that matters.** Prolog owns *rules*; Python owns *graphs*. They meet at the boundaries.

After this stage we have, for each candidate, a full step-by-step itinerary.

---

## 7 · Stage 6 — The audit loop: Prolog vetoes the map

Here is where most retrieval systems fall down. And here is where NavLogic's KRR story lives.

Consider: the user asked for indoor-only. Wat Mangkon *is* indoor. But the best **route** to Wat Mangkon might require transferring at Hua Lamphong via an open-air footbridge that bakes you for four minutes in the April sun. The destination passed the tag filter. The route didn't.

So Python sends the computed route back to Prolog for auditing:

```prolog
% A route is audited by checking every transfer against the goal.
audit_route(Goal, Route, Violation) :-
    member(transfer(From, To), Route),
    transfer_property(From, To, weather_exposed),
    Goal = and(Conjuncts),
    member(none_tag(Tags), Conjuncts),
    member(weather_exposed, Tags),
    Violation = transfer_violates(weather_exposed, From, To).

audit_route(_, _, clean).   % fall-through — no violation found
```

Read that top clause out loud: *"There exists a transfer in the route whose walkway is weather-exposed, and the user's goal explicitly forbade `weather_exposed` — therefore emit a violation."*

Now Python's side of the loop:

```python
blacklist = set()

for attempt in range(MAX_REPLAN):
    poi = pick_best_candidate(candidates, blacklist)
    if poi is None:
        return failure("all candidates rejected")

    route      = dijkstra(origin, poi_station(poi))
    violation  = prolog.audit_route(goal, route)

    if violation == "clean":
        return success(poi, route)
    else:
        blacklist.add(poi)
        audit_trail.append((poi, violation))
```

Candidate gets vetoed → blacklist it → try the next one → bounded by `MAX_REPLAN` so we never loop forever. **This is the audit loop.** It's Prolog actively supervising numeric search, not passively filtering its inputs. The rulebook doesn't just say *"here are the acceptable destinations"* — it says *"you found a route to one, but that route breaks the same rule you filtered on, so throw it out."*

In our walkthrough, Erawan Shrine gets rejected because its best transfer crosses an exposed walkway. Wat Mangkon survives the audit (entirely underground via MRT Blue), and it becomes the answer.

---

## 8 · Stage 7 — LLM narrates the structured result

Python hands the final structure back to Gemini:

```python
{
  "origin": "Asok",
  "poi": "Wat Mangkon Kamalawat",
  "total_time": 22,
  "steps": [...],
  "audit_trail": [
    { "rejected": "Erawan Shrine",
      "reason": "transfer_violates(weather_exposed, Ratchadamri, …)" }
  ],
  "relaxation_note": []
}
```

And Gemini writes prose. *"Try Wat Mangkon — it's reachable entirely via the air-conditioned MRT Blue line, about 22 minutes. I skipped Erawan Shrine because the best transfer there crosses an open walkway."*

Every phrase in that paragraph is grounded in a term the rulebook produced. The LLM didn't invent the rejection — it narrated it. If you disagree with the answer, you can walk backward through the structured result and find the exact predicate that made the decision. **Try doing that with a pure-LLM system.** You can't; there's nothing to point at.

---

## 9 · Why this is Prolog and not Python

Every one of these mechanisms — subsumption, goal evaluation, relaxation, audit — has the same shape:

> "Recurse through a structured term. At each node, unify with a pattern. On failure, backtrack. Collect all solutions."

That's not an algorithm. That's *the Prolog evaluation model*. When your problem's structure matches the language's execution model, you write three lines and the engine does the work. When you try to write it in Python, you end up reinventing unification, backtracking, and pattern matching — badly, without the decades of compiler work SWI-Prolog has behind it.

The cliché is that Prolog is "declarative." The real answer is sharper: **Prolog is the right abstraction for problems where the rules have more structure than the data**. Tag hierarchies, logical goals, constraint cascades, audit checks — the rules are rich; the data (stations, POIs, tags) is flat. That's Prolog's home court.

Python handles the parts where the data is rich and the rules are simple: shortest path, graph pruning, iteration caps, network I/O. Each language at what it's best at. That's the whole design principle.

---

## 10 · The full pipeline, one more time — now with teeth

```
 "I want a temple but I hate the heat."
         │
         ▼
 [LLM] ── translate_to_query ──▶  and([ any_tag([temple]),
                                        none_tag([weather_exposed]) ])
         │
         ▼
 [Python] ── prolog.candidates(Goal) ──▶  [wat_mangkon, erawan_shrine]
                                          (empty? → relax/4 drops a conjunct)
         │
         ▼
 [Python] ── dijkstra to each candidate ──▶ routes with ride/transfer steps
         │
         ▼
 [Python + Prolog] ── audit_route(Goal, Route, Violation)
                      │
                      ├── clean?    →  accept
                      └── violation? → blacklist POI, replan (≤ MAX_REPLAN)
         │
         ▼
 [LLM] ── format_result ──▶  "Head to Wat Mangkon — all underground via MRT…"
```

Seven stages. Two LLM calls at the bookends. Everything in the middle is symbolic, deterministic, and inspectable.

---

## 11 · TL;DR (the part you paste into your notes)

- **LLM's job:** text → structured goal, then structured result → text. It is a *translator at the boundaries*. It is never allowed to reason in the middle.
- **Prolog's job:** own the rulebook. `is_a/2` (recursive subsumption), `synonym/2` (aliasing), `satisfies/3` (pattern-matched goal evaluation), `candidates/2` (`findall` gather), `relax/4` (minimal-drop weakening), `audit_route/3` (post-hoc veto).
- **Python's job:** orchestrate. Pass the goal to Prolog, run Dijkstra on the survivors, feed routes back to Prolog for audit, handle the blacklist-and-retry loop, bound the iterations, assemble the response.
- **Why Prolog scales:** because subsumption, goal evaluation, relaxation, and audit are all *"recurse through a term, unify, backtrack, collect"* — which is literally what the Prolog engine does for free. You write the rules; the engine does the reasoning.
- **Why the audit loop matters:** it proves the symbolic layer is actively supervising the numeric layer. The rulebook doesn't just filter inputs — it *vetoes outputs* and forces a replan. That's what makes this KRR, not RAG.

Go write a `subtag/2` fact. Go stare at three lines of `is_a/2`. Everything in NavLogic — every route recommendation, every rejection, every relaxation — is built on top of primitives that small.

That's the whole trick. 🔧
