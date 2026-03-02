from jsonschema import Draft202012Validator

def assert_matches_schema(payload: object, schema: dict) -> None:
    v = Draft202012Validator(schema)
    errors = sorted(v.iter_errors(payload), key=lambda e: e.path)
    if errors:
        e = errors[0]
        path = ".".join(str(p) for p in e.path) or "<root>"
        raise AssertionError(f"Schema mismatch at {path}: {e.message}")