# NavLogic - Bangkok

A Bangkok public transit assistant built on an **open-vocabulary neuro-symbolic loop**. A Prolog ontology + knowledge base owns the rulebook (stations, lines, edges, POIs, tags, synonyms, subsumption); **Google Gemini** translates free-form user input into structured Prolog goals and narrates the result; the orchestrator runs **candidate generation → relaxation → Dijkstra → audit / replan**. All reasoning is symbolic — the LLM never routes.

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
    "steps": [ /* ride / transfer steps */ ],
    "preference_score": 2,                 // optional
    "relaxation_note": ["weather_exposed"], // optional — dropped conjuncts
    "audit_trail": [ /* rejected candidates + reasons */ ],
    "alternatives": ["Wat Pho", "Erawan Shrine"], // optional
    "unknown_tags": ["aesthetic"],         // optional — surfaced to the user
    "answer": "Take BTS Sukhumvit from Asok..."   // LLM narration
  }
}
```

Every field after `steps` exposes a distinct layer of the symbolic reasoner — relaxation, audit, and unknown-tag handling are all visible to the front-end.

## Testing

```sh
cd back-end
pytest                                                             # All tests
pytest tests/test_ontology.py tests/test_relaxation.py tests/test_audit_loop.py  # Neuro-symbolic features
pytest tests/test_exhaustive_routes.py                             # All-pairs Dijkstra
pytest tests/test_api.py -k test_name                              # Run a single test by name
pytest --cov                                                       # Run with coverage
```

Tests stub the LLM via `StubLLM` and use an in-memory SQLite database. SWI-Prolog must be installed for engine tests; auth / CRUD / JWT tests need neither Prolog nor an API key.

CI runs automatically on push/PR to main via GitHub Actions (`.github/workflows/python_tests.yml`, `.github/workflows/frontend_checks.yml`).

## Architecture

```
back-end/
├── app.py                    # FastAPI setup & router wiring
├── api/
│   ├── routes/               # query, route, stations, auth, conversations
│   └── schemas.py            # PlanData, PlanResponse, QueryResult union, auth/conversation models
├── auth/                     # JWT auth, password hashing
├── db/                       # SQLAlchemy models, CRUD, database config
├── engine/
│   ├── orchestrator.py       # handle() entry, _handle_plan pipeline, _select_via_audit, _dijkstra
│   ├── prolog.py             # pyswip wrapper: candidates, relax, audit_route_for_path, vocab/synonyms
│   ├── ontology.pl           # bind_tag/2, is_a/2 subsumption, synonym/2, active_tag_vocabulary/1
│   ├── knowledge_base.pl     # station/2, edge/4, poi/3, tagged/2, transfers
│   ├── rules.pl              # route steps, classified station matching, line display names
│   └── llm/
│       ├── llm.py            # Gemini client (translate_to_query + format_result)
│       ├── tools.py          # plan function declaration for Gemini function calling
│       └── system_prompt.txt # LLM system prompt (vocab + synonyms injected at runtime)
└── tests/                    # 219 pytest tests (incl. test_ontology, test_relaxation, test_audit_loop)

front-end/
├── src/
│   ├── App.tsx               # Router, layout, auth/theme providers
│   ├── api/client.ts         # API client (typed against {plan|answer|error})
│   ├── components/
│   │   ├── PlanResult.tsx    # Renders the full neuro-symbolic loop (header, relaxation, audit, alternatives, unknown tags, route, answer)
│   │   ├── RouteSteps.tsx    # Ride + transfer step list
│   │   ├── LineBadge.tsx     # Line chip
│   │   ├── SearchBar.tsx     # Explore search
│   │   └── Sidebar.tsx       # Conversation list
│   ├── context/              # Auth and theme context providers
│   ├── pages/                # Home (chat), Route, Explore, Login, Register
│   ├── types/                # PlanData + QueryResponse = PlanResponse | AnswerResponse | ErrorResponse
│   └── utils/                # Line color mappings
└── vite.config.ts            # Vite config with API proxy to back-end
```

### Key design decisions

- **Prolog owns the rulebook.** `ontology.pl` holds the open-vocabulary backbone — `bind_tag/2` with cut semantics, `is_a/2` subsumption, `synonym/2`, and the `active_tag_vocabulary/1` / `active_synonyms/1` exports that the LLM sees. Any new tag, synonym, or subsumption edge goes in Prolog, never in Python.
- **Constraint relaxation is symbolic.** When candidate generation returns empty, `PrologInterface.relax` drops the minimal set of conjuncts — single-conjunct first, then two-conjunct — and re-runs. The dropped conjuncts surface as `relaxation_note` so the user sees exactly which constraint gave way.
- **Routes are audited.** After Dijkstra picks a path, `audit_route_for_path` checks it against constraints the graph can't encode (e.g. `weather_exposed` transfers). Violating candidates are blacklisted and the loop retries, bounded by `MAX_REPLAN`. The full trail surfaces as `audit_trail`.
- **The LLM is a translator, not a reasoner.** `translate_to_query` produces a structured Prolog goal via Gemini function calling; `format_result` narrates the structured result. Routing, relaxation, audit, and name resolution happen in Python + Prolog. The LLM sees the current tag vocabulary and synonym list injected into its system prompt.
- **Hybrid name resolution.** Prolog classifies candidates (exact / prefix / substring match); Python ranks them by similarity; edit-distance fallback handles typos. Unknown tags are wrapped as `unknown/1` by the `bind_tag` cut and surfaced via `unknown_tags` rather than dropped silently.
- **One unified response schema.** `/api/query` always returns `{type, data}` where `type ∈ {"plan", "answer", "error"}`. `PlanData` is the single surface for everything the reasoner produces — adding a new signal means extending `PlanData`, not creating a new response type.

## Tech Stack

**Back-end**: Python, FastAPI, pyswip (SWI-Prolog), Google Gemini API, SQLAlchemy, SQLite, python-jose (JWT), bcrypt

**Front-end**: React 19, TypeScript, Vite, Tailwind CSS, React Router, Framer Motion, React Markdown
