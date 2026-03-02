from dataclasses import dataclass
from typing import Iterable, Sequence

LEAD_CORE_FIELDS = ("Id", "LastName", "Company")
LEAD_EXTENDED_FIELDS = ("Id", "LastName", "Company", "Email", "Phone", "Title")

def _csv(items: Iterable[str]) -> str:
    return ", ".join(items)

def latest_lead(fields: Sequence[str] = LEAD_CORE_FIELDS) -> str:
    return f"SELECT {_csv(fields)} FROM Lead ORDER BY CreatedDate DESC LIMIT 1"

def lead_by_id(lead_id: str, fields: Sequence[str] = LEAD_CORE_FIELDS) -> str:
    return f"SELECT {_csv(fields)} FROM Lead WHERE Id = '{lead_id}' LIMIT 1"

def leads_created_by(username: str, fields: Sequence[str] = LEAD_CORE_FIELDS, limit: int = 5) -> str:
    return f"SELECT {_csv(fields)} FROM Lead WHERE CreatedBy.Username = '{username}' ORDER BY CreatedDate DESC LIMIT {int(limit)}"