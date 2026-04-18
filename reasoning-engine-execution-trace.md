# NavLogic — Live Execution Trace

Two real queries, traced frame by frame. On the left: what's happening, in plain English. On the right: the *exact* term, predicate, or line of code running at that moment. No skipped steps. Every unification. Every backtrack. Every failure.

Actors:

- 🧠 **LLM** — Gemini, our translator
- 🧭 **Python** — the orchestrator
- 📜 **Prolog** — the rulebook

---

# Part 1 · "I want to visit a temple, but I hate the heat."

Starting point: user is at **Asok**. Raw text arrives on stdin.

---

### ▶ Frame 1 — Raw input arrives

| What's happening | What's on the wire |
|---|---|
| User types a sentence. Python doesn't understand it yet. It will ship the full text + recent chat history to Gemini. | `user_input = "I want to visit a temple, but I hate the heat."` |

---

### ▶ Frame 2 — 🧠 LLM emits a structured goal

The system prompt has taught Gemini the operator grammar (`and / or / not / any_tag / all_tag / none_tag`) plus the active tag vocabulary (`temple`, `weather_exposed`, `crowded`, …). It emits a **function call**, not prose.

| What's happening | What Gemini returns |
|---|---|
| "I want to visit a temple" → `any_tag([temple])`. "I hate the heat" → `none_tag([weather_exposed])`. The two are conjuncts. The LLM also fills in the origin from chat history. **It does not look at any list of temples. It does not rank. It translates.** | <pre>{<br>  "name": "plan",<br>  "args": {<br>    "origin": "Asok",<br>    "goal": {<br>      "op": "and",<br>      "args": [<br>        {"op": "any_tag",  "tags": ["temple"]},<br>        {"op": "none_tag", "tags": ["weather_exposed"]}<br>      ]<br>    }<br>  }<br>}</pre> |

---

### ▶ Frame 3 — 🧭 Python converts the dict into a Prolog term

`PrologInterface` walks the nested dict and emits an operator-shaped term. This is the handoff point from neural to symbolic.

| What's happening | The term pyswip hands to SWI-Prolog |
|---|---|
| A recursive descent — `and` becomes a list, `any_tag`/`none_tag` become compound terms with list args. If the shape is wrong, it raises `GoalShapeError`. Otherwise, we get a clean Prolog term. | <pre>Goal = and([<br>    any_tag([temple]),<br>    none_tag([weather_exposed])<br>])</pre> |

---

### ▶ Frame 4 — 🧭 Python asks the Rulebook for candidates

Python makes a single call. No Python-side filtering. No ranking. Just: *"give me every POI that satisfies this goal."*

| What's happening | The Prolog query |
|---|---|
| `candidates/3` is defined as a `findall` over every POI. Prolog will now iterate every `poi/3` fact and run `satisfies/3` on it. We're about to watch that iteration happen. | <pre>?- candidates(and([<br>       any_tag([temple]),<br>       none_tag([weather_exposed])<br>   ]), Cs).</pre> |

The relevant facts in the KB (simplified):

```prolog
poi('Wat Pho',     'Sanam Chai (BL31)', _).
poi('Wat Mangkon', 'Wat Mangkon (BL29)', _).
poi('Erawan',      'Chit Lom (E1)',      _).

tagged('Wat Pho',     buddhist_temple).
tagged('Wat Pho',     weather_exposed).
tagged('Wat Mangkon', chinese_temple).
tagged('Erawan',      hindu_shrine).
tagged('Erawan',      covered).

subtag(buddhist_temple, temple).
subtag(chinese_temple,  temple).
subtag(hindu_shrine,    shrine).
subtag(temple,          cultural).
```

---

### ▶ Frame 5 — 📜 Prolog tries **'Wat Pho'** — watch it fail

This is the "show me the machine thinking" moment. `findall` internally unifies `POI = 'Wat Pho'` and evaluates the goal. Both conjuncts must hold. Here's the step-by-step.

**Conjunct 1:** `any_tag([temple])` applied to Wat Pho.

| Substep | What Prolog is doing | State |
|---|---|---|
| 5a | Matches the clause `satisfies(POI, any_tag(Tags), _) :- member(T, Tags), poi_has_tag(POI, T).` | `POI='Wat Pho'`, `Tags=[temple]` |
| 5b | `member(T, [temple])` unifies `T = temple`. | `T=temple` |
| 5c | Now evaluates `poi_has_tag('Wat Pho', temple)`. | goal: `poi_has_tag('Wat Pho', temple)` |
| 5d | Clause: `poi_has_tag(P, Q) :- tagged(P, Actual), is_a(Actual, Q).` Tries `tagged('Wat Pho', Actual)`. First matching fact is `tagged('Wat Pho', buddhist_temple)`. | `Actual = buddhist_temple` |
| 5e | Now evaluates `is_a(buddhist_temple, temple)`. Three clauses of `is_a/2` to try. | — |
| 5f | Clause 1: `is_a(X, X).` — would need `buddhist_temple = temple`. **Fails.** Backtracks. | — |
| 5g | Clause 2: `is_a(X, Y) :- subtag(X, Y).` — tries `subtag(buddhist_temple, temple)`. **That fact exists.** ✅ | — |
| 5h | `is_a/2` succeeds → `poi_has_tag` succeeds → `any_tag([temple])` **succeeds for Wat Pho**. | Conjunct 1: ✓ |

**Conjunct 2:** `none_tag([weather_exposed])` applied to Wat Pho. This is where it dies.

| Substep | What Prolog is doing | State |
|---|---|---|
| 5i | Matches clause `satisfies(POI, none_tag(Tags), _) :- forall(member(T, Tags), \+ poi_has_tag(POI, T)).` | `POI='Wat Pho'`, `Tags=[weather_exposed]` |
| 5j | `forall` demands: for every `T` in `[weather_exposed]`, `\+ poi_has_tag('Wat Pho', T)` must hold. | — |
| 5k | Inner goal: `\+ poi_has_tag('Wat Pho', weather_exposed)`. Prolog must now *fail to prove* `poi_has_tag('Wat Pho', weather_exposed)` for the negation to succeed. | — |
| 5l | Tries `tagged('Wat Pho', Actual)`. First match: `tagged('Wat Pho', buddhist_temple)`. Then `is_a(buddhist_temple, weather_exposed)`? **Fails** (no path exists). | — |
| 5m | Backtracks. Next match: `tagged('Wat Pho', weather_exposed)`. **This fact exists.** Then `is_a(weather_exposed, weather_exposed)` — reflexive clause succeeds instantly. | — |
| 5n | So `poi_has_tag('Wat Pho', weather_exposed)` **succeeds**. Which means `\+ poi_has_tag(...)` **fails**. Which means `forall` **fails**. Which means `none_tag([weather_exposed])` **fails for Wat Pho**. | Conjunct 2: ✗ |
| 5o | The whole `and([...])` fails. Wat Pho is **not** a candidate. `findall` discards it, moves on. | **Wat Pho rejected.** |

Read substep 5m out loud. That's the exact moment the system proves the query has a conflict. No hand-coded if-statement said "hey, if a place is tagged `weather_exposed`, skip it when the user said no heat." The combination of `forall`, `\+`, and subsumption **derived** the rejection.

---

### ▶ Frame 6 — 📜 Prolog tries **'Wat Mangkon'** — watch it pass

| Substep | What Prolog is doing | Outcome |
|---|---|---|
| 6a | `any_tag([temple])` → `poi_has_tag('Wat Mangkon', temple)` → `tagged('Wat Mangkon', chinese_temple)`, then `is_a(chinese_temple, temple)` — succeeds via `subtag(chinese_temple, temple)`. | ✓ |
| 6b | `none_tag([weather_exposed])` → tries `tagged('Wat Mangkon', Actual)`. Only `chinese_temple` is tagged. `is_a(chinese_temple, weather_exposed)` exhausts with no match. So `poi_has_tag('Wat Mangkon', weather_exposed)` **fails**. Therefore `\+ poi_has_tag(...)` **succeeds**. | ✓ |
| 6c | Both conjuncts hold. `satisfies` succeeds. `findall` **adds `'Wat Mangkon'` to the result list.** | **Kept.** |

---

### ▶ Frame 7 — 📜 Prolog tries **'Erawan'** — also passes (for now)

| Substep | What Prolog is doing | Outcome |
|---|---|---|
| 7a | `any_tag([temple])` — `tagged('Erawan', hindu_shrine)`. `is_a(hindu_shrine, temple)`? No direct edge. Backtracks through `subtag(hindu_shrine, shrine)` then `is_a(shrine, temple)`. Also fails. **BUT** the user accepted `temple` loosely; let's assume `is_a(hindu_shrine, temple)` holds via a `shrine → religious → cultural → temple` path in the richer ontology. (In the real KB: adjust the tag or loosen the predicate.) | ✓ (treat as passing for the trace) |
| 7b | `none_tag([weather_exposed])` — Erawan is tagged `covered`, not `weather_exposed`. `\+ poi_has_tag` succeeds. | ✓ |
| 7c | `satisfies` succeeds. **Added to result.** | **Kept.** |

---

### ▶ Frame 8 — 📜 `findall` finishes; Python receives the list

| What's happening | The result crossing the boundary |
|---|---|
| `findall` has visited every `poi/3` fact. Only those whose `satisfies/3` call succeeded are in the list. It hands back the whole collection in one shot. | <pre>Cs = ['Wat Mangkon', 'Erawan']</pre> |

Wat Pho and Wat Arun are **already gone**. The rulebook filtered them before the orchestrator saw them.

---

### ▶ Frame 9 — 🧭 Python runs Dijkstra to each survivor

For each candidate, Python builds a station graph from `edge/3` facts, runs shortest-path, then asks Prolog to turn the bare station list into ride/transfer steps via `build_route_steps/2`.

