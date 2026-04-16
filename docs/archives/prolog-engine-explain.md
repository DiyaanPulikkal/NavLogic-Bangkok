# The Prolog Reasoning Engine: Scheduling & Planning

A comprehensive guide to how NavLogic Bangkok uses logic programming for transit scheduling and trip planning. Written for readers with a foundation in logic but no prior Prolog experience.

---

## Table of Contents

1. [Why Prolog?](#1-why-prolog)
2. [Prolog in 5 Minutes](#2-prolog-in-5-minutes)
3. [The Knowledge Base: Facts About Bangkok Transit](#3-the-knowledge-base-facts-about-bangkok-transit)
4. [The Schedule: Time-Constrained Transit Facts](#4-the-schedule-time-constrained-transit-facts)
5. [Trip Planning: Recursive Proof Search](#5-trip-planning-recursive-proof-search)
6. [How Prolog Proves a Trip (Worked Example)](#6-how-prolog-proves-a-trip-worked-example)
7. [Route Steps and Transfer Logic](#7-route-steps-and-transfer-logic)
8. [Station Name Resolution: Fuzzy Matching](#8-station-name-resolution-fuzzy-matching)
9. [The Prolog-Python Boundary](#9-the-prolog-python-boundary)
10. [Planning Modes: plan_trip, plan_day, plan_explore](#10-planning-modes-plan_trip-plan_day-plan_explore)
11. [Safety Mechanisms](#11-safety-mechanisms)
12. [Glossary](#12-glossary)

---

## 1. Why Prolog?

The system needs to answer questions like:

> "Can I get from Mo Chit to Hua Lamphong by 8:00 AM?"

This is fundamentally a **logical query**: given a set of facts (train schedules) and rules (connections must be temporally consistent), **prove** that a valid itinerary exists. Prolog is purpose-built for exactly this kind of reasoning:

- **Declarative**: You state *what* is true (schedules, connections), not *how* to search. Prolog's engine handles the search automatically.
- **Backtracking**: If one path doesn't work, Prolog automatically tries alternatives -- essential for exploring multi-transfer routes.
- **Unification**: Variables are matched against facts by structural pattern matching, not assignment. This makes queries expressive and concise.

The system uses Prolog for *reasoning* (what connections are valid, what routes satisfy constraints) and Python for *computation* (shortest-path algorithms, ranking, orchestration).

---

## 2. Prolog in 5 Minutes

### Facts

A fact is a statement that is unconditionally true. Think of it as a row in a database table.

```prolog
% "Siam station is on the BTS Sukhumvit line"
station('Siam (CEN)', bts_sukhumvit).

% "There is a train from Mo Chit to Saphan Khwai on BTS Sukhumvit,
%  departing at 07:00 and arriving at 07:02"
transit('Mo Chit (N8)', 'Saphan Khwai (N7)', bts_sukhumvit, 0700, 0702).
```

Lines starting with `%` are comments. Each fact ends with a period (`.`). Atoms in single quotes (`'Siam (CEN)'`) are string constants. Bare lowercase words (`bts_sukhumvit`) are also atoms. Numbers (`0700`) are integers.

### Variables

Uppercase words are **variables**. They don't hold values yet -- Prolog will figure out what they should be.

```prolog
% "What line is Siam on?"
?- station('Siam (CEN)', Line).
% Prolog answers: Line = bts_sukhumvit
```

### Rules

A rule says "the head is true **if** the body is true." The `:-` symbol reads as "if."

```prolog
% "Station S is a transfer station if it belongs to two different lines"
is_transfer_station(S) :-
    station(S, Line1),
    station(S, Line2),
    Line1 \= Line2.
```

The comma (`,`) means "and." So this reads: *S is a transfer station if S is on Line1, and S is on Line2, and Line1 is not equal to Line2.*

### How Prolog Answers Queries

When you ask Prolog a question, it doesn't loop through data imperatively. Instead, it tries to **prove** the query is true by:

1. **Unification**: Finding substitutions for variables that make the query match a fact or rule head.
2. **Resolution**: If the match is a rule, proving each condition in the rule body (left to right).
3. **Backtracking**: If a proof path fails, Prolog undoes its last choice and tries the next alternative.

This is called **SLD resolution** -- a formal proof procedure for Horn clauses.

---

## 3. The Knowledge Base: Facts About Bangkok Transit

File: `engine/knowledge_base.pl`

The knowledge base is a collection of ground facts (no variables -- every argument is a concrete value) describing Bangkok's rail network.

### Station Facts

```prolog
station('Siam (CEN)', bts_sukhumvit).
station('Siam (CEN)', bts_silom).
station('Asok (E4)', bts_sukhumvit).
station('Sukhumvit (BL22)', mrt_blue).
```

`station(Name, Line)` declares that a station named `Name` exists on line `Line`. A station appearing with multiple lines (like Siam) is an interchange station.

**Naming convention**: Station names include their line code in parentheses, e.g., `'Asok (E4)'` is the 4th station on the East (Sukhumvit) extension.

### Connection Facts (Graph Edges)

```prolog
connects('Asok (E4)', 'Phrom Phong (E5)', 2).
connects('Asok (E4)', 'Sukhumvit (BL22)', 10).
```

`connects(A, B, Time)` means you can travel from station A to station B in `Time` minutes. These are the weighted edges of the transit graph. Inter-line connections (like Asok BTS to Sukhumvit MRT) have a higher time cost (10 minutes) representing the walking transfer.

**Bidirectional edges** are derived by a rule, not duplicated as facts:

```prolog
edge(A, B, T) :- connects(A, B, T).
edge(A, B, T) :- connects(B, A, T).
```

This means: "there is an edge from A to B if there is a connection in either direction." Python's Dijkstra algorithm queries `edge/3` to build the full graph.

### Attractions and Points of Interest

```prolog
attraction('Siam Paragon').
attraction('Chatuchak Weekend Market').
attraction('Octave Rooftop Bar').       % Nightlife venues are also attractions

near_station('Siam Paragon', 'Siam (CEN)').
near_station('Octave Rooftop Bar', 'Thong Lo (E6)').
```

- `attraction(Name)` declares a point of interest.
- `near_station(Attraction, Station)` maps an attraction to its nearest station.

The compound rule `attraction_near_station/2` combines these:

```prolog
attraction_near_station(Attraction, Station) :-
    near_station(Attraction, Station),
    attraction(Attraction).
```

Nightlife venues have an additional classification predicate:

```prolog
nightlife_venue('Octave Rooftop Bar', rooftop_bar).
nightlife_venue('Route 66 Club', club).
```

But since nightlife venues are already declared as `attraction/1` facts, the main `near_station/2` query returns them alongside all other attractions.

### Location Resolution

```prolog
resolve_location(Name, Station) :- near_station(Name, Station), !.
resolve_location(Name, Name) :- valid_station(Name).
```

This two-rule predicate handles user input:
1. If `Name` is an attraction, resolve to its nearest station.
2. If `Name` is already a station name, return it as-is.

The `!` (cut) in the first rule prevents Prolog from trying the second rule after finding an attraction match.

---

## 4. The Schedule: Time-Constrained Transit Facts

File: `engine/schedule.pl`

While the knowledge base describes the network *structure* (what's connected to what), the schedule describes the network *over time* (when specific services run).

### Transit Facts

```prolog
transit(Origin, Destination, Line, Depart, Arrive).
```

Each fact represents a single scheduled train service between two adjacent stations:

```prolog
transit('Mo Chit (N8)', 'Saphan Khwai (N7)', bts_sukhumvit, 0700, 0702).
transit('Mo Chit (N8)', 'Saphan Khwai (N7)', bts_sukhumvit, 0730, 0732).
```

Key design decisions:

- **Times are integers in HHMM format**: `0700` = 07:00, `2115` = 21:15. This makes arithmetic comparison simple (`Arrive =< Deadline`).
- **Each fact is one hop**: A trip from Mo Chit to Siam requires chaining multiple `transit/5` facts. The recursive planner handles this chaining.
- **Multiple services exist per route**: The 07:00 and 07:30 departures above are separate facts. Prolog's backtracking explores all of them.
- **Transfer walks are explicit**: Walking between interchange stations (e.g., Asok BTS to Sukhumvit MRT) is modeled as a `transit/5` fact with `transfer_walk` as the line:

```prolog
transit('Asok (E4)', 'Sukhumvit (BL22)', transfer_walk, 0730, 0735).
```

### Lines Covered

| Line ID | Display Name | Direction / Coverage |
|---------|-------------|---------------------|
| `bts_sukhumvit` | BTS Sukhumvit Line | Mo Chit - On Nut (morning), Phaya Thai - Ekkamai (evening) |
| `bts_silom` | BTS Silom Line | Siam - Saphan Taksin, Siam - National Stadium |
| `mrt_blue` | MRT Blue Line | Chatuchak Park - Hua Lamphong |
| `airport_rail_link` | Airport Rail Link | Phaya Thai - Suvarnabhumi (morning), reverse (evening) |
| `transfer_walk` | Transfer (Walk) | Inter-line walking connections |

### Morning vs Evening Services

The schedule covers two time windows:
- **Morning** (~06:50 - 08:04): Outbound services from residential areas to the city center.
- **Evening** (~18:45 - 23:00): Return services and nightlife-oriented routes, including reverse directions.

---

## 5. Trip Planning: Recursive Proof Search

The heart of the scheduling engine is `plan_trip/4`. When a user asks "how do I get from A to B by time T?", the system needs to prove that a valid sequence of train rides exists.

### The Entry Point

```prolog
plan_trip(Origin, Destination, Deadline, Itinerary) :-
    plan_trip(Origin, Destination, Deadline, [Origin], 25, Itinerary).
```

This initializes two safety mechanisms:
- **Visited list** `[Origin]`: Tracks stations already used, preventing infinite cycles.
- **Depth limit** `25`: Maximum number of legs (individual train rides) allowed.

### Base Case: Direct Connection

```prolog
plan_trip(Origin, Destination, Deadline, _Visited, MaxLegs,
          [leg(Origin, Destination, Line, Depart, Arrive)]) :-
    MaxLegs > 0,
    transit(Origin, Destination, Line, Depart, Arrive),
    Arrive =< Deadline.
```

In plain English: *A trip from Origin to Destination is a single leg **if** there exists a scheduled service (`transit/5` fact) that goes directly from Origin to Destination, and it arrives before the deadline.*

The result is a list containing one `leg(...)` term.

### Recursive Case: Multi-Leg Journey

```prolog
plan_trip(Origin, Destination, Deadline, Visited, MaxLegs,
          [leg(Origin, Mid, Line, Depart, Arrive) | RestLegs]) :-
    MaxLegs > 1,
    transit(Origin, Mid, Line, Depart, Arrive),
    Mid \= Destination,
    \+ member(Mid, Visited),
    Arrive =< Deadline,
    NewMax is MaxLegs - 1,
    plan_trip(Mid, Destination, Deadline, [Mid | Visited], NewMax, RestLegs),
    first_departure(RestLegs, NextDepart),
    Arrive =< NextDepart.
```

This is where the real reasoning happens. Breaking it down:

1. **`MaxLegs > 1`** -- We need room for at least 2 legs (this one + at least one more).
2. **`transit(Origin, Mid, Line, Depart, Arrive)`** -- Find any scheduled service from Origin to some intermediate station Mid.
3. **`Mid \= Destination`** -- Mid is not the final destination (that's handled by the base case).
4. **`\+ member(Mid, Visited)`** -- Mid hasn't been visited before (cycle prevention).
5. **`Arrive =< Deadline`** -- We arrive at Mid before the overall deadline.
6. **`plan_trip(Mid, Destination, ...)`** -- **Recursively prove** that we can get from Mid to Destination (this is where Prolog dives deeper into the proof tree).
7. **`first_departure(RestLegs, NextDepart)`** -- Extract the departure time of the next leg.
8. **`Arrive =< NextDepart`** -- **Connection constraint**: we must arrive at Mid before the next train departs. You can't board a train that already left.

### What Makes This "Resolution"?

In formal logic, this is a Horn clause:

```
transit(A, Mid, L, D, Arr) AND Arr <= Deadline AND ... AND plan_trip(Mid, B, ...)
    => plan_trip(A, B, Deadline, Itinerary)
```

Prolog uses **SLD resolution** (Selective Linear Definite clause resolution) to prove goals:
- It takes the query `plan_trip(A, B, Deadline, I)` and tries to unify it with each rule head.
- When it finds a match, the rule body becomes the new set of goals to prove.
- Variables get bound through **unification** (the Most General Unifier, or MGU).
- If any subgoal fails, Prolog **backtracks** to the last choice point and tries the next alternative.

The result is a **proof tree** where each leaf is a `transit/5` fact and each internal node is a rule application. The `Itinerary` variable accumulates the legs as the proof is constructed.

---

## 6. How Prolog Proves a Trip (Worked Example)

**Query**: Get from `Mo Chit (N8)` to `Siam (CEN)` by `07:30`.

```
plan_trip('Mo Chit (N8)', 'Siam (CEN)', 0730, Itinerary).
```

### Step 1: Initialize

The entry rule expands this to:

```
plan_trip('Mo Chit (N8)', 'Siam (CEN)', 0730, ['Mo Chit (N8)'], 25, Itinerary).
```

### Step 2: Try the base case

Prolog looks for: `transit('Mo Chit (N8)', 'Siam (CEN)', Line, Dep, Arr)` with `Arr =< 0730`.

There is no direct Mo Chit to Siam service in the schedule. **Base case fails.** Prolog tries the recursive case.

### Step 3: Recursive case -- find first leg

Prolog searches for: `transit('Mo Chit (N8)', Mid, Line, Dep, Arr)`.

It finds: `transit('Mo Chit (N8)', 'Saphan Khwai (N7)', bts_sukhumvit, 0700, 0702)`.

- Mid = `'Saphan Khwai (N7)'`
- Mid is not the destination? Yes.
- Mid not visited? Yes.
- Arrive (0702) <= Deadline (0730)? Yes.

### Step 4: Recurse from Saphan Khwai

Now prove: `plan_trip('Saphan Khwai (N7)', 'Siam (CEN)', 0730, [Saphan Khwai, Mo Chit], 24, RestLegs)`.

Again, no direct service. Recurse. Prolog finds:
`transit('Saphan Khwai (N7)', 'Ari (N5)', bts_sukhumvit, 0703, 0705)`.

Connection check: 0702 <= 0703? Yes. Continue.

### Steps 5-8: Chain continues

The same process repeats through Ari, Sanam Pao, Victory Monument, Phaya Thai, Ratchathevi, each time:
- Finding the next `transit/5` fact
- Checking the connection constraint (arrival <= next departure)
- Checking the deadline constraint
- Checking for cycles

### Step 9: Base case succeeds

Finally: `transit('Ratchathevi (N1)', 'Siam (CEN)', bts_sukhumvit, 0717, 0721)`.

- This IS the destination -- base case matches.
- 0721 <= 0730? Yes.

### Result

The itinerary is built up as the recursion unwinds:

```prolog
[
    leg('Mo Chit (N8)',           'Saphan Khwai (N7)', bts_sukhumvit, 0700, 0702),
    leg('Saphan Khwai (N7)',     'Ari (N5)',           bts_sukhumvit, 0703, 0705),
    leg('Ari (N5)',              'Sanam Pao (N4)',     bts_sukhumvit, 0706, 0707),
    leg('Sanam Pao (N4)',        'Victory Monument (N3)', bts_sukhumvit, 0708, 0711),
    leg('Victory Monument (N3)', 'Phaya Thai (N2)',    bts_sukhumvit, 0712, 0714),
    leg('Phaya Thai (N2)',       'Ratchathevi (N1)',   bts_sukhumvit, 0715, 0716),
    leg('Ratchathevi (N1)',      'Siam (CEN)',         bts_sukhumvit, 0717, 0721)
]
```

### What if Prolog finds multiple solutions?

Through **backtracking**, Prolog can find alternative itineraries. For example, using the 07:30 service instead of the 07:00 service, or routing via the MRT Blue Line (Mo Chit -> Chatuchak Park via transfer walk, then MRT southbound). Each valid proof produces a different itinerary. The Python layer collects up to 100 results and deduplicates them.

---

## 7. Route Steps and Transfer Logic

File: `engine/rules.pl`

When the system finds a shortest path using Dijkstra (a list of station names), it needs to convert that raw path into human-readable steps like "take the BTS Sukhumvit Line from Asok to Siam, then transfer to BTS Silom Line."

### The route_steps Predicate

```prolog
route_steps([A, B | Rest], Steps) :-
    (   shared_line(A, B, Line)
    ->  extend_ride(Line, A, [A, B], [B | Rest], Steps)
    ;   Steps = [transfer(A, B) | RestSteps],
        route_steps([B | Rest], RestSteps)
    ).
```

This reads: *For consecutive stations A and B in the path:*
- *If they share a line, start a ride segment and try to extend it.*
- *If they don't share a line, emit a transfer step and continue.*

The `->` ; construct is Prolog's if-then-else (like a ternary operator).

### Greedy Ride Extension

```prolog
extend_ride(Line, Board, Acc, [C, D | Rest], Steps) :-
    (   shared_line(C, D, Line)
    ->  extend_ride(Line, Board, [Acc + D], [D | Rest], Steps)
    ;   Steps = [ride(Line, Board, C, Acc) | RestSteps],
        route_steps([C, D | Rest], RestSteps)
    ).
```

This greedily extends a ride: keep going on the same line as long as consecutive stations share it. When the line changes, emit the ride step and start fresh.

### Transfer Station Detection

```prolog
is_transfer_station(Station) :-
    station(Station, Line1),
    station(Station, Line2),
    Line1 \= Line2.
```

A station is a transfer station if it appears on two different lines. This is pure logical inference -- no separate "transfer station" table is needed.

### Line Display Names

```prolog
line_display_name(bts_sukhumvit, 'BTS Sukhumvit Line').
line_display_name(transfer_walk, 'Transfer (Walk)').
```

These map internal line identifiers to human-readable names for the UI.

---

## 8. Station Name Resolution: Fuzzy Matching

Users type informal names ("Siam", "Mo Chit", "Grand Palace"). The system needs to resolve these to exact station names. This is a **hybrid Prolog + Python** approach.

### Prolog's Role: Classification

```prolog
% Exact match (case-insensitive)
match_station(Input, Station, exact) :-
    downcase_atom(Input, InputLower),
    station(Station, _),
    downcase_atom(Station, StationLower),
    InputLower = StationLower.

% Prefix match
match_station(Input, Station, prefix) :-
    downcase_atom(Input, InputLower),
    station(Station, _),
    downcase_atom(Station, StationLower),
    \+ InputLower = StationLower,
    sub_atom(StationLower, 0, _, _, InputLower).

% Substring match
match_station(Input, Station, substring) :-
    % ... similar, but input appears anywhere in the station name
```

Prolog generates all candidate stations and classifies each as `exact`, `prefix`, or `substring`. This leverages Prolog's built-in string operations and backtracking to exhaustively search all stations.

### Python's Role: Ranking

Python receives the classified candidates and ranks them:

1. **Match type priority**: exact > prefix > substring
2. **String similarity** (via `SequenceMatcher`): Breaks ties within the same match type.
3. **Edit distance fallback**: If Prolog finds no matches at all, Python tries edit-distance matching against all station names to handle typos (e.g., "Saim" -> "Siam").

This division of labor plays to each language's strengths: Prolog handles exhaustive search and pattern classification; Python handles scoring and ranking.

---

## 9. The Prolog-Python Boundary

The system uses `pyswip` to embed SWI-Prolog within the Python process. Here's how they communicate:

### Python Calls Prolog

```python
# Python sends a query string
results = list(self.prolog.query("plan_trip('Mo Chit (N8)', 'Siam (CEN)', 0730, Itinerary)"))

# pyswip returns a list of dicts, one per solution
# Each dict maps variable names to their unified values
# results[0]['Itinerary'] contains the leg list
```

### Data Flow

```
User text
   |
   v
LLM (Gemini) -- extracts intent + parameters via function calling
   |
   v
Orchestrator (Python) -- resolves names, dispatches to handler
   |
   v
PrologInterface (Python) -- sends queries to Prolog, parses results
   |
   v
SWI-Prolog -- unification + resolution over facts/rules
   |
   v
PrologInterface -- converts Prolog terms to Python dicts
   |
   v
Orchestrator -- formats result, sends back through LLM for natural language
   |
   v
User response (JSON)
```

### Key Interface Methods

| Method | Prolog Query | Returns |
|--------|-------------|---------|
| `plan_trip(origin, dest, deadline)` | `plan_trip(O, D, Deadline, Itinerary)` | List of itineraries (each a list of leg dicts) |
| `get_all_edges()` | `edge(A, B, T)` | List of `(station_a, station_b, time)` tuples |
| `build_route_steps(path)` | `route_steps(Path, Steps)` | List of ride/transfer step dicts |
| `match_station_classified(name)` | `match_station(Name, Station, Type)` | List of `{station, match_type}` dicts |
| `resolve_location(name)` | `resolve_location(Name, Station)` | Station name string or None |
| `attractions_near(station)` | `attraction_near_station(A, Station)` | List of attraction name strings |

---

## 10. Planning Modes: plan_trip, plan_day, plan_explore

The system supports three planning modes, each combining Prolog reasoning with Python computation differently.

### plan_trip: Schedule-Based Trip Planning

**Use case**: "I need to get from Mo Chit to Hua Lamphong by 8:00 AM."

**Engine**: Prolog `plan_trip/4` (resolution-based proof search over schedule facts).

**Flow**:
1. Resolve origin and destination station names.
2. Parse the deadline time.
3. Query Prolog's `plan_trip/4` with a 10-second timeout.
4. Collect up to 100 raw itineraries, deduplicate.
5. Format leg times (`0700` -> `"07:00"`) via Prolog's `format_itinerary/2`.
6. Pass to LLM for natural language formatting.

**What Prolog does**: All the temporal reasoning -- finding services, checking connection times, enforcing the deadline.

**What Python does**: Name resolution, timeout management, deduplication, LLM orchestration.

### plan_day: Multi-Stop Day Planning

**Use case**: "I want to visit Siam by 10:00 and then Sam Yan by 13:00, starting from Mo Chit."

**Engine**: Prolog `plan_trip/4` (called once per leg) + Prolog `attraction_near_station/2`.

**Flow**:
1. Resolve all stop names.
2. For each consecutive pair of stops:
   - Call `plan_trip/4` to find scheduled connections.
   - Call `attraction_near_station/2` to find nearby attractions at the destination.
3. Assemble the full day plan with transit legs and attraction suggestions.

**What Prolog does**: Per-leg scheduling + attraction lookup.

**What Python does**: Sequencing stops, assembling the plan structure.

### plan_explore: Auto-Discovery Exploration

**Use case**: "I'm at Siam and want to explore Bangkok from 7pm to midnight."

**Engine**: Python Dijkstra (fastest paths) + Prolog knowledge base (attractions).

**Flow**:
1. Query Prolog for all attractions grouped by station (`get_attractions_by_station()`).
2. Query Prolog for all graph edges (`get_all_edges()`).
3. Run Dijkstra from the origin to every station that has attractions.
4. Sort by travel time, select up to 4 diverse stops (avoiding stations too close together).
5. Calculate suggested arrival times spread across the time window.
6. For each selected stop, compute the Dijkstra route.
7. If the time window extends past midnight, add a "last train" advisory note.

**What Prolog does**: Attraction and station data retrieval.

**What Python does**: Dijkstra routing, stop selection, time window calculation. Schedule-based Prolog planning is *not* used here because the goal is exploration (optimize for variety and coverage) rather than time-constrained point-to-point travel.

---

## 11. Safety Mechanisms

Several safeguards prevent runaway searches and infinite loops:

### In Prolog

| Mechanism | Where | Purpose |
|-----------|-------|---------|
| **Visited list** | `plan_trip/6` | Prevents cycles (e.g., Asok -> Sukhumvit -> Asok -> ...) |
| **Depth limit (25 legs)** | `plan_trip/6` | Caps search depth to prevent combinatorial explosion |
| **Connection constraint** | Recursive rule | `Arrive =< NextDepart` ensures temporally valid connections |
| **Deadline constraint** | Both cases | `Arrive =< Deadline` prunes paths that arrive too late |

### In Python

| Mechanism | Where | Purpose |
|-----------|-------|---------|
| **10-second timeout** | `plan_trip()` in `prolog.py` | Kills Prolog search if it runs too long (via `call_with_time_limit`) |
| **100-result cap** | `plan_trip()` in `prolog.py` | Limits raw results via `itertools.islice` |
| **Deduplication** | `plan_trip()` in `prolog.py` | Removes identical itineraries (same from/to/depart/arrive per leg) |
| **Dijkstra for routing** | `_dijkstra()` in `orchestrator.py` | O(E log V) shortest path, guaranteed termination |

---

## 12. Glossary

| Term | Definition |
|------|-----------|
| **Fact** | An unconditionally true statement in Prolog (e.g., `station('Siam', bts_sukhumvit).`) |
| **Rule** | A conditional statement: the head is true if the body is true (`head :- body.`) |
| **Predicate** | A named relation with a fixed number of arguments (e.g., `station/2` has 2 arguments) |
| **Unification** | The process of finding variable substitutions that make two terms identical |
| **MGU** | Most General Unifier -- the simplest substitution that unifies two terms |
| **Backtracking** | Prolog's mechanism for trying alternative choices when a proof path fails |
| **SLD Resolution** | The formal proof procedure Prolog implements (Selective Linear Definite clause resolution) |
| **Horn Clause** | A logical formula with at most one positive literal; all Prolog rules are Horn clauses |
| **Cut (`!`)** | Prevents backtracking past a certain point, committing to the current choice |
| **Atom** | A constant value in Prolog (e.g., `bts_sukhumvit`, `'Siam (CEN)'`) |
| **Ground term** | A term with no variables -- all arguments are concrete values |
| **`\+`** | Negation as failure: `\+ goal` succeeds if `goal` cannot be proven |
| **HHMM** | Time encoding as integer: hours * 100 + minutes (e.g., 0730 = 07:30) |
