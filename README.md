# NavLogic - Bangkok

A Bangkok public transit assistant built on an **open-vocabulary neuro-symbolic loop**. A Prolog ontology + knowledge base owns the rulebook (stations, lines, edges, POIs, tags, synonyms, subsumption, per-agency fares); **Google Gemini** translates free-form user input into structured Prolog goals and narrates the result; the orchestrator runs **candidate generation → relaxation → Dijkstra → audit / replan**. All reasoning is symbolic — the LLM never routes.

Two feedback loops anchor the engine:

- **Audit loop** (`audit_route/3` + `_select_via_audit`) — Prolog rejects a candidate POI whose route violates a hard constraint; Python blacklists that POI and replans.
- **Repair loop** (`diagnose_budget/3` + `propose_repair/3` + `_budget_repair`) — Prolog diagnoses why a path busts the user's THB budget, synthesises a structured pruning constraint (`avoid_specific_boundary` → `avoid_agency_pair` → `force_single_agency` → `infeasible`), and Python re-runs Dijkstra on the pruned graph. When no repair succeeds, Prolog emits a **constructive infeasibility certificate** rather than a silent "no".

## Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **SWI-Prolog** (required by pyswip)
  - macOS: `brew install swi-prolog`
  - Ubuntu: `sudo apt-get install swi-prolog`
- **Gemini API Key** for Gemini LLM features (If you don't have a key, get it [here](https://aistudio.google.com/api-keys))

## Getting Started

### Back-end

```sh
cd back-end
pip install -r requirements.txt
```

Create a `.env` file in `back-end/` with your Google API key:

```
GOOGLE_API_KEY=your_key_here
```

Start the development server:

```sh
uvicorn app:app --reload
```

The API runs at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### Front-end

```sh
cd front-end
npm install
npm run dev
```

The Vite dev server starts at `http://localhost:5173` and proxies `/api` requests to the back-end at `http://localhost:8000`.

## API Endpoints

All endpoints are prefixed with `/api`.

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/query` | Yes | Natural-language chat (runs the neuro-symbolic loop) |
| `GET` | `/route?start=...&end=...` | No | Pure routing (Dijkstra, no LLM) |
| `GET` | `/stations` | No | List stations with their lines |
| `GET` | `/attractions` | No | List POIs with tags and nearest station |
| `POST` | `/auth/register` | No | Register a new user |
| `POST` | `/auth/login` | No | Login and receive JWT token |
| `POST` | `/auth/refresh` | No | Refresh a JWT token |
| `GET` | `/conversations` | Yes | List user's conversations |
| `POST` | `/conversations` | Yes | Create a new conversation |
| `GET` | `/conversations/{id}` | Yes | Get conversation with messages |
| `DELETE` | `/conversations/{id}` | Yes | Delete a conversation |

### `/api/query` response shape

```jsonc
{
  "type": "plan" | "answer" | "error",
  "data": {
    // PlanData (type === "plan"):
    "origin": "Asok",
    "destination": "Siam",
    "poi": "Jim Thompson House",           // optional
    "total_time": 14,                      // minutes, optional
    "total_fare": 47,                      // THB, optional — set when budget_context is present
    "steps": [ /* ride / transfer steps */ ],
    "fare_breakdown": [                    // optional — per-agency segments from the repair layer
      {"agency": "bts", "from": "Asok (E4)", "to": "Siam (CEN)", "fare": 25}
    ],
    "preference_score": 2,                 // optional
    "relaxation_note": ["weather_exposed"],  // optional — dropped tag conjuncts
    "audit_trail": [ /* rejected candidates + reasons */ ],
    "repair_trail": [                      // optional — symbolic repair steps that shaped this path
      {"diagnosis": {"kind": "over_budget", "total": 65, "overage": 15, "boundaries": [...]},
       "repair_applied": {"kind": "avoid_specific_boundary", "a": "Asok (E4)", "b": "Sukhumvit (BL22)"}}
    ],
    "budget_context": {"max_thb": 50},     // optional — echoes the query's fiscal ceiling
    "budget_audit": [                      // optional — infeasibility certificates per rejected candidate
      {"candidate": "Wat Pho", "certificate": {"repairs_exhausted": [...], "final_over_by": 20, "min_seen": 70}}
    ],
    "alternatives": ["Wat Pho", "Erawan Shrine"],  // optional — in explore mode, each carries its own repair_trail / fare_breakdown
    "explore": true,                       // optional — true when the user asked "where can I go?"
    "unknown_tags": ["aesthetic"],         // optional — surfaced to the user
    "answer": "Take BTS Sukhumvit from Asok..."    // LLM narration
  }
}
```

Every field after `steps` exposes a distinct layer of the symbolic reasoner — relaxation, audit, symbolic repair, and unknown-tag handling are all visible to the front-end. `repair_trail` narrates the diagnose→propose→prune→replan chain; `budget_audit` carries the infeasibility certificates Prolog emits when no repair succeeds.

## Testing

```sh
cd back-end
pytest                                                             # All 262 tests
pytest tests/test_ontology.py tests/test_relaxation.py tests/test_audit_loop.py  # Neuro-symbolic features
pytest tests/test_exhaustive_routes.py                             # All-pairs Dijkstra
pytest tests/test_api.py -k test_name                              # Run a single test by name
pytest --cov                                                       # Run with coverage
```

### Regenerating fare facts

`back-end/engine/fares.pl` is machine-generated from `back-end/engine/electric_train_fares.csv`. After the CSV changes, rebuild the Prolog facts:

```sh
python scripts/build_fares.py
```

The preprocessor normalises station names against the KB atom map, derives agency from `agency_id` (BTSC→`bts`, BEM→`bem`, SRTET→`srtet`; MRTA rows are dropped pending KB expansion), and writes `fare(Agency, StationA, StationB, PriceTHB)` facts. The emitted file carries a provenance header with row-drop counts; regeneration is idempotent.

Tests stub the LLM via `StubLLM` and use an in-memory SQLite database. SWI-Prolog must be installed for engine tests; auth / CRUD / JWT tests need neither Prolog nor an API key.

CI runs automatically on push/PR to main via GitHub Actions (`.github/workflows/python_tests.yml`, `.github/workflows/frontend_checks.yml`).

## Architecture

```
scripts/
└── build_fares.py            # CSV → fares.pl preprocessor (per-agency fare facts, idempotent)

back-end/
├── app.py                    # FastAPI setup & router wiring
├── api/
│   ├── routes/               # query, route, stations, auth, conversations
│   └── schemas.py            # PlanData (incl. BudgetContext, FareSegment, RepairStep, BudgetAuditEntry, ExploreAlternative), PlanResponse, QueryResult union, auth/conversation models
├── auth/                     # JWT auth, password hashing
├── db/                       # SQLAlchemy models, CRUD, database config
├── engine/
│   ├── orchestrator.py       # handle() entry, _handle_plan pipeline, _select_via_audit, _budget_repair, _dijkstra
│   ├── prolog.py             # pyswip wrapper: candidates, relax, audit_route_for_path, trip_fare, diagnose_budget, propose_repair, vocab/synonyms
│   ├── ontology.pl           # bind_tag/2, is_a/2 subsumption, synonym/2, active_tag_vocabulary/1
│   ├── knowledge_base.pl     # station/2, edge/4, poi/3, tagged/2, transfers (consults fares.pl)
│   ├── rules.pl              # §1 route steps · §2 classified station matching · §3 line display names · §4 fiscal reasoning · §5 symbolic repair
│   ├── fares.pl              # auto-generated per-agency fare/4 facts (regenerated via scripts/build_fares.py)
│   └── llm/
│       ├── llm.py            # Gemini client (translate_to_query + format_result)
│       ├── tools.py          # plan function declaration for Gemini function calling (origin, goal, time_context, budget_context, explore)
│       └── system_prompt.txt # LLM system prompt (vocab + synonyms injected at runtime)
└── tests/                    # 262 pytest tests (incl. test_ontology, test_relaxation, test_audit_loop)

front-end/
├── src/
│   ├── App.tsx               # Router, layout, auth/theme providers
│   ├── api/client.ts         # API client (typed against {plan|answer|error})
│   ├── components/
│   │   ├── PlanResult.tsx    # Renders the full neuro-symbolic loop: time/budget badges, relaxation, unknown-tags, LLM answer, FareBreakdown, RepairTrailDisclosure, RouteSteps, AuditTrailDisclosure, BudgetAuditDisclosure, ExploreAlternativesList/AlternativesList
│   │   ├── RouteSteps.tsx    # Ride + transfer step list
│   │   ├── LineBadge.tsx     # Line chip
│   │   ├── SearchBar.tsx     # Explore search
│   │   └── Sidebar.tsx       # Conversation list
│   ├── context/              # Auth and theme context providers
│   ├── pages/                # Home (chat), Route, Explore, Login, Register
│   ├── types/                # PlanData + QueryResponse union; BudgetContext, FareSegment, Diagnosis/Repair discriminated unions, RepairStep, InfeasibilityCertificate, BudgetAuditEntry, ExploreAlternative
│   └── utils/                # Line color mappings
└── vite.config.ts            # Vite config with API proxy to back-end
```

### Key design decisions

- **Prolog owns the rulebook.** `ontology.pl` holds the open-vocabulary backbone — `bind_tag/2` with cut semantics, `is_a/2` subsumption, `synonym/2`, and the `active_tag_vocabulary/1` / `active_synonyms/1` exports that the LLM sees. Any new tag, synonym, or subsumption edge goes in Prolog, never in Python.
- **Constraint relaxation is symbolic.** When candidate generation returns empty, `PrologInterface.relax` drops the minimal set of conjuncts — single-conjunct first, then two-conjunct — and re-runs. The dropped conjuncts surface as `relaxation_note` so the user sees exactly which constraint gave way.
- **Routes are audited.** After Dijkstra picks a path, `audit_route_for_path` checks it against constraints the graph can't encode (e.g. `weather_exposed` transfers). Violating candidates are blacklisted and the loop retries, bounded by `MAX_REPLAN`. The full trail surfaces as `audit_trail`.
- **Fiscal reasoning is symbolic repair, not a post-filter.** When the user pins a THB budget, Prolog partitions the path by agency (`path_segments/2`), looks up each segment's fare (`fare/4` facts), and either confirms `within_budget` or produces a structured `over_budget(Total, Overage, Segments, Boundaries)` diagnosis. `propose_repair/3` synthesises a new ground constraint at runtime — `avoid_specific_boundary` → `avoid_agency_pair` → `force_single_agency` → `infeasible` — and Python's `_build_graph_with_pruning` applies it as an edge removal before re-running Dijkstra. When the tier cascade exhausts, `explain_infeasibility/3` emits a **constructive certificate** (`repairs_exhausted` + `final_over_by` + `min_seen`) that reaches the user as `budget_audit`. This is the sibling of the audit loop: audit blacklists a POI, repair blacklists an edge or agency crossing.
- **The LLM is a translator, not a reasoner.** `translate_to_query` produces a structured Prolog goal via Gemini function calling; `format_result` narrates the structured result. Routing, relaxation, audit, fare diagnosis, repair synthesis, and name resolution happen in Python + Prolog. The LLM sees the current tag vocabulary and synonym list injected into its system prompt.
- **Hybrid name resolution.** Prolog classifies candidates (exact / prefix / substring match); Python ranks them by similarity; edit-distance fallback handles typos. Unknown tags are wrapped as `unknown/1` by the `bind_tag` cut and surfaced via `unknown_tags` rather than dropped silently.
- **One unified response schema.** `/api/query` always returns `{type, data}` where `type ∈ {"plan", "answer", "error"}`. `PlanData` is the single surface for everything the reasoner produces — adding a new signal means extending `PlanData`, not creating a new response type.

## Tech Stack

**Back-end**: Python, FastAPI, pyswip (SWI-Prolog), Google Gemini API, SQLAlchemy, SQLite, python-jose (JWT), bcrypt

**Front-end**: React 19, TypeScript, Vite, Tailwind CSS, React Router, Framer Motion, React Markdown
