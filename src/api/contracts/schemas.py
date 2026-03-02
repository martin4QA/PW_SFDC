LEAD_SCHEMA = {
    "type": "object",
    "required": ["attributes", "Id", "LastName", "Company"],
    "properties": {
        "attributes": {"type": "object"},
        "Id": {"type": "string"},
        "LastName": {"type": "string"},
        "Company": {"type": "string"},
        "Email": {"type": ["string", "null"]},
        "Phone": {"type": ["string", "null"]},
        "Title": {"type": ["string", "null"]},
    },
    "additionalProperties": True,
}

LIMITS_SCHEMA = {
    "type": "object",
    "additionalProperties": {
        "type": "object",
        "required": ["Max", "Remaining"],
        "properties": {
            "Max": {"type": "integer"},
            "Remaining": {"type": "integer"},
        },
        "additionalProperties": True,
    },
}