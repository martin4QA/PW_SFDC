from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from api.http_client import ApiClient


@dataclass(frozen=True)
class CreateResult:
    success: bool
    id: Optional[str]
    errors: list


def create_lead(
    client: ApiClient,
    api_version: str,
    lead: Dict[str, Any],
) -> CreateResult:
    """
    Create a Salesforce Lead via REST API.

    Args:
        client: Authenticated ApiClient (Bearer token + instance_url base)
        api_version: e.g. "60.0"
        lead: Dict payload with SF Lead fields (e.g. LastName, Company, Email...)

    Returns:
        CreateResult(success, id, errors)

    Raises:
        AssertionError: if response is not 201 or payload unexpected (keeps tests clear)
    """
    resp = client.post(
        f"/services/data/v{api_version}/sobjects/Lead/",
        json=lead,
    )

    # Salesforce returns 201 Created on success
    assert resp.status_code == 201, f"Lead create failed: {resp.status_code} {resp.text}"
    assert resp.json is not None, f"Lead create returned no JSON: {resp.text}"

    return CreateResult(
        success=bool(resp.json.get("success")),
        id=resp.json.get("id"),
        errors=resp.json.get("errors", []),
    )


def delete_lead(client: ApiClient, api_version: str, lead_id: str) -> None:
    """
    Delete a Salesforce Lead via REST API. Useful for test cleanup.
    """
    resp = client.request(
        "DELETE",
        f"/services/data/v{api_version}/sobjects/Lead/{lead_id}",
    )
    # On delete: 204 No Content is typical
    assert resp.status_code in (204, 200), f"Lead delete failed: {resp.status_code} {resp.text}"