from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests


@dataclass
class ApiResponse:
    status_code: int
    headers: Dict[str, str]
    json: Optional[Dict[str, Any]]
    text: str


class ApiClient:
    def __init__(self, base_url: str, token: str, session: requests.Session | None = None):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.session = session or requests.Session()

    def request(self, method: str, path: str, **kwargs) -> ApiResponse:
        url = f"{self.base_url}{path}"
        headers = kwargs.pop("headers", {})
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            **headers,
        }

        r = self.session.request(method, url, headers=headers, timeout=30, **kwargs)
        try:
            payload = r.json()
            if not isinstance(payload, dict):
                payload = {"_value": payload}
        except Exception:
            payload = None

        return ApiResponse(r.status_code, dict(r.headers), payload, r.text)

    def get(self, path: str, **kwargs) -> ApiResponse:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs) -> ApiResponse:
        return self.request("POST", path, **kwargs)

    def delete(self, path: str, **kwargs) -> ApiResponse:
        return self.request("DELETE", path, **kwargs)
