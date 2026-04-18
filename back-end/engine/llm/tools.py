"""
tools.py — Gemini function declaration.

Exactly ONE function: plan(origin, goal). The `goal` is a recursive logical
form (and/or/not/any_tag/all_tag/none_tag/prefer_tag/route_to). The schema
below types `goal` as a plain object — Gemini's function-calling schema
does not support recursive $ref, so the operator grammar is taught
concretely in the system prompt instead. The orchestrator validates the
shape via PrologInterface._goal_to_prolog before sending it to Prolog.

This is the open-vocabulary contract: tag literals are free strings, the
LLM is given the active vocabulary at call time but is allowed to emit
anything, and the rulebook surfaces unbound tags as unknown(_) rather
than silently dropping them.
"""

PLAN_FUNCTION = {
    "name": "plan",
    "description": (
        "Plan a transit-aware trip in Bangkok. `goal` is a recursive logical "
        "form built from these operators: and, or, not, any_tag, all_tag, "
        "none_tag, prefer_tag, route_to. Use {\"route_to\": \"<station>\"} "
        "alone for simple A-to-B routing with no theme constraints. "
        "See system instructions for the full grammar and examples."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "origin": {
                "type": "string",
                "description": (
                    "The starting location as the user said it. Can be a station "
                    "name ('Asok', 'Mo Chit') or a POI name ('Grand Palace'). "
                    "Do not append station codes — the engine resolves names."
                ),
            },
            "goal": {
                "type": "object",
                "description": (
                    "A recursive logical-form goal. Always a single-key object "
                    "whose key is one of the operators. Examples:\n"
                    "  Pure routing: {\"route_to\": \"Siam\"}\n"
                    "  See temples but avoid heat: {\"and\": ["
                    "{\"any_tag\": [\"temple\"]}, "
                    "{\"none_tag\": [\"weather_exposed\"]}]}\n"
                    "  Indoor + budget, prefer museum: {\"and\": ["
                    "{\"all_tag\": [\"indoor\", \"budget_friendly\"]}, "
                    "{\"prefer_tag\": [\"museum\"]}]}\n"
                    "Tag literals are free strings — the engine resolves "
                    "synonyms via the ontology and reports any unknown tag back."
                ),
            },
            "time_context": {
                "type": "object",
                "description": (
                    "Optional per-query time frame. Emit when the user "
                    "references a time (\"tonight\", \"this Saturday\", "
                    "\"at 10 AM\", \"after sunset\"); omit otherwise and the "
                    "engine will default to the current Bangkok wall-clock "
                    "injected into your system prompt. Time-gated POI tags "
                    "(e.g. Jodd Fairs is only `high_density` after sunset; "
                    "Chatuchak is only `high_density` on weekends) fire or "
                    "fail based on this frame — so emit it whenever the "
                    "user pins a time."
                ),
                "properties": {
                    "weekday": {
                        "type": "string",
                        "description": (
                            "Three-letter lowercase day: mon, tue, wed, thu, "
                            "fri, sat, sun. Full English names also accepted."
                        ),
                    },
                    "hour": {
                        "type": "integer",
                        "description": "Hour of day in [0, 23].",
                    },
                    "minute": {
                        "type": "integer",
                        "description": "Minute of hour in [0, 59].",
                    },
                },
            },
            "budget_context": {
                "type": "object",
                "description": (
                    "Optional per-query fare ceiling in Thai Baht. Emit "
                    "whenever the user mentions money (\"I have 500 baht\", "
                    "\"under 100 THB\", \"cheap trip\"). Absent means the "
                    "engine does no fare reasoning. When present, the "
                    "orchestrator runs a symbolic-repair loop: Prolog "
                    "diagnoses why a path busts the budget, synthesises a "
                    "boundary-avoidance constraint, and re-runs Dijkstra on "
                    "the pruned graph. Surface the resulting fare_breakdown "
                    "and repair_trail to the user."
                ),
                "properties": {
                    "max_thb": {
                        "type": "integer",
                        "description": (
                            "Maximum total one-way fare in THB across all "
                            "agency journeys. Positive integer."
                        ),
                    },
                },
            },
            "explore": {
                "type": "boolean",
                "description": (
                    "Set true when the user asks \"where can I go?\" / "
                    "\"what can I travel to?\" / \"show me places\" — any "
                    "question about the REACHABLE SET rather than a single "
                    "pick. When true, the engine skips single-answer "
                    "selection and returns every matching POI as an "
                    "annotated alternative. Default false (a single "
                    "chosen plan)."
                ),
            },
        },
        "required": ["origin", "goal"],
    },
}

FUNCTION_DECLARATIONS = [PLAN_FUNCTION]
