# NavLogic - Bangkok

A Bangkok public transit assistant that combines **Prolog-based logical reasoning** with **LLM intent extraction** (Google Gemini) to answer natural language queries about routes, schedules, and attractions across Bangkok's rail network (BTS, MRT, Airport Rail Link).

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
| `POST` | `/query` | Yes | Natural language query (LLM-powered chat) |
| `GET` | `/route?start=...&end=...` | No | Direct route finding |
| `GET` | `/schedule?origin=...&destination=...&deadline=...` | No | Direct schedule query |
| `GET` | `/stations` | No | List all stations with their lines |
| `GET` | `/attractions` | No | List all attractions with nearest stations |
| `POST` | `/auth/register` | No | Register a new user |
| `POST` | `/auth/login` | No | Login and receive JWT token |
| `GET` | `/conversations` | Yes | List user's conversations |
| `POST` | `/conversations` | Yes | Create a new conversation |
| `GET` | `/conversations/{id}` | Yes | Get conversation with messages |
| `DELETE` | `/conversations/{id}` | Yes | Delete a conversation |

## Testing

```sh
cd back-end
pytest                                    # Run all tests
pytest tests/test_exhaustive_routes.py    # Exhaustive route pairs only
pytest tests/test_api.py -k test_name     # Run a single test by name
pytest --cov                              # Run with coverage
```

Tests mock the LLM and use an in-memory SQLite database. No API key or SWI-Prolog running service is needed for tests that don't touch Prolog (auth, CRUD, JWT tests), but SWI-Prolog must be installed for route/schedule tests.

CI runs automatically on push/PR to main via GitHub Actions (`.github/workflows/python_tests.yml`).

## Architecture

```
back-end/
├── app.py                    # FastAPI application setup & router wiring
├── api/routes/               # API route handlers
├── auth/                     # JWT auth, password hashing
├── db/                       # SQLAlchemy models, CRUD, database config
├── engine/
│   ├── orchestrator.py       # Central dispatcher + Dijkstra + name resolution
│   ├── prolog.py             # pyswip wrapper for all Prolog queries
│   ├── knowledge_base.pl     # Prolog facts: stations, lines, edges, attractions
│   ├── rules.pl              # Prolog rules: route steps, transfers, fuzzy matching
│   ├── schedule.pl           # Prolog timetable facts + trip planning via resolution
│   └── llm/
│       ├── llm.py            # Gemini client (intent extraction + result formatting)
│       ├── tools.py          # Function declarations for Gemini function calling
│       └── system_prompt.txt # LLM system prompt
└── tests/                    # pytest test suite

front-end/
├── src/
│   ├── App.tsx               # Router, layout, auth/theme providers
│   ├── api/client.ts         # API client functions
│   ├── components/           # UI components (route steps, search, badges)
│   ├── context/              # Auth and theme context providers
│   ├── pages/                # Home (chat), Route, Explore, Login, Register
│   ├── types/                # TypeScript type definitions
│   └── utils/                # Line color mappings
└── vite.config.ts            # Vite config with API proxy to back-end
```

### Key Design Decisions

- **Prolog for domain logic, Python for orchestration**: Station relationships, line membership, transfer detection, and schedule planning are expressed as Prolog facts and rules. Python handles routing (Dijkstra), fuzzy name resolution ranking, and HTTP serving.
- **Hybrid name resolution**: Prolog classifies candidates (exact/prefix/substring match), Python ranks them by similarity score, with edit-distance fallback for typos.
- **LLM as interface layer only**: Gemini extracts structured function calls from user text and formats results back to natural language. It never performs routing or schedule logic.
- **Structured response types**: The API returns typed responses (`route`, `schedule`, `day_plan`, `nightlife`, `answer`, `error`) so the front-end can render specialized UI components for each.

## Tech Stack

**Back-end**: Python, FastAPI, pyswip (SWI-Prolog), Google Gemini API, SQLAlchemy, SQLite, python-jose (JWT), bcrypt

**Front-end**: React 19, TypeScript, Vite, Tailwind CSS, React Router, Framer Motion, React Markdown
