# Sales Script: NavLogic Bangkok

> **Product**: NavLogic Bangkok -- AI-Powered Bangkok Transit Assistant
> **Audience**: Prospective customers, stakeholders, or investors evaluating the platform
> **Tone**: Confident, concrete, technically credible without being overwhelming

---

## Opening Hook (30 seconds)

Every year, over 25 million tourists visit Bangkok. Most of them face the same problem within their first hour: *How do I get from here to there on this transit system?*

Bangkok has three separate rail networks -- the BTS Skytrain, MRT underground, and Airport Rail Link -- each with their own maps, naming conventions, and transfer stations. Even locals get confused.

**NavLogic Bangkok solves this.** A user types a question in plain English -- "How do I get from my hotel near Lat Krabang to the Grand Palace?" -- and in under two seconds, they get a complete, step-by-step transit itinerary with real departure times, transfer instructions, and nearby attraction recommendations.

No app-switching. No map-reading. Just ask and go.

---

## The Problem (1 minute)

Let me paint the picture of what tourists and locals deal with today:

1. **Fragmented information**: BTS, MRT, and Airport Rail Link each have separate apps, separate maps, and separate fare systems. No single tool covers all three.

2. **Language barriers**: Station names are in Thai and English, with inconsistent romanization. "Asok" on BTS is connected to "Sukhumvit" on MRT -- but there's no obvious indication they're the same interchange unless you already know.

3. **Time-sensitive connections**: "Can I make it from Chatuchak to Hua Lamphong by 8 AM?" requires knowing exact schedules and transfer times. Google Maps gives driving directions; it doesn't reason about train connections.

4. **Discovery gap**: Tourists near Thong Lo don't know there are five rooftop bars within walking distance of the station. That information exists -- it's just locked away in blog posts and travel guides, not integrated into navigation.

---

## The Solution: What NavLogic Bangkok Does (2 minutes)

NavLogic Bangkok is a conversational transit assistant with three core capabilities:

### 1. Natural Language Route Finding

Users ask questions the way they'd ask a friend:

> "How do I get from Siam to Chatuchak?"

The system understands informal names, attraction names, and even typos. Type "Saim" and it resolves to "Siam." Type "Grand Palace" and it knows the nearest station is Sanam Chai. The response includes:

- Exact lines to take (BTS Sukhumvit, MRT Blue, etc.)
- Where to board, where to alight
- Where to transfer and how
- Estimated travel time in minutes

### 2. Schedule-Aware Trip Planning

This is where NavLogic goes beyond basic routing.

> "I need to get from Mo Chit to Hua Lamphong by 8 AM."

The system doesn't just find the shortest path -- it finds **specific departures** that satisfy the time constraint. It returns actual departure and arrival times for every leg:

- "Depart Mo Chit at 07:00, arrive Saphan Khwai at 07:02"
- "Depart Saphan Khwai at 07:03, arrive Ari at 07:05"
- ...all the way to the destination

It verifies that every connection is physically possible -- you can't board a train that departed before you arrived at the platform. And it finds multiple alternative itineraries so the user can choose.

### 3. Intelligent Day Planning & Exploration

> "I'm staying near Lat Krabang and have a free day. Plan something from 9 AM to 5 PM."

The system automatically:
- Discovers all attractions and points of interest reachable by transit
- Calculates optimal routes from the user's location
- Selects 3-4 diverse stops (not all clustered in one area)
- Spreads them across the time window with suggested arrival times
- Includes nearby attractions at each stop

This also works for nightlife:

> "Plan a night out starting from Asok at 7 PM until midnight."

It recommends rooftop bars, clubs, night markets, and entertainment districts reachable by train -- with a "last train" advisory when the time window extends past midnight.

---

## What Makes It Different: The Technical Edge (2 minutes)

This isn't just another chatbot wrapper. NavLogic Bangkok has a unique hybrid architecture that combines **three technologies**, each doing what it's best at:

### Logic Engine (Prolog)

At the core is a **Prolog-based reasoning engine** -- the same type of formal logic system used in expert systems and theorem provers. The Bangkok transit network is encoded as logical facts and rules:

- "Siam station is on the BTS Sukhumvit Line" -- a fact
- "A station is a transfer station if it serves two different lines" -- a rule
- "A valid trip exists if each leg's arrival time is before the next leg's departure" -- a constraint

When a user asks "Can I get from A to B by time T?", the system doesn't search a database -- it **proves** the itinerary is valid, the same way a mathematician proves a theorem. This gives us correctness guarantees that traditional search-based approaches can't match.

### Graph Algorithms (Python)

For fastest-path routing (where exact times don't matter), we use **Dijkstra's shortest-path algorithm** running in Python. This gives us O(E log V) performance across the entire network -- sub-millisecond route calculations for any station pair.

### Large Language Model (Google Gemini)

The LLM handles the **human interface layer** -- understanding natural language input and formatting results into conversational responses. Critically, **the LLM never performs routing or scheduling logic**. It extracts intent and formats output. All reasoning happens in the logic engine and algorithms.

This separation means:
- **No hallucinated routes**: The LLM can't invent a station or connection that doesn't exist in the knowledge base
- **Deterministic correctness**: Same question always produces the same route
- **Auditable logic**: Every result traces back to declared facts and provable rules

---

## Live Demo Walkthrough (2 minutes)

*[Open the application in browser]*

### Demo 1: Conversational Chat

Let me show you the main chat interface. I'll type: **"How do I get from Suvarnabhumi Airport to Siam?"**

Watch what happens:
1. The LLM extracts intent: this is a route-finding query
2. "Suvarnabhumi Airport" resolves to the Airport Rail Link station
3. "Siam" resolves to Siam (CEN)
4. Dijkstra computes the optimal path across multiple transit lines
5. Prolog builds the step-by-step ride and transfer instructions
6. The result renders with color-coded line badges and clear transfer points

The user sees a friendly natural-language response *and* a structured visual breakdown.

### Demo 2: Scheduled Trip

Now: **"I need to reach Asok from Mo Chit by 8 AM."**

This triggers the schedule planner. The system returns specific trains with exact times:
- Depart 07:00, arrive 07:31 via BTS Sukhumvit
- Alternative: Depart 07:30, arrive 08:01 via BTS Sukhumvit

Notice it found multiple options and verified each connection is temporally valid.

### Demo 3: Day Exploration

**"Plan a day trip from Lat Krabang, 9 AM to 5 PM."**

The system auto-discovers reachable attractions: Chatuchak Market, Siam shopping district, riverside attractions at Saphan Taksin. It spreads them across the day and gives transit directions between each stop.

### Demo 4: Station Explorer

The Explore page lets users browse all stations and attractions without asking questions -- filterable by line, searchable by name. Every attraction shows its nearest station.

---

## Engineering Quality & Reliability (1 minute)

This isn't a prototype. It's production-grade software:

- **169 automated tests** across 9 test suites covering:
  - Every Prolog query method
  - Every orchestrator dispatch path
  - All API endpoints (route, schedule, stations, attractions, auth, conversations)
  - JWT authentication and authorization
  - Database CRUD operations
  - Exhaustive route validation across all station pairs (path correctness + cost symmetry)

- **CI/CD pipeline** via GitHub Actions: every push and pull request runs the full test suite automatically. Front-end changes trigger ESLint + TypeScript checks.

- **Security**: JWT-based authentication, bcrypt password hashing, input validation at every API boundary.

- **Fuzzy input handling**: Three-tier name resolution -- exact match, prefix match, substring match via Prolog classification, then Python similarity ranking, with edit-distance fallback for typos. Users don't need to know exact station names.

---

## Architecture at a Glance (30 seconds)

```
User Question (natural language)
       |
  Google Gemini  --> extracts intent (function calling)
       |
  Orchestrator   --> resolves names, dispatches to handler
       |
  Prolog Engine  --> logical reasoning (schedules, facts, rules)
  + Dijkstra     --> shortest-path computation
       |
  Google Gemini  --> formats result into conversational response
       |
  React Frontend --> renders structured UI (route steps, schedules, plans)
```

**Back-end**: Python, FastAPI, SWI-Prolog (via pyswip), Google Gemini, SQLAlchemy, SQLite

**Front-end**: React 19, TypeScript, Vite, Tailwind CSS, Framer Motion

---

## Market Fit & Use Cases (1 minute)

### Who is this for?

| Segment | Use Case |
|---------|----------|
| **Hotels & hostels** | Embed as a concierge chatbot for guests ("How do I get to the mall?") |
| **Tourism platforms** | Integrate as a transit planning widget alongside booking flows |
| **Transit authorities** | White-label as an official trip planner for BTS/MRT/ARL |
| **Travel apps** | API integration for route and schedule data |
| **Corporate travel** | Help business travelers navigate unfamiliar transit systems |

### Why now?

- Bangkok's rail network is expanding rapidly (Gold Line, Orange Line, new MRT extensions) -- the need for a unified, intelligent navigator is growing
- LLM-powered interfaces have crossed the usability threshold -- users now expect to type questions, not fill forms
- The hybrid architecture (logic engine + LLM) is a proven pattern that avoids the reliability problems of pure-LLM approaches

---

## Competitive Advantages (30 seconds)

| Feature | NavLogic | Google Maps | Transit Apps |
|---------|----------|-------------|--------------|
| Natural language queries | Yes | Limited | No |
| Schedule-aware planning | Yes (proven correct) | Estimated only | Partial |
| Attraction discovery | Built-in | Separate search | No |
| Day/night planning | Automatic | Manual | No |
| Nightlife recommendations | Yes | No | No |
| Multi-line transfer logic | Formally verified | Heuristic | Varies |
| Typo-tolerant input | 3-tier fuzzy matching | Basic | Exact match |
| Conversational context | Multi-turn chat | No | No |

---

## Closing (30 seconds)

NavLogic Bangkok takes a problem that every Bangkok visitor faces -- navigating a complex, multi-system rail network -- and solves it with a simple conversation.

Behind that simple conversation is a formally grounded logic engine that guarantees correct results, a shortest-path algorithm that guarantees optimal routes, and an LLM interface that makes it all feel like talking to a knowledgeable local friend.

The code is tested, the architecture is clean, and the system is ready to scale to new cities, new transit lines, and new languages.

**The question isn't whether Bangkok needs a better transit assistant. It's whether you want to be the one providing it.**

---

## Appendix: Objection Handling

**"Why not just use Google Maps?"**
Google Maps doesn't reason about train schedules -- it estimates. NavLogic *proves* that connections are valid. It also integrates attraction discovery and day planning, which Maps doesn't do.

**"What happens when schedules change?"**
The schedule is a set of declarative facts in a Prolog file. Updating a departure time is changing one line. No code changes, no redeployment logic -- just update the fact.

**"Does it scale to other cities?"**
The architecture is city-agnostic. The Prolog knowledge base and schedule are the only Bangkok-specific components. Swap them out for Tokyo, Singapore, or London, and the reasoning engine, algorithms, and UI work unchanged.

**"What if the LLM hallucinates?"**
It can't hallucinate routes or schedules. The LLM only extracts user intent and formats results. All routing and scheduling logic runs in deterministic Prolog rules and Python algorithms. The LLM never invents data.

**"Is Prolog a niche/outdated technology?"**
Prolog is the industry standard for formal reasoning, used in IBM Watson, airline scheduling systems, and expert systems worldwide. SWI-Prolog (our runtime) is actively maintained and powers production systems globally. We use it because it's the right tool for logical inference -- not because it's trendy.
