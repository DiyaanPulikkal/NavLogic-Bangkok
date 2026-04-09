# Orchestrator & Prolog Engine — Technical Documentation

This document provides a comprehensive explanation of how the **Orchestrator** (`engine/orchestrator.py`) and **Prolog Engine** (`engine/prolog.py`, `engine/knowledge_base.pl`, `engine/schedule.pl`, `engine/rules.pl`) work together to power NavLogic Bangkok's transit intelligence.

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [End-to-End Request Flow](#2-end-to-end-request-flow)
3. [The Orchestrator](#3-the-orchestrator)
   - 3.1 [Initialization](#31-initialization)
   - 3.2 [Main Dispatch: `handle()`](#32-main-dispatch-handle)
   - 3.3 [Function Handlers](#33-function-handlers)
   - 3.4 [Station Name Resolution Pipeline](#34-station-name-resolution-pipeline)
   - 3.5 [Dijkstra Route Finding](#35-dijkstra-route-finding)
   - 3.6 [Direct API Methods (LLM Bypass)](#36-direct-api-methods-llm-bypass)
4. [The Prolog Engine](#4-the-prolog-engine)
   - 4.1 [Architecture: pyswip Bridge](#41-architecture-pyswip-bridge)
   - 4.2 [Knowledge Base (`knowledge_base.pl`)](#42-knowledge-base-knowledge_basepl)
   - 4.3 [Inference Rules (`rules.pl`)](#43-inference-rules-rulespl)
   - 4.4 [Schedule & Trip Planning (`schedule.pl`)](#44-schedule--trip-planning-schedulepl)
   - 4.5 [PrologInterface Methods](#45-prologinterface-methods)
5. [Prolog Reasoning In Depth](#5-prolog-reasoning-in-depth)
   - 5.1 [First-Order Logic Foundations](#51-first-order-logic-foundations)
   - 5.2 [Unification and Resolution](#52-unification-and-resolution)
   - 5.3 [Trip Planning Proof Tree](#53-trip-planning-proof-tree)
   - 5.4 [Cycle Prevention and Depth Bounding](#54-cycle-prevention-and-depth-bounding)
6. [Hybrid Prolog + Python Design](#6-hybrid-prolog--python-design)
7. [Data Flow Diagrams](#7-data-flow-diagrams)

---

## 1. System Overview

NavLogic Bangkok uses a **hybrid architecture** where:

- **Prolog** handles logical reasoning: station/line facts, attraction lookups, fuzzy name matching, route step inference, transfer station suggestions, and time-constrained trip planning via SLD resolution.
- **Python** handles algorithmic computation: Dijkstra shortest-path routing, candidate ranking with edit-distance scoring, graph construction, and response formatting.
- **Google Gemini LLM** handles natural language: extracting structured function calls from user text (intent extraction) and formatting structured results back into human-readable responses.

```
User query (natural language)
       |
       v
  Gemini LLM  -->  extracts function call (e.g. find_route, plan_trip)
       |
       v
  Orchestrator  -->  dispatches to the correct handler
       |
       v
  Prolog KB + Python Dijkstra  -->  computes result
       |
       v
  Gemini LLM  -->  formats result as natural language
       |
       v
  JSON response to frontend
```

---

## 2. End-to-End Request Flow

Here is the complete lifecycle of a user query like *"How do I get from Chatuchak to Terminal 21?"*:

1. **Frontend** sends POST to `/api/query` with the user's message and conversation history.
2. **API layer** (`app.py`) forwards to `Orchestrator.handle(user_input, history)`.
3. **LLM intent extraction**: `LLMInterface.translate_to_query()` sends the message to Gemini with function declarations. Gemini returns a structured function call:
   ```
   ("find_route", {"start": "Chatuchak", "end": "Terminal 21"})
   ```
4. **Orchestrator dispatch**: `handle()` sees `function_name == 'find_route'` and calls `_handle_find_route(arguments)`.
5. **Name resolution**: The orchestrator resolves "Chatuchak" and "Terminal 21" to canonical station names:
   - "Chatuchak" -> Prolog `resolve_location` -> no exact match -> `match_station_classified` finds "Chatuchak Park (BL13)" via substring match -> returns it.
   - "Terminal 21" -> Prolog `resolve_location` -> matches attraction `near_station('Terminal 21', 'Asok (E4)')` -> returns "Asok (E4)".
6. **Route computation**: Python Dijkstra runs on the graph built from Prolog `edge/3` facts, finding the shortest path from "Chatuchak Park (BL13)" to "Asok (E4)".
7. **Step building**: The path is sent back to Prolog's `route_steps/2` which infers ride segments and transfer points using `shared_line/3` and `line_display_name/2`.
8. **LLM formatting**: The structured route result is sent back to Gemini via `format_prolog_result()`, which generates a natural language description.
9. **Response**: The formatted JSON is returned to the frontend.

---

## 3. The Orchestrator

**File**: `engine/orchestrator.py`

The Orchestrator is the central dispatcher that ties together the LLM, Prolog, and Python algorithms.

### 3.1 Initialization

```python
class Orchestrator:
    def __init__(self):
        self.llm = LLMInterface()     # Gemini client
        self.prolog = PrologInterface() # pyswip Prolog engine
```

On construction, the Prolog engine loads `knowledge_base.pl` (which also loads `rules.pl`) and `schedule.pl`. The LLM client is initialized with Gemini and the system prompt.

### 3.2 Main Dispatch: `handle()`

```python
def handle(self, user_input: str, history: list | None = None) -> tuple[dict, list]:
```

This is the primary entry point. The dispatch logic is:

| LLM Returns | Action |
|---|---|
| `None` | Return error: "couldn't process your request" |
| Plain text `str` | Return as-is (conversational response, no Prolog needed) |
| `("find_route", args)` | `_handle_find_route(args)` — Dijkstra routing |
| `("plan_trip", args)` | `_handle_plan_trip(args)` — Schedule-based trip planning |
| `("plan_day", args)` | `_handle_plan_day(args)` — Multi-stop day planning |
| `("plan_explore", args)` | `_handle_plan_explore(args)` — Auto-discover explore planner |
| `("line_of", args)` | Knowledge-base Prolog query |
| `("same_line", args)` | Knowledge-base Prolog query |
| `("is_transfer_station", args)` | Knowledge-base Prolog query |
| `("needs_transfer", args)` | Knowledge-base Prolog query |
| `("attraction_near_station", args)` | Knowledge-base Prolog query |

For knowledge-base queries, the orchestrator:
1. Resolves station names in the arguments using `_resolve_location()`.
2. Builds a Prolog query string from `PROLOG_QUERY_MAP`.
3. Executes the query via `PrologInterface.query()`.
4. Sends the result back through the LLM for natural language formatting.

### 3.3 Function Handlers

#### `_handle_find_route(arguments)`
- Resolves start/end station names.
- Calls `_find_and_format_route()` which runs Python Dijkstra on Prolog edge data, then delegates route step building back to Prolog.
- Returns type `"route"` with steps, total time, and endpoints.

#### `_handle_plan_trip(arguments, history)`
- Resolves origin/destination station names.
- Parses deadline time string (e.g. "08:00") to HHMM integer (800).
- Calls `PrologInterface.plan_trip()` which executes the recursive `plan_trip/4` Prolog rule.
- Deduplicates itineraries and sends to LLM for formatting.
- Returns type `"schedule"` with itineraries.

#### `_handle_plan_day(arguments, history)`
- Resolves origin and all stop locations.
- For each leg (origin -> stop1 -> stop2 -> ...):
  - Plans the transit route via `prolog.plan_trip()`.
  - Finds nearby attractions via `prolog.attractions_near()`.
- Returns type `"day_plan"` with legs, itineraries, and attraction recommendations.

#### `_handle_plan_explore(arguments, history)`
- The most complex handler. Combines Python Dijkstra with Prolog KB queries.
- Resolves origin, parses start/end time window.
- Queries Prolog for **all** attractions and nightlife venues grouped by station.
- Merges them into a unified points-of-interest (POI) map per station.
- Runs Python Dijkstra from origin to every station with POIs.
- Selects up to 4 diverse stops (using `_select_explore_stops()` which skips stations too close in travel time).
- Distributes arrival times evenly across the time window.
- Builds route legs using Dijkstra for each consecutive pair.
- Adds a late-night/past-midnight note if applicable.
- Returns type `"explore"` with legs, stops, and POIs.

### 3.4 Station Name Resolution Pipeline

The `_resolve_location()` method implements a **three-tier fallback** strategy:

```
User input: "Chatuchak"
      |
      v
  1. Prolog resolve_location/2 (exact match)
     - Checks near_station/2 (attraction → station mapping)
     - Checks valid_station/1 (exact station name)
     - Result: None (no exact match)
      |
      v
  2. Prolog match_station/3 (classified fuzzy match)
     - Tries exact (case-insensitive full name match)
     - Tries prefix (station name starts with input)
     - Tries substring (input appears in station name)
     - Result: [{"station": "Chatuchak Park (BL13)", "match_type": "substring"}]
      |
      v
  3. Python _rank_candidates() (hybrid scoring)
     - Sort by: match_type priority (exact > prefix > substring)
     - Tie-break by: SequenceMatcher similarity ratio
     - Reject substring matches with similarity < 0.4
     - Result: "Chatuchak Park (BL13)"
```

If step 2 returns no candidates, the system falls through to:

```
  4. Python _best_edit_distance_match() (typo correction)
     - Compares against base names (without station codes)
     - Requires similar length (±1 character)
     - Threshold: similarity >= 0.75
     - Example: "Saim" → "Siam (CEN)"
```

**Why this hybrid design?**
- Prolog handles the *classification logic* (what kind of match: exact, prefix, substring) using its pattern matching strengths.
- Python handles the *ranking and scoring* (SequenceMatcher, edit distance) where numerical computation is more natural.

### 3.5 Dijkstra Route Finding

The orchestrator contains a standard Dijkstra implementation:

```python
def _dijkstra(self, graph, start, end):
    heap = [(0, start, [start])]
    visited = set()
    while heap:
        cost, node, path = heapq.heappop(heap)
        if node in visited:
            continue
        visited.add(node)
        if node == end:
            return path, cost
        for neighbor, weight in graph.get(node, []):
            if neighbor not in visited:
                heapq.heappush(heap, (cost + weight, neighbor, path + [neighbor]))
    return None, None
```

The graph is built from Prolog's `edge/3` facts (which are derived from `connects/3` with bidirectionality):
```prolog
edge(A,B,T) :- connects(A,B,T).
edge(A,B,T) :- connects(B,A,T).
```

**Why Python Dijkstra instead of Prolog path-finding?**
- Dijkstra is an imperative algorithm that benefits from mutable heaps and visited sets.
- The transit network has ~100+ stations with cross-line transfers, making BFS/DFS in Prolog inefficient.
- Prolog's `plan_trip/4` is used separately for *time-constrained* trip planning where logical inference over timetable facts is the correct approach.

### 3.6 Direct API Methods (LLM Bypass)

Several methods bypass the LLM for direct API access:

| Method | Used By | Description |
|---|---|---|
| `find_route(start, end)` | `/api/route` | Direct route finding |
| `plan_trip(origin, dest, deadline)` | `/api/schedule` | Direct schedule query |
| `get_all_stations_with_lines()` | `/api/stations` | List all stations with their lines |
| `get_all_attractions()` | `/api/attractions` | List all attractions with nearest stations |

---

## 4. The Prolog Engine

### 4.1 Architecture: pyswip Bridge

**File**: `engine/prolog.py`

`PrologInterface` wraps [pyswip](https://github.com/yuce/pyswip), a Python-SWI-Prolog bridge. On macOS with Homebrew, it auto-detects the SWI-Prolog library path at import time.

```python
class PrologInterface:
    def __init__(self):
        self.prolog = Prolog()
        self.prolog.consult(KB_PATH)       # knowledge_base.pl (also loads rules.pl)
        self.prolog.consult(SCHEDULE_PATH)  # schedule.pl
```

Key design decisions:
- **Query validation**: `is_valid_query()` validates that queries match the pattern `predicate(args).` before execution.
- **String stripping**: The trailing `.` is stripped before passing to pyswip (which doesn't expect it).
- **Result conversion**: pyswip returns results as lists of dicts mapping Prolog variable names to values. PrologInterface converts these to native Python types.

### 4.2 Knowledge Base (`knowledge_base.pl`)

This file contains the ground truth **facts** about Bangkok's transit network. It is pure declarative knowledge with no procedural logic.

#### Station Facts
```prolog
station(StationName, LineId).
```
Every station in the network has one or more `station/2` facts associating it with a transit line.

**Lines in the knowledge base:**
| Line ID | Name | Stations |
|---|---|---|
| `bts_sukhumvit` | BTS Sukhumvit Line | 48 stations (N24 to E23, via Siam CEN) |
| `bts_silom` | BTS Silom Line | 13 stations (W1, S1-S12, via Siam CEN) |
| `gold` | BTS Gold Line | 3 stations (G1-G3) |
| `mrt_blue` | MRT Blue Line | 38 stations (BL01-BL38) |
| `airport_rail_link` | Airport Rail Link | 8 stations (A1-A8) |

**Multi-line stations** (stations that appear in multiple lines, making them transfer stations):
- `Siam (CEN)` — bts_sukhumvit + bts_silom

#### Connection Facts
```prolog
connects(StationA, StationB, TravelTimeMinutes).
```
Directed connection facts with travel time in minutes. Made bidirectional via the `edge/3` rule.

**Inter-line connections** have a travel time of 10 minutes (representing walking transfers):
```prolog
connects('Mo Chit (N8)', 'Chatuchak Park (BL13)', 10).       % BTS ↔ MRT
connects('Asok (E4)', 'Sukhumvit (BL22)', 10).               % BTS ↔ MRT
connects('Phaya Thai (N2)', 'Phaya Thai (A8)', 10).           % BTS ↔ ARL
connects('Silom (BL26)', 'Sala Daeng (S2)', 10).              % MRT ↔ BTS
connects('Bang Wa (S12)', 'Bang Wa (BL34)', 10).              % BTS ↔ MRT
connects('Krung Thon Buri (S7)', 'Krung Thon Buri (G1)', 10).% BTS ↔ Gold
connects('Makkasan (A6)', 'Phetchaburi (BL21)', 10).          % ARL ↔ MRT
connects('Ha Yaek Lat Phrao (N9)', 'Phahon Yothin (BL14)', 10). % BTS ↔ MRT
```

#### Attraction Facts
```prolog
attraction(AttractionName).
near_station(AttractionName, StationName).
```
Two-part structure: `attraction/1` declares an attraction exists, `near_station/2` maps it to its nearest station. The `attraction_near_station/2` rule joins them.

**Attraction categories** include:
- Shopping malls (Siam Paragon, Terminal 21, MBK Center, etc.)
- Temples and landmarks (Grand Palace, Wat Pho, Wat Traimit)
- Parks (Lumpini Park, Benchasiri Park, Benjakitti Park)
- Markets (Chatuchak Weekend Market, Jodd Fairs, Pratunam Market)
- Nightlife venues (see below)

#### Nightlife Venue Classification
```prolog
nightlife_venue(VenueName, Category).
```
Venues are classified into categories: `rooftop_bar`, `club`, `bar`, `speakeasy`, `bar_street`, `entertainment_district`, `night_market`.

The `nightlife_near_station/3` rule joins venue classification with station proximity:
```prolog
nightlife_near_station(Venue, Category, Station) :-
    nightlife_venue(Venue, Category),
    near_station(Venue, Station).
```

#### Reasoning Rules (in knowledge_base.pl)

```prolog
% What line(s) does a station serve?
line_of(Station, Line) :- station(Station, Line).

% Do two stations share a line?
same_line(A, B) :- station(A, Line), station(B, Line).

% Is a station an interchange? (belongs to 2+ lines)
is_transfer_station(S) :- station(S, L1), station(S, L2), L1 \= L2.

% Does traveling between two stations require a transfer?
needs_transfer(A, B) :- \+ same_line(A, B).

% Bidirectional edges (used by Python Dijkstra)
edge(A,B,T) :- connects(A,B,T).
edge(A,B,T) :- connects(B,A,T).

% Location resolution: attraction name → station, or direct station name
resolve_location(Name, Station) :- near_station(Name, Station), !.
resolve_location(Name, Name) :- valid_station(Name).

% Station existence check
valid_station(S) :- station(S, _).
```

### 4.3 Inference Rules (`rules.pl`)

**File**: `engine/rules.pl`

This file contains the more complex Prolog rules that involve multi-step inference.

#### Line Display Names
```prolog
line_display_name(bts_sukhumvit, 'BTS Sukhumvit Line').
line_display_name(mrt_blue, 'MRT Blue Line').
% ... etc.
```
Maps internal line IDs to human-readable names for display.

#### Station Matching (Classified)

Three-tiered matching with explicit classification:

```prolog
% Tier 1: Exact match (case-insensitive)
match_station(Input, Station, exact) :-
    downcase_atom(Input, InputLower),
    station(Station, _),
    downcase_atom(Station, StationLower),
    InputLower = StationLower.

% Tier 2: Prefix match (station starts with input)
match_station(Input, Station, prefix) :-
    downcase_atom(Input, InputLower),
    station(Station, _),
    downcase_atom(Station, StationLower),
    \+ InputLower = StationLower,                     % exclude exact
    sub_atom(StationLower, 0, _, _, InputLower).

% Tier 3: Substring match (input appears anywhere in station name)
match_station(Input, Station, substring) :-
    downcase_atom(Input, InputLower),
    station(Station, _),
    downcase_atom(Station, StationLower),
    \+ InputLower = StationLower,                     % exclude exact
    \+ sub_atom(StationLower, 0, _, _, InputLower),   % exclude prefix
    sub_atom(StationLower, _, _, _, InputLower).
```

**Key design**: Each tier explicitly excludes matches from higher tiers, so the match type classification is unambiguous. Prolog's `sub_atom/5` built-in handles the string matching efficiently.

#### Route Steps Inference

The `route_steps/2` predicate takes an ordered list of stations (from Dijkstra) and groups them into ride segments and transfer steps:

```prolog
route_steps([A, B | Rest], Steps) :-
    (   shared_line(A, B, Line)
    ->  extend_ride(Line, A, [A, B], [B | Rest], Steps)
    ;   Steps = [transfer(A, B) | RestSteps],
        route_steps([B | Rest], RestSteps)
    ).
```

Logic:
1. If consecutive stations A and B share a line, start a **ride segment** and greedily extend it.
2. If they don't share a line, insert a **transfer step** and continue.

`extend_ride/5` accumulates stations on the same line until a line change is detected:
```prolog
extend_ride(Line, Board, Acc, [C, D | Rest], Steps) :-
    (   shared_line(C, D, Line)
    ->  append(Acc, [D], NewAcc),
        extend_ride(Line, Board, NewAcc, [D | Rest], Steps)
    ;   line_display_name(Line, DisplayLine),
        Steps = [ride(DisplayLine, Board, C, Acc) | RestSteps],
        route_steps([C, D | Rest], RestSteps)
    ).
```

**Output terms:**
- `ride(LineName, BoardStation, AlightStation, StationsList)` — a continuous ride on one line
- `transfer(FromStation, ToStation)` — a walking transfer between lines

#### Transfer Station Suggestions

```prolog
% Direct: same physical station serves both lines
suggest_transfer_station(LineA, LineB, TransferStation) :-
    LineA \= LineB,
    station(TransferStation, LineA),
    station(TransferStation, LineB).

% Indirect: walk between connected stations on different lines
suggest_transfer_station(LineA, LineB, transfer_pair(StationA, StationB)) :-
    LineA \= LineB,
    station(StationA, LineA),
    station(StationB, LineB),
    (connects(StationA, StationB, _) ; connects(StationB, StationA, _)),
    StationA \= StationB.
```

Returns either a station name (same-station transfer) or a `transfer_pair(A, B)` compound term (walking transfer).

### 4.4 Schedule & Trip Planning (`schedule.pl`)

**File**: `engine/schedule.pl`

This is the most logically sophisticated part of the system. It demonstrates **First-Order Logic (FOL)** principles using Prolog's SLD resolution engine.

#### Transit Schedule Facts
```prolog
transit(Origin, Destination, Line, DepartTime, ArriveTime).
```
Each fact represents a single scheduled service between adjacent stations. Times are integers in HHMM format (e.g., `0730` = 7:30 AM, `2115` = 9:15 PM).

The schedule covers:
- **Morning services** (~07:00-08:00): BTS Sukhumvit, BTS Silom, MRT Blue, Airport Rail Link
- **Evening services** (~18:45-23:00): All lines with multiple service patterns
- **Transfer walks**: Inter-line walking transfers at various times throughout the day

Each line typically has 2-3 service patterns (e.g., 07:00 departure and 07:30 departure).

#### Trip Planning Rules

**Public entry point:**
```prolog
plan_trip(Origin, Destination, Deadline, Itinerary) :-
    plan_trip(Origin, Destination, Deadline, [Origin], 25, Itinerary).
```
Initializes the visited-station list (for cycle prevention) and sets a max depth of 25 legs.

**Base case (direct trip):**
```prolog
plan_trip(Origin, Destination, Deadline, _Visited, MaxLegs,
          [leg(Origin, Destination, Line, Depart, Arrive)]) :-
    MaxLegs > 0,
    transit(Origin, Destination, Line, Depart, Arrive),
    Arrive =< Deadline.
```
A direct connection exists where arrival is before the deadline.

**Recursive case (multi-leg trip):**
```prolog
plan_trip(Origin, Destination, Deadline, Visited, MaxLegs,
          [leg(Origin, Mid, Line, Depart, Arrive) | RestLegs]) :-
    MaxLegs > 1,
    transit(Origin, Mid, Line, Depart, Arrive),
    Mid \= Destination,
    \+ member(Mid, Visited),        % cycle prevention
    Arrive =< Deadline,
    NewMax is MaxLegs - 1,
    plan_trip(Mid, Destination, Deadline, [Mid | Visited], NewMax, RestLegs),
    first_departure(RestLegs, NextDepart),
    Arrive =< NextDepart.           % connection constraint
```

**Constraints enforced:**
1. **Deadline**: All arrivals must be before the user's deadline (`Arrive =< Deadline`).
2. **Connection timing**: You can't board the next service before arriving at the transfer station (`Arrive =< NextDepart`).
3. **Cycle prevention**: The `Visited` list ensures no station is visited twice.
4. **Depth bound**: `MaxLegs` (initialized to 25) prevents infinite search.

#### Formatting Helpers
```prolog
format_time(HHMM, Formatted) :-
    Hours is HHMM // 100,
    Minutes is HHMM mod 100,
    format(atom(Formatted), '~|~`0t~d~2+:~|~`0t~d~2+', [Hours, Minutes]).

format_itinerary([], []).
format_itinerary([leg(From, To, Line, Dep, Arr) | Rest],
                 [formatted_leg(From, To, DisplayLine, DepStr, ArrStr) | FormattedRest]) :-
    format_time(Dep, DepStr),
    format_time(Arr, ArrStr),
    (line_display_name(Line, DisplayLine) -> true ; DisplayLine = Line),
    format_itinerary(Rest, FormattedRest).
```

Converts internal `leg/5` terms to `formatted_leg/5` terms with human-readable times and line names.

### 4.5 PrologInterface Methods

Here is a complete reference of `PrologInterface` methods and their Prolog queries:

| Python Method | Prolog Query | Returns |
|---|---|---|
| `query(q)` | Any validated query | Raw Prolog result list |
| `get_all_edges()` | `edge(A, B, T)` | List of `(station, station, time)` tuples |
| `get_station_lines()` | `station(S, L)` | Dict: station → [lines] |
| `resolve_location(name)` | `resolve_location(Name, Station)` | Station name or `None` |
| `is_valid_station(name)` | `valid_station(Name)` | Boolean |
| `get_all_station_names()` | `station(S, _)` | List of station names |
| `build_route_steps(path)` | `route_steps(Path, Steps)` | List of step dicts |
| `fuzzy_match_station(name)` | `fuzzy_match_station(Name, Station)` | List of matching stations |
| `match_station_classified(name)` | `match_station(Name, Station, MatchType)` | List of `{station, match_type}` dicts |
| `suggest_transfer_station(a, b)` | `suggest_transfer_station(A, B, Transfer)` | List of transfer options |
| `get_line_display_name(id)` | `line_display_name(Id, Name)` | Display name string |
| `plan_trip(o, d, deadline)` | `plan_trip(O, D, Deadline, Itinerary)` | List of itinerary lists |
| `attractions_near(station)` | `attraction_near_station(A, Station)` | List of attraction names |
| `get_attractions_by_station()` | `near_station(A, S)` | Dict: station → [attractions] |
| `get_nightlife_venues()` | `nightlife_near_station(V, C, S)` | Dict: station → [{name, category}] |

#### Plan Trip Query Details

The `plan_trip` method wraps the Prolog query with safety measures:

```python
query = (
    f"catch("
    f"call_with_time_limit({SCHEDULE_QUERY_TIMEOUT}, "
    f"(plan_trip('{origin}', '{destination}', {deadline}, Itinerary), "
    f"format_itinerary(Itinerary, Formatted))"
    f"), time_limit_exceeded, fail)"
)
results = list(islice(self.prolog.query(query), 100))
```

- **`call_with_time_limit(10, ...)`**: Prevents runaway Prolog searches (10 second timeout).
- **`catch(..., time_limit_exceeded, fail)`**: Gracefully handles timeout by failing instead of throwing.
- **`islice(..., 100)`**: Limits raw results to 100 to avoid combinatorial explosion.
- **Deduplication**: Results are deduplicated by `(from, to, depart, arrive)` tuples.

#### Parsing Prolog Terms

pyswip returns complex Prolog terms as strings. `PrologInterface` includes parsers:

- `_parse_route_steps(steps_term)`: Parses `ride(...)` and `transfer(...)` terms.
- `_parse_ride_step(s)`: Extracts line, board, alight, and station list from a ride term.
- `_parse_formatted_legs(formatted_term)`: Extracts leg details from `formatted_leg(...)` terms.
- `_split_top_level(s)`: Utility to split comma-separated strings while respecting nested parentheses and brackets.

---

## 5. Prolog Reasoning In Depth

### 5.1 First-Order Logic Foundations

The system demonstrates several FOL concepts:

**Ground atoms** (facts with no variables):
```prolog
station('Siam (CEN)', bts_sukhumvit).
transit('Mo Chit (N8)', 'Saphan Khwai (N7)', bts_sukhumvit, 0700, 0702).
```

**Universally quantified rules** (Horn clauses):
```prolog
% For all stations S and lines L1, L2:
%   if S is on L1 and S is on L2 and L1 != L2, then S is a transfer station.
is_transfer_station(S) :- station(S, L1), station(S, L2), L1 \= L2.
```

In clause normal form (CNF):
```
~station(S, L1) v ~station(S, L2) v L1 = L2 v is_transfer_station(S)
```

### 5.2 Unification and Resolution

When you query `plan_trip('Mo Chit (N8)', 'Siam (CEN)', 0800, Itinerary)`:

1. **Prolog attempts to unify** the query with the head of the `plan_trip/4` entry point rule.
   - `Origin = 'Mo Chit (N8)'`, `Destination = 'Siam (CEN)'`, `Deadline = 0800`, `Itinerary = ?`

2. **The body becomes the new goal**: `plan_trip('Mo Chit (N8)', 'Siam (CEN)', 0800, ['Mo Chit (N8)'], 25, Itinerary)`

3. **Base case attempted**: Prolog tries to find `transit('Mo Chit (N8)', 'Siam (CEN)', Line, Dep, Arr)` — no such direct service exists, so it fails.

4. **Recursive case attempted**: Prolog finds `transit('Mo Chit (N8)', 'Saphan Khwai (N7)', bts_sukhumvit, 0700, 0702)`, then recursively tries to plan from `'Saphan Khwai (N7)'` to `'Siam (CEN)'`.

5. **Resolution continues** through intermediate stations until Siam is reached. Each step checks timing constraints.

### 5.3 Trip Planning Proof Tree

For a query `plan_trip('Mo Chit (N8)', 'Siam (CEN)', 0800, Itinerary)`:

```
plan_trip('Mo Chit (N8)', 'Siam (CEN)', 0800, Itin)
  |
  +-- plan_trip('Mo Chit (N8)', 'Siam (CEN)', 0800, [Mo Chit], 25, Itin)
       |
       +-- transit('Mo Chit (N8)', 'Saphan Khwai (N7)', bts_sukhumvit, 0700, 0702) ✓
       |   Arrive 0702 =< 0800 ✓
       |   'Saphan Khwai' not in Visited ✓
       |
       +-- plan_trip('Saphan Khwai (N7)', 'Siam (CEN)', 0800, [...], 24, RestLegs)
            |
            +-- transit('Saphan Khwai', 'Ari', bts_sukhumvit, 0703, 0705) ✓
            |   0702 =< 0703 ✓ (connection timing)
            |
            +-- plan_trip('Ari (N5)', 'Siam (CEN)', 0800, [...], 23, ...)
                 |
                 +-- ... (continues through Sanam Pao, Victory Monument,
                          Phaya Thai, Ratchathevi, until reaching Siam)
                          |
                          +-- transit('Ratchathevi (N1)', 'Siam (CEN)',
                                      bts_sukhumvit, 0717, 0721) ✓
                              Arrive 0721 =< 0800 ✓ BASE CASE SUCCEEDS
```

The complete itinerary is constructed bottom-up as the proof unwinds:
```prolog
[leg('Mo Chit (N8)', 'Saphan Khwai (N7)', bts_sukhumvit, 0700, 0702),
 leg('Saphan Khwai (N7)', 'Ari (N5)', bts_sukhumvit, 0703, 0705),
 leg('Ari (N5)', 'Sanam Pao (N4)', bts_sukhumvit, 0706, 0707),
 leg('Sanam Pao (N4)', 'Victory Monument (N3)', bts_sukhumvit, 0708, 0711),
 leg('Victory Monument (N3)', 'Phaya Thai (N2)', bts_sukhumvit, 0712, 0714),
 leg('Phaya Thai (N2)', 'Ratchathevi (N1)', bts_sukhumvit, 0715, 0716),
 leg('Ratchathevi (N1)', 'Siam (CEN)', bts_sukhumvit, 0717, 0721)]
```

### 5.4 Cycle Prevention and Depth Bounding

**Why cycle prevention is critical:**

Without cycle prevention, the inter-line transfer walks create infinite loops:
```
Asok (E4) → Sukhumvit (BL22) → Asok (E4) → Sukhumvit (BL22) → ...
```

The `Visited` list accumulates every station the itinerary passes through. Before adding a new intermediate station, Prolog checks `\+ member(Mid, Visited)`.

**Why depth bounding matters:**

Even with cycle prevention, the search space grows exponentially with the number of legs. The 25-leg cap (`MaxLegs`) ensures:
- Realistic itineraries (real trips rarely exceed 10-15 legs)
- Bounded computation time
- Combined with the 10-second timeout and 100-result limit on the Python side

---

## 6. Hybrid Prolog + Python Design

The system deliberately splits responsibilities:

| Responsibility | Technology | Reason |
|---|---|---|
| **Station/line/attraction facts** | Prolog | Declarative facts are Prolog's strength; easy to extend |
| **Fuzzy name matching** | Prolog | `sub_atom/5` and `downcase_atom/2` handle pattern matching concisely |
| **Match ranking & scoring** | Python | Numerical similarity scoring (SequenceMatcher) is more natural in Python |
| **Edit-distance fallback** | Python | Pure computation; no logical inference needed |
| **Route step grouping** | Prolog | Recursive list processing with `shared_line/3` inference |
| **Shortest-path routing** | Python (Dijkstra) | Imperative algorithm with mutable priority queue |
| **Time-constrained trip planning** | Prolog | Perfect fit for SLD resolution over timetable facts |
| **Explore area selection** | Python | Graph analysis + heuristic filtering |
| **Natural language understanding** | LLM (Gemini) | Intent extraction from free text |
| **Response formatting** | LLM (Gemini) | Natural language generation |

This hybrid approach plays to each technology's strengths:
- Prolog excels at **logical deduction over structured facts** (what lines serve a station? can I reach B from A by 8 AM?).
- Python excels at **algorithmic computation** (Dijkstra, similarity scoring, graph construction).
- The LLM excels at **natural language interfaces** (understanding "how do I get to the Grand Palace?" and generating human-friendly responses).

---

## 7. Data Flow Diagrams

### Route Finding Flow
```
User: "How to get from Chatuchak to Terminal 21?"
  |
  v
LLM: find_route(start="Chatuchak", end="Terminal 21")
  |
  v
Orchestrator._handle_find_route()
  |
  +---> _resolve_location("Chatuchak")
  |       |-> Prolog: resolve_location('Chatuchak', S)  --> no match
  |       |-> Prolog: match_station('Chatuchak', S, T)  --> [{station: 'Chatuchak Park (BL13)', type: substring}]
  |       |-> Python: _rank_candidates()                 --> 'Chatuchak Park (BL13)'
  |
  +---> _resolve_location("Terminal 21")
  |       |-> Prolog: resolve_location('Terminal 21', S) --> 'Asok (E4)' (via near_station)
  |
  +---> _find_and_format_route('Chatuchak Park (BL13)', 'Asok (E4)')
          |-> Prolog: get_all_edges()                    --> [(A,B,T), ...]
          |-> Python: _build_graph() + _dijkstra()       --> path + cost
          |-> Prolog: build_route_steps(path)            --> [ride(...), transfer(...), ride(...)]
          |
          v
        {type: "route", data: {from, to, total_time, steps}}
```

### Trip Planning Flow
```
User: "I need to get from Mo Chit to Asok by 8am"
  |
  v
LLM: plan_trip(origin="Mo Chit", destination="Asok", deadline="08:00")
  |
  v
Orchestrator._handle_plan_trip()
  |
  +---> _resolve_location("Mo Chit")  --> 'Mo Chit (N8)'
  +---> _resolve_location("Asok")     --> 'Asok (E4)'
  +---> _parse_time("08:00")          --> 800
  |
  +---> Prolog: plan_trip('Mo Chit (N8)', 'Asok (E4)', 800, Itinerary)
  |       |
  |       +-- SLD Resolution: tries transit facts recursively
  |       +-- Finds: Mo Chit → Saphan Khwai → Ari → ... → Siam → Chit Lom → ... → Asok
  |       +-- Checks timing at each step
  |       +-- format_itinerary converts to formatted_leg terms
  |
  +---> Python: deduplicate itineraries
  |
  +---> LLM: format_prolog_result() --> natural language response
          |
          v
        {type: "schedule", data: {origin, destination, deadline, itineraries}}
```

### Explore Planning Flow
```
User: "I want to explore Bangkok tonight, starting from Siam at 7pm until 2am"
  |
  v
LLM: plan_explore(origin="Siam", start_time="19:00", end_time="02:00")
  |
  v
Orchestrator._handle_plan_explore()
  |
  +---> _resolve_location("Siam")              --> 'Siam (CEN)'
  +---> Prolog: get_attractions_by_station()    --> {station: [attractions]}
  +---> Prolog: get_nightlife_venues()          --> {station: [{name, category}]}
  +---> Merge into unified POI map
  |
  +---> Prolog: get_all_edges()                 --> edge list
  +---> Python: _build_graph() + _dijkstra() for each POI station
  +---> Python: _select_explore_stops()         --> up to 4 diverse stops
  +---> Python: distribute arrival times across 19:00-02:00 window
  |
  +---> For each leg: _find_and_format_route()
  +---> Add last_train_note (past midnight)
  |
  +---> LLM: format_prolog_result()
          |
          v
        {type: "explore", data: {origin, stops, legs, start_time, end_time, last_train_note}}
```