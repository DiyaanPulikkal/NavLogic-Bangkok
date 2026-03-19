# Function Declarations for LLM

find_route = {
    "name": "find_route",
    "description": (
        "Find the best route between two locations in Bangkok's public transit network. "
        "Use this when the user wants to travel from one place to another. "
        "Locations can be station names, partial names, or attraction names — "
        "they will be resolved automatically."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "start": {
                "type": "string",
                "description": "The starting location as the user said it (e.g. 'Siam', 'Grand Palace', 'Mo Chit')."
            },
            "end": {
                "type": "string",
                "description": "The destination as the user said it (e.g. 'Asok', 'Terminal 21', 'Chatuchak')."
            }
        },
        "required": ["start", "end"]
    }
}

line_of = {
    "name": "line_of",
    "description": (
        "Find which transit line(s) a station belongs to. "
        "Use this when the user asks which line serves a given station."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "station_name": {
                "type": "string",
                "description": "The station name as the user said it (e.g. 'Asok', 'Mo Chit'). No need for exact codes."
            }
        },
        "required": ["station_name"]
    }
}

same_line = {
    "name": "same_line",
    "description": (
        "Check whether two stations are served by at least one common transit line. "
        "Use this when the user asks if two stations are on the same line."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "station_a": {
                "type": "string",
                "description": "The first station name as the user said it."
            },
            "station_b": {
                "type": "string",
                "description": "The second station name as the user said it."
            }
        },
        "required": ["station_a", "station_b"]
    }
}

is_transfer_station = {
    "name": "is_transfer_station",
    "description": (
        "Check whether a station is an interchange (serves more than one transit line). "
        "Use this when the user asks if a station is a transfer or interchange station."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "station_name": {
                "type": "string",
                "description": "The station name as the user said it (e.g. 'Siam', 'Bang Wa')."
            }
        },
        "required": ["station_name"]
    }
}

needs_transfer = {
    "name": "needs_transfer",
    "description": (
        "Check whether travelling between two stations requires a line change. "
        "Use this when the user asks if they need to transfer to get from one station to another."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "station_a": {
                "type": "string",
                "description": "The starting station name as the user said it."
            },
            "station_b": {
                "type": "string",
                "description": "The destination station name as the user said it."
            }
        },
        "required": ["station_a", "station_b"]
    }
}

attraction_near_station = {
    "name": "attraction_near_station",
    "description": (
        "Find the nearest transit station to a named attraction. "
        "Use this when the user asks which station is closest to a landmark or attraction."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "attraction_name": {
                "type": "string",
                "description": "The attraction name as the user said it (e.g. 'Grand Palace', 'Chatuchak Weekend Market')."
            }
        },
        "required": ["attraction_name"]
    }
}

plan_trip = {
    "name": "plan_trip",
    "description": (
        "Plan a time-constrained trip using the transit schedule. "
        "Use this when the user wants to arrive somewhere by a specific time, "
        "asks about departure/arrival times, or wants a scheduled itinerary. "
        "This uses the timetable to find valid connections."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "origin": {
                "type": "string",
                "description": "The starting station name as the user said it (e.g. 'Mo Chit', 'Siam')."
            },
            "destination": {
                "type": "string",
                "description": "The destination station name as the user said it (e.g. 'Asok', 'Hua Lamphong')."
            },
            "deadline": {
                "type": "string",
                "description": (
                    "The latest acceptable arrival time in HH:MM 24-hour format "
                    "(e.g. '08:00', '09:30'). If the user doesn't specify, use '09:00' as default."
                )
            }
        },
        "required": ["origin", "destination", "deadline"]
    }
}

plan_day = {
    "name": "plan_day",
    "description": (
        "Plan a day trip with multiple stops, time constraints, and attraction recommendations. "
        "Use this when the user wants to visit multiple places in one day, has free time between stops, "
        "or asks what to do/visit between two destinations. "
        "This combines scheduled trip planning with nearby attraction lookup."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "origin": {
                "type": "string",
                "description": "The starting location (e.g. 'Mo Chit', 'Chatuchak Park')."
            },
            "stops": {
                "type": "array",
                "description": (
                    "Ordered list of stops. Each stop has a location and an arrival deadline. "
                    "Example: [{\"location\": \"Siam\", \"arrive_by\": \"10:00\"}, {\"location\": \"Sam Yan\", \"arrive_by\": \"13:00\"}]"
                ),
                "items": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The stop/destination name."
                        },
                        "arrive_by": {
                            "type": "string",
                            "description": "Latest arrival time in HH:MM 24-hour format."
                        }
                    },
                    "required": ["location", "arrive_by"]
                }
            }
        },
        "required": ["origin", "stops"]
    }
}

FUNCTION_DECLARATIONS = [
    find_route,
    line_of,
    same_line,
    is_transfer_station,
    needs_transfer,
    attraction_near_station,
    plan_trip,
    plan_day,
]
