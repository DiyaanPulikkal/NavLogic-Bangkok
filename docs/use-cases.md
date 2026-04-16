# NavLogic Bangkok — Use Case Specification

## Actors

**Primary**
- **Guest User** — unauthenticated visitor
- **Registered User** — authenticated visitor (extends Guest)

**Secondary (external systems)**
- **Gemini LLM** — translates natural-language input into structured goals and narrates results
- **Prolog Engine** — performs symbolic reasoning (candidates, relaxation, audit)

---

## Use Cases

### 1. Authentication (Guest)
| ID | Use Case | Description |
|----|----------|-------------|
| UC-1 | Register Account | Guest creates an account with email + password (`POST /api/auth/register`). |
| UC-2 | Log In | Guest authenticates and receives access + refresh JWT (`POST /api/auth/login`). |
| UC-3 | Refresh Token | Registered User exchanges refresh token for a new access token (`POST /api/auth/refresh`). |

### 2. Direct Route Planning (Guest)
| ID | Use Case | Description |
|----|----------|-------------|
| UC-4 | Find Route Between Two Stations | Guest enters origin + destination; system returns Dijkstra path with ride/transfer steps (`GET /api/route`). |
| UC-5 | Browse Stations | Guest views all stations with their lines (`GET /api/stations`). |
| UC-6 | Browse Attractions | Guest views all POIs with their tags and nearest station (`GET /api/attractions`). |

### 3. Conversational Trip Planning (Registered User)
| ID | Use Case | Description |
|----|----------|-------------|
| UC-7 | Send Chat Query | User sends free-form natural-language request (e.g. *"night market that's not crowded from Siam"*); system runs the neuro-symbolic loop and returns a plan (`POST /api/query`). |
| UC-8 | Receive Reasoned Plan | System surfaces the chosen POI, route, time-context badge, and `answer` narration. |
| UC-9 | View Relaxation Notes | When no candidate satisfies the full goal, the system drops the minimal set of conjuncts and tells the user *what was relaxed* (e.g. "dropped: night_market"). |
| UC-10 | View Audit Trail | When candidates are rejected by route-level constraints (e.g. weather-exposed transfer), the system shows which alternatives were skipped and why. |
| UC-11 | View Alternatives | System lists other matching POIs the user might also consider. |
| UC-12 | Resolve Unknown Terms | When the user uses vocabulary the engine doesn't know, the system asks for clarification with sample known tags. |

### 4. Conversation Management (Registered User)
| ID | Use Case | Description |
|----|----------|-------------|
| UC-13 | Create Conversation | User starts a new conversation thread. |
| UC-14 | List Conversations | User views their conversation history. |
| UC-15 | Rename Conversation | User updates a conversation title. |
| UC-16 | Delete Conversation | User removes a conversation and its messages. |
| UC-17 | View Message History | User retrieves messages in a conversation, including stored `response_data` for replay of plans. |

---

## Relationships (for the diagram)

- **`<<include>>`**
  - UC-7 *Send Chat Query* **includes** *Translate Input* (Gemini LLM) and *Resolve Goal* (Prolog Engine).
  - UC-7 **includes** UC-4 *Find Route* internally (Dijkstra runs on the chosen POI's station).
  - UC-13–17 **include** *Authenticate Request* (JWT check).

- **`<<extend>>`**
  - UC-9 *View Relaxation Notes* **extends** UC-7 (only when constraints had to be relaxed).
  - UC-10 *View Audit Trail* **extends** UC-7 (only when candidates were rejected).
  - UC-12 *Resolve Unknown Terms* **extends** UC-7 (only when the goal contained unknown vocabulary).

- **Generalization**: *Registered User* inherits all *Guest User* use cases.

---

## Suggested layout for the diagram

```
                  ┌──────────────────────────────────────┐
                  │         NavLogic Bangkok             │
                  │                                      │
  Guest ──────────┼─→ UC-1 Register                      │
                  ├─→ UC-2 Log In                        │
                  ├─→ UC-4 Find Route ──────────┐        │
                  ├─→ UC-5 Browse Stations      │        │
                  └─→ UC-6 Browse Attractions   │        │
                                                ▼        │
                  ┌─→ UC-3 Refresh Token        │        │
                  ├─→ UC-7 Send Chat Query ─include→ UC-4│ ──→ Prolog Engine
                  │     │  «include» «extend»            │ ──→ Gemini LLM
                  │     ├─ UC-8 Receive Plan             │
                  │     ├─ UC-9 Relaxation Notes (ext)   │
                  │     ├─ UC-10 Audit Trail (ext)       │
                  │     ├─ UC-11 Alternatives            │
   Registered ────┤     └─ UC-12 Unknown Terms (ext)     │
   User           ├─→ UC-13 Create Conversation          │
   (extends Guest)├─→ UC-14 List Conversations           │
                  ├─→ UC-15 Rename Conversation          │
                  ├─→ UC-16 Delete Conversation          │
                  └─→ UC-17 View Message History         │
                  └──────────────────────────────────────┘
```
