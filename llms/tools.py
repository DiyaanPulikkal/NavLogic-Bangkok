# Function Declarations for LLM

find_route = {
    "name": "find_route",
    "description": (
        "Find the best route between two locations in Bangkok's public transit network. "
        "Use this when the user wants to travel from one place to another. "
        "Locations can be station names or attraction names."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "start": {
                "type": "string",
                "description": "The starting station or attraction name (e.g. 'Mo Chit (N8)' or 'Grand Palace')."
            },
            "end": {
                "type": "string",
                "description": "The destination station or attraction name (e.g. 'Siam (CEN)' or 'Terminal 21')."
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
                "description": "The exact name of the station (e.g. 'Asok (E4)')."
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
                "description": "The exact name of the first station."
            },
            "station_b": {
                "type": "string",
                "description": "The exact name of the second station."
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
                "description": "The exact name of the station to check (e.g. 'Siam (CEN)')."
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
                "description": "The exact name of the starting station."
            },
            "station_b": {
                "type": "string",
                "description": "The exact name of the destination station."
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
                "description": "The name of the attraction (e.g. 'Grand Palace', 'Chatuchak Weekend Market')."
            }
        },
        "required": ["attraction_name"]
    }
}

FUNCTION_DECLARATIONS = [
    find_route,
    line_of,
    same_line,
    is_transfer_station,
    needs_transfer,
    attraction_near_station,
]