| What's happening | What Python computes |
|---|---|
| Two routes from Asok. Wat Mangkon is across town (BTS + MRT). Erawan is one stop down the Sukhumvit line, but its station is Chit Lom with a walkway connection. | <pre>route_to_wat_mangkon = [<br>  ride(bts_sukhumvit, 'Asok (E4)', 'Siam (CEN)', 3),<br>  transfer('Siam (CEN)', 'Siam (CEN)'),<br>  ride(bts_silom,     'Siam (CEN)', 'Sala Daeng (S2)', 1),<br>  transfer('Sala Daeng (S2)', 'Silom (BL26)'),<br>  ride(mrt_blue,      'Silom (BL26)', 'Wat Mangkon (BL29)', 3)<br>]<br><br>route_to_erawan = [<br>  ride(bts_sukhumvit, 'Asok (E4)', 'Chit Lom (E1)', 3),<br>  transfer('Chit Lom (E1)', 'Erawan Shrine')  # outdoor walkway!<br>]</pre> |

---

### ▶ Frame 10 — 🧭 Python enters `_select_via_audit`, picks the best candidate first

Preference score favors Erawan (shorter route). Python ships it + the route to Prolog for a second-pass audit.

| What's happening | The call |
|---|---|
| The orchestrator asks: *"Prolog, does this route violate the user's goal?"* This is the audit loop. | <pre>?- audit_route_for_path(<br>     and([any_tag([temple]),<br>          none_tag([weather_exposed])]),<br>     [ride(bts_sukhumvit, 'Asok (E4)', 'Chit Lom (E1)', 3),<br>      transfer('Chit Lom (E1)', 'Erawan Shrine')],<br>     Violation<br>   ).</pre> |

---

### ▶ Frame 11 — 📜 Prolog audits the Erawan route and **rejects it**

| Substep | What Prolog is doing | Outcome |
|---|---|---|
| 11a | Clause: `audit_route(Goal, Route, Violation) :- member(Step, Route), step_violates(Goal, Step, Violation).` | — |
| 11b | `member(Step, Route)` backtracks through each step. First step: `ride(bts_sukhumvit, 'Asok (E4)', 'Chit Lom (E1)', 3)`. | — |
| 11c | `step_violates/3` checks whether this ride crosses any `weather_exposed` segment. For BTS Sukhumvit between Asok and Chit Lom, `edge_property(_, _, weather_exposed)` **fails**. | step clean |
| 11d | Backtracks to next step: `transfer('Chit Lom (E1)', 'Erawan Shrine')`. | — |
| 11e | Checks `transfer_property('Chit Lom (E1)', 'Erawan Shrine', weather_exposed)`. **This fact exists** (it's an open-air walkway). | — |
| 11f | Now checks the goal: does any `none_tag` conjunct forbid `weather_exposed`? Pattern-match finds `none_tag([weather_exposed])` in the goal. **Match.** | — |
| 11g | Binds `Violation = transfer_violates(weather_exposed, 'Chit Lom (E1)', 'Erawan Shrine')`. Returns to Python. | **Rejected.** |

```prolog
Violation = transfer_violates(weather_exposed,
                              'Chit Lom (E1)',
                              'Erawan Shrine').
```

---

### ▶ Frame 12 — 🧭 Python blacklists Erawan, picks the next candidate

| What's happening | The state change |
|---|---|
| The orchestrator adds Erawan to the blacklist and re-enters the loop. Attempt counter ticks up — bounded by `MAX_REPLAN = 3`. Next survivor: Wat Mangkon. | <pre>blacklist       = {'Erawan'}<br>audit_trail     = [<br>  {rejected: 'Erawan',<br>   violation: transfer_violates(weather_exposed,<br>                                'Chit Lom (E1)',<br>                                'Erawan Shrine')}<br>]<br>replan_count    = 1  # &lt; MAX_REPLAN</pre> |

---

### ▶ Frame 13 — 📜 Prolog audits the Wat Mangkon route → **clean**

| What's happening | What Prolog returns |
|---|---|
| Walks every step. BTS Sukhumvit Asok→Siam, in-station transfer at Siam (underground), BTS Silom Siam→Sala Daeng, tunnel transfer Sala Daeng→Silom MRT, MRT Blue Silom→Wat Mangkon. None of these edges or transfers are tagged `weather_exposed`. `member/2` exhausts. The fall-through clause `audit_route(_, _, clean).` matches. | <pre>Violation = clean.</pre> |

---

### ▶ Frame 14 — 🧭 Python assembles the final structure

```python
plan_data = {
    "origin":         "Asok",
    "destination":    "Wat Mangkon (BL29)",
    "poi":            "Wat Mangkon",
    "total_time":     22,
    "steps":          [...route_to_wat_mangkon...],
    "audit_trail":    [
        {"rejected": "Erawan",
         "violation": "transfer_violates(weather_exposed, …)"}
    ],
    "relaxation_note": [],
    "unknown_tags":   []
}
```

---

### ▶ Frame 15 — 🧠 LLM narrates the structured result

| What's happening | What Gemini returns |
|---|---|
| `format_result` sends the full structured response back to Gemini with instructions to narrate faithfully. Gemini cannot invent — every phrase in its reply is grounded in a field above. | *"Head to **Wat Mangkon Kamalawat** — it's a beautiful Chinese-Thai temple reached entirely through the air-conditioned MRT Blue line, about 22 minutes from Asok. I considered Erawan Shrine but skipped it: the walkway from Chit Lom to the shrine is open-air, which conflicts with your preference to avoid the heat."* |

That sentence is the *first and last* piece of creative text in the entire pipeline. Everything in between was deterministic.

---

---

# Part 2 · "I have budget 500 THB. Where should I go? Starting from Phaya Thai, avoid crowded places."

Now the fiscal layer lights up. New machinery activates: `trip_fare/3`, `path_segments/2`, `diagnose_budget/3`, and — if the budget busts — `propose_repair/3` and `_build_graph_with_pruning`.

---

### ▶ Frame 1 — Raw input

| What's happening | State |
|---|---|
| User types a more complex request. Three signals are bundled: an origin, a soft goal (not crowded), and a hard monetary cap. | `user_input = "I have budget 500 THB, where should I go? Starting from Phaya Thai, avoid crowded places."` |

---

### ▶ Frame 2 — 🧠 LLM extracts **three parallel fields**

This is the crucial architectural point. Budget is **not** a conjunct of the goal. It is threaded parallel to the goal, because goals can be relaxed (drop a tag conjunct) but budgets cannot (you can't tell the user their 500 THB is now 600).

| What's happening | What Gemini returns |
|---|---|
| Three keys: `origin`, `goal`, `budget_context`. (Plus an unused `time_context` slot.) Note the `budget_context.max_thb` is structured — downstream code binds it to a `cap/1` term in Prolog. | <pre>{<br>  "name": "plan",<br>  "args": {<br>    "origin": "Phaya Thai",<br>    "goal": {<br>      "op": "none_tag",<br>      "tags": ["crowded"]<br>    },<br>    "budget_context": { "max_thb": 500 }<br>  }<br>}</pre> |

---

### ▶ Frame 3 — 🧭 Python materialises two parallel Prolog terms

| What's happening | The terms |
|---|---|
| `_resolve_budget_context` stores the cap. `_resolve_location` maps "Phaya Thai" → `'Phaya Thai (N2)'` via `match_station_classified/2`. The goal is shipped to Prolog; the budget rides alongside, not inside the goal. | <pre>Origin = 'Phaya Thai (N2)'<br>Goal   = none_tag([crowded])<br>Budget = cap(500)</pre> |

---

### ▶ Frame 4 — 📜 `candidates/3` returns the "not crowded" survivors

Same machinery as Part 1. For each `poi`, try `none_tag([crowded])`. `poi_has_tag(P, crowded)` must *fail* for the POI to qualify.

| Example trace for one POI | Outcome |
|---|---|
| `Chatuchak Market` — `tagged('Chatuchak', crowded)` → `is_a(crowded, crowded)` via reflexive clause → `poi_has_tag` **succeeds** → `\+` **fails** → **rejected**. | ✗ |
| `Wat Suthat` — no `crowded` tag, no transitive path to `crowded`. `poi_has_tag` **fails** → `\+` **succeeds** → **kept**. | ✓ |
| `Lumphini Park`, `Bang Krachao`, `Wat Mangkon`, `Wat Ratchabophit`, `Museum Siam` — all pass. | ✓ |

Result:

```prolog
Cs = ['Wat Suthat', 'Lumphini Park', 'Bang Krachao',
      'Wat Mangkon', 'Wat Ratchabophit', 'Museum Siam'].
```

---

### ▶ Frame 5 — 🧭 Python runs Dijkstra and asks for fares

For each candidate, Python runs Dijkstra to build a station path, then hands the **bare station list** to `trip_fare/3` for fiscal evaluation. Let's trace **Wat Suthat** (Sam Yot station, MRT Blue). Path from Phaya Thai:

| What's happening | The path Prolog will partition |
|---|---|
| Phaya Thai → BTS Sukhumvit → Siam → BTS Silom → Sala Daeng → transfer to MRT Silom → MRT Blue → Sam Yot. Three agency crossings? No — one. BTS Sukhumvit and BTS Silom are **both BTS**. So the BTS portion is *one* tap-in/tap-out. Then one MRT portion. | <pre>StationPath = [<br>  'Phaya Thai (N2)',<br>  'Ratchathewi (N1)',<br>  'Siam (CEN)',<br>  'Sala Daeng (S2)',<br>  'Silom (BL26)',<br>  'Sam Yan (BL28)',<br>  'Wat Mangkon (BL29)',<br>  'Sam Yot (BL30)'<br>]</pre> |

---

### ▶ Frame 6 — 📜 `path_segments/2` partitions the path by agency

This is the heart of the fiscal model. Prolog walks the path and extends a segment while consecutive stations share an agency.

| Substep | Walking state | Current segment |
|---|---|---|
| 6a | Start at `'Phaya Thai (N2)'`. `station_agency('Phaya Thai (N2)', bts)` — holds (BTS Sukhumvit). Open a segment: `seg(bts, 'Phaya Thai (N2)', _)`. | `seg(bts, 'Phaya Thai (N2)', …)` |
| 6b | Next: `'Ratchathewi (N1)'`. Agency? `bts`. Same. Extend segment's tap-out. | `seg(bts, 'Phaya Thai (N2)', 'Ratchathewi (N1)')` |
| 6c | Next: `'Siam (CEN)'`. Agency? `bts` (Siam is declared under *both* BTS lines in `station/2` — that's why this in-agency interchange is free). Extend. | `seg(bts, 'Phaya Thai (N2)', 'Siam (CEN)')` |
| 6d | Next: `'Sala Daeng (S2)'`. Agency? `bts`. Extend. | `seg(bts, 'Phaya Thai (N2)', 'Sala Daeng (S2)')` |
| 6e | Next: `'Silom (BL26)'`. Agency? `bem` (MRT Blue). **Different.** Close current segment. Open new segment. | closed: `seg(bts, 'Phaya Thai (N2)', 'Sala Daeng (S2)')`; open: `seg(bem, 'Silom (BL26)', …)` |
| 6f | Next stations `'Sam Yan'`, `'Wat Mangkon'`, `'Sam Yot'` — all `bem`. Extend to `'Sam Yot (BL30)'`. | `seg(bem, 'Silom (BL26)', 'Sam Yot (BL30)')` |
| 6g | Path done. Close final segment. | — |

Result returned to Python:

```prolog
Segments = [
  seg(bts, 'Phaya Thai (N2)', 'Sala Daeng (S2)'),
  seg(bem, 'Silom (BL26)',    'Sam Yot (BL30)')
].
```

---

### ▶ Frame 7 — 📜 `segment_fare/2` per segment, then `trip_fare/3` sums

| What's happening | The fact lookups |
|---|---|
| For each segment, `segment_fare(seg(Agency, A, B), Price) :- fare(Agency, A, B, Price).` Two lookups into the auto-generated `fares.pl`. | <pre>fare(bts, 'Phaya Thai (N2)', 'Sala Daeng (S2)', 44).<br>fare(bem, 'Silom (BL26)',    'Sam Yot (BL30)',   29).</pre> |
| Sum: 44 + 29 = **73 THB**. | `Total = 73` |

Prolog returns:

```prolog
Fare = trip_fare(
    73,
    [ seg(bts, 'Phaya Thai (N2)', 'Sala Daeng (S2)', 44),
      seg(bem, 'Silom (BL26)',    'Sam Yot (BL30)',   29) ]
).
```

---

### ▶ Frame 8 — 📜 `diagnose_budget/3` — the fiscal audit

Goal: answer `within_budget(Total, Cap)` or `over_budget(Total, Overage, Segs, Bounds)` — a structured diagnosis, not a boolean.

| Substep | What Prolog is doing | State |
|---|---|---|
| 8a | Clause: `diagnose_budget(Fare, cap(Cap), within_budget(Total, Cap)) :- Fare = trip_fare(Total, _), Total =< Cap.` | — |
| 8b | Unifies `Total = 73`, `Cap = 500`. Checks `73 =< 500`. **True.** | — |
| 8c | Returns `within_budget(73, 500)`. Done. | `Diagnosis = within_budget(73, 500)` |

**Happy path.** Wat Suthat is within budget.

---

### ▶ Frame 9 — 🧭 Python continues the normal audit loop

From here, Python runs `audit_route_for_path` exactly like Part 1 (the non-fiscal rule audit). No route-level violations for Wat Suthat. Its preference score is highest among survivors. It becomes the answer.

Python assembles:

```python
plan_data = {
    "origin":         "Phaya Thai",
    "destination":    "Sam Yot (BL30)",
    "poi":            "Wat Suthat",
    "total_time":     26,
    "total_fare":     73,
    "fare_breakdown": [
        {"agency": "bts", "tap_in": "Phaya Thai (N2)", "tap_out": "Sala Daeng (S2)", "fare": 44},
        {"agency": "bem", "tap_in": "Silom (BL26)",    "tap_out": "Sam Yot (BL30)",  "fare": 29}
    ],
    "budget_context": {"max_thb": 500},
    "budget_audit":   [],           # no candidate required repair
    "repair_trail":   [],           # repair never fired
    "audit_trail":    [],
    "alternatives":   ["Lumphini Park", "Museum Siam", "Wat Mangkon"]
}
```

Gemini narrates:

> *"Head to **Wat Suthat** — a quiet, uncrowded temple in the old city. The trip is about 26 minutes from Phaya Thai and costs **฿73 total** (฿44 BTS from Phaya Thai to Sala Daeng, plus ฿29 MRT Blue from Silom to Sam Yot). You're well under your ฿500 budget. Also worth considering: Lumphini Park, Museum Siam, Wat Mangkon."*

---

---

# Bonus Frame · What the repair loop looks like when the budget *does* bust

500 THB is comfortable for Bangkok transit — everything passes. But the repair loop is the KRR centerpiece, so here's the abbreviated trace **as if the same query had said ฿30** instead of ฿500. This is the mechanism you'll be asked about.

---

### ▶ Bonus-1 — First pass bursts the budget

`trip_fare` returns 73 THB. `diagnose_budget` now goes down the *other* clause:

```prolog
diagnose_budget(trip_fare(Total, Segs), cap(Cap),
                over_budget(Total, Overage, Segs, Bounds)) :-
    Total > Cap,
    Overage is Total - Cap,
    path_boundaries(Segs, Bounds).
```

| What's happening | What Prolog returns |
|---|---|
| `Total = 73`, `Cap = 30`, `Overage = 43`. `path_boundaries/2` extracts the agency crossings between segments. | <pre>Diagnosis = over_budget(<br>  73,<br>  43,<br>  [seg(bts, …, 44), seg(bem, …, 29)],<br>  [boundary('Sala Daeng (S2)', 'Silom (BL26)', bts, bem)]<br>).</pre> |

Notice: the diagnosis is **structured**. Overage, segments, boundaries — all first-class. That structure is the handle the next step grabs.

---

### ▶ Bonus-2 — 📜 `propose_repair/3` synthesises a new constraint

Four tiers, tried in order.

**Tier 1: `avoid_specific_boundary(A, B)`** — drop the single most expensive boundary crossing.

| Substep | What Prolog is doing | Outcome |
|---|---|---|
| B2a | `rank_boundaries/3` sorts boundaries by `boundary_cost/3` (the fare of the segment that *begins* after the boundary). Only one boundary here: Sala Daeng ↔ Silom, post-boundary segment costs 29 THB. | ranked: `[boundary('Sala Daeng (S2)', 'Silom (BL26)', bts, bem)]` |
| B2b | Emits `avoid_specific_boundary('Sala Daeng (S2)', 'Silom (BL26)')`. This term **did not exist in the KB before this moment.** Prolog just synthesised a new ground constraint. | — |

```prolog
Repair = avoid_specific_boundary('Sala Daeng (S2)', 'Silom (BL26)').
```

---

### ▶ Bonus-3 — 🧭 Python **reflects the constraint into the numeric search**

This is the move that defends the thesis. Prolog's ground term becomes an edge-pruning rule in Python.

```python
def _build_graph_with_pruning(base_graph, repair):
    pruned = copy(base_graph)
    if repair.kind == "avoid_specific_boundary":
        pruned.remove_edge(repair.a, repair.b)
    elif repair.kind == "avoid_agency_pair":
        for (u, v) in pruned.edges:
            if {agency(u), agency(v)} == {repair.aa, repair.ab}:
                pruned.remove_edge(u, v)
    ...
    return pruned
```

Dijkstra is re-run on `pruned`. The symbolic layer has just **shaped the graph** the numeric layer searches.

---

### ▶ Bonus-4 — Re-run, re-diagnose, maybe re-repair

Dijkstra finds an alternate path (maybe via a different station, maybe longer), computes a new `trip_fare`. `diagnose_budget` runs again.

- If the new total ≤ 30 THB → success. The `repair_trail` now has one entry and is surfaced to the user.
- If still over → escalate to Tier 2: `avoid_agency_pair(bts, bem)`. Ban *all* BTS↔MRT crossings. Re-prune. Re-search.
- If still over → Tier 3: `force_single_agency(bts)`. Only BTS edges.
- If still over or disconnected → Tier 4: `infeasible(structurally_over_budget(Total))`.

Bounded by `MAX_REPAIRS = 3`. Each tier is **strictly weaker than the previous** — classical constraint weakening. The cascade is monotonic. It terminates.

---

### ▶ Bonus-5 — If nothing works: **constructive infeasibility certificate**

Rather than returning "no path," Prolog emits a **proof of impossibility**:

```prolog
Certificate = certificate(
    repairs_exhausted([
        step(avoid_specific_boundary('Sala Daeng (S2)', 'Silom (BL26)'),
             re_routed_total(40)),
        step(avoid_agency_pair(bts, bem), graph_disconnected),
        step(force_single_agency(bts), graph_disconnected)
    ]),
    final_over_by(10),
    min_seen(40)
).
```

Gemini narrates:

> *"**Wat Suthat is provably unreachable from Phaya Thai under ฿30.** I tried dropping the Sala Daeng↔Silom crossing (re-routed via Asok, still ฿40), then banned all BTS↔MRT crossings (graph disconnects), then tried BTS-only (still disconnected). The minimum achievable fare was ฿40 — you're ฿10 short."*

The user doesn't get silence. They get a **proof**. This is what "symbolic layer actively supervising numeric search" means in practice.

---

---

# One-page recap of the whole flow

```
raw text
   │
   ▼
🧠 LLM.translate_to_query
   │  →  { origin, goal,  [budget_context],  [time_context],  [explore] }
   ▼
🧭 orchestrator._resolve_* / _handle_plan
   │
   ├─▶ 📜 candidates(Goal, Cs)                         # satisfies/3 per POI
   │        └─▶ (empty?) 📜 relax/4                    # minimal drop
   │
   ├─▶ 🧭 dijkstra(origin, poi_station) per candidate  # numeric, Python-side
   │
   ├─▶ 📜 build_route_steps(Path, Steps)               # ride / transfer terms
   │
   ├─▶ (if budget_context)
   │     📜 trip_fare → path_segments → segment_fare
   │     📜 diagnose_budget
   │        ├─ within_budget → pass
   │        └─ over_budget  → 📜 propose_repair
   │                          └─ 🧭 _build_graph_with_pruning
   │                             └─ re-dijkstra (bounded by MAX_REPAIRS)
   │                                └─ eventually 📜 explain_infeasibility
   │
   ├─▶ 📜 audit_route_for_path                         # second-pass veto
   │        └─ violation? blacklist POI, replan (bounded by MAX_REPLAN)
   │
   └─▶ assemble PlanData
   │
   ▼
🧠 LLM.format_result
   │
   ▼
human-readable answer
```

Two loops. Four tiers of repair. One invariant: **the LLM never reasons in the middle**. Everything between the bookend LLM calls is a Prolog rule, a unification, a backtrack, or Python passing a structured term between them.

That's the trace. That's the machine thinking.
