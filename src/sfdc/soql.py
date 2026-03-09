from typing import Iterable, Sequence

LEAD_CORE_FIELDS = ("Id", "LastName", "Company")
LEAD_EXTENDED_FIELDS = ("Id", "LastName", "Company", "Email", "Phone", "Title")

# Helper functions to build SOQL queries for Lead object

# function to convert list of fields to comma-separated string for SOQL SELECT clause
def _csv(items: Iterable[str]) -> str:
    return ", ".join(items)

# Get the latest created Lead with specified fields (default to core fields)
def latest_lead(fields: Sequence[str] = LEAD_CORE_FIELDS) -> str:
    return f"SELECT {_csv(fields)} FROM Lead ORDER BY CreatedDate DESC LIMIT 1"

# Get a Lead by its Salesforce Id with specified fields (default to core fields)
def lead_by_id(lead_id: str, fields: Sequence[str] = LEAD_CORE_FIELDS) -> str:
    return f"SELECT {_csv(fields)} FROM Lead WHERE Id = '{lead_id}' LIMIT 1"

# Get recent Leads created by a specific user with specified fields (default to core fields)
def leads_created_by(
    username: str, fields: Sequence[str] = LEAD_CORE_FIELDS, limit: int = 5
) -> str:
    return (
        "SELECT "
        f"{_csv(fields)} "
        "FROM Lead "
        "WHERE CreatedBy.Username = "
        f"'{username}' "
        "ORDER BY CreatedDate DESC "
        f"LIMIT {int(limit)}"
    )
