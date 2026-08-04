"""
Minimal ExtraHop RevealX 360 REST API client.

Handles OAuth2 client-credentials auth with automatic token refresh,
plus convenience methods for paginated endpoints.

Setup:
    export EXTRAHOP_HOST=your-tenant.api.cloud.extrahop.com
    export EXTRAHOP_CLIENT_ID=<your-client-id>
    export EXTRAHOP_CLIENT_SECRET=<your-client-secret>

Usage:
    from extrahop_client import ExtraHopClient
    client = ExtraHopClient()
    resp = client.post("/detections/search", json={
        "filter": {"risk_score_min": 80, "status": ["new", "in_progress"]},
        "limit": 100,
    })
    detections = resp.json()
"""
import base64
import os
import time
from typing import Any, Dict, Iterator, Optional

import requests


class ExtraHopClient:
    def __init__(
        self,
        host: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        timeout: int = 30,
    ):
        self.host = host or os.environ["EXTRAHOP_HOST"]
        self.client_id = client_id or os.environ["EXTRAHOP_CLIENT_ID"]
        self.client_secret = client_secret or os.environ["EXTRAHOP_CLIENT_SECRET"]
        self.base_url = f"https://{self.host}/api/v1"
        self.token_url = f"https://{self.host}/oauth2/token"
        self.timeout = timeout

        self._token: Optional[str] = None
        self._token_expires_at: float = 0.0
        self._session = requests.Session()

    # --- auth ---------------------------------------------------------------

    def _fetch_token(self) -> str:
        """Get a new OAuth2 access token via client credentials grant."""
        creds = f"{self.client_id}:{self.client_secret}".encode()
        auth_header = base64.b64encode(creds).decode()
        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        resp = requests.post(
            self.token_url,
            headers=headers,
            data="grant_type=client_credentials",
            timeout=self.timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        # Refresh 60s before expiry to be safe
        self._token = data["access_token"]
        self._token_expires_at = time.time() + data.get("expires_in", 3600) - 60
        return self._token

    def _auth_header(self) -> Dict[str, str]:
        if not self._token or time.time() >= self._token_expires_at:
            self._fetch_token()
        return {"Authorization": f"Bearer {self._token}"}

    # --- core requests ------------------------------------------------------

    def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        **kwargs,
    ) -> requests.Response:
        """Make an authenticated request. `path` is relative to /api/v1 (e.g. '/detections/search')."""
        url = f"{self.base_url}{path}"
        headers = self._auth_header()
        headers.setdefault("Accept", "application/json")
        if json is not None:
            headers.setdefault("Content-Type", "application/json")

        resp = self._session.request(
            method.upper(), url,
            params=params, json=json, headers=headers,
            timeout=self.timeout, **kwargs,
        )
        # Retry once on 401 in case the token expired mid-flight
        if resp.status_code == 401:
            self._token = None
            headers = self._auth_header()
            headers.setdefault("Accept", "application/json")
            if json is not None:
                headers.setdefault("Content-Type", "application/json")
            resp = self._session.request(
                method.upper(), url,
                params=params, json=json, headers=headers,
                timeout=self.timeout, **kwargs,
            )
        return resp

    def get(self, path: str, **kw) -> requests.Response:
        return self.request("GET", path, **kw)

    def post(self, path: str, **kw) -> requests.Response:
        return self.request("POST", path, **kw)

    def patch(self, path: str, **kw) -> requests.Response:
        return self.request("PATCH", path, **kw)

    def put(self, path: str, **kw) -> requests.Response:
        return self.request("PUT", path, **kw)

    def delete(self, path: str, **kw) -> requests.Response:
        return self.request("DELETE", path, **kw)

    # --- pagination helpers -------------------------------------------------

    def paginate_offset(
        self,
        path: str,
        page_size: int = 100,
        max_results: Optional[int] = None,
        extra_params: Optional[Dict[str, Any]] = None,
    ) -> Iterator[Dict[str, Any]]:
        """
        Iterate a GET endpoint that supports `limit` + `offset` query params.
        Works for endpoints like GET /devices.
        """
        offset = 0
        yielded = 0
        while True:
            params = dict(extra_params or {})
            params["limit"] = page_size
            params["offset"] = offset
            resp = self.get(path, params=params)
            resp.raise_for_status()
            page = resp.json()
            if not page:
                return
            for item in page:
                yield item
                yielded += 1
                if max_results and yielded >= max_results:
                    return
            if len(page) < page_size:
                return
            offset += page_size

    def paginate_search(
        self,
        path: str,
        body: Dict[str, Any],
        max_results: Optional[int] = None,
    ) -> Iterator[Dict[str, Any]]:
        """
        Iterate a POST search endpoint that returns a paginated cursor.
        Some endpoints (e.g. POST /detections/search, POST /records/search)
        return an `offset` or `cursor` in the response — adjust as needed.
        """
        offset = body.get("offset", 0)
        limit = body.get("limit", 100)
        yielded = 0
        while True:
            page_body = dict(body)
            page_body["offset"] = offset
            page_body["limit"] = limit
            resp = self.post(path, json=page_body)
            resp.raise_for_status()
            data = resp.json()
            items = data if isinstance(data, list) else data.get("detections", data.get("results", []))
            if not items:
                return
            for item in items:
                yield item
                yielded += 1
                if max_results and yielded >= max_results:
                    return
            if len(items) < limit:
                return
            offset += limit


if __name__ == "__main__":
    # Smoke test: list the first detection.
    client = ExtraHopClient()
    resp = client.post("/detections/search", json={"limit": 1})
    resp.raise_for_status()
    print(resp.json())
