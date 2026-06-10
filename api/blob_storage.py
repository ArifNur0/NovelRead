import json
from dataclasses import dataclass
from typing import Any

import vercel_blob

import config


@dataclass(frozen=True)
class BlobJSONPaths:
    users: str = "data/users.json"
    novels: str = "data/novels.json"


BLOB_PATHS = BlobJSONPaths()


def _client() -> Any:
    return vercel_blob.BlobClient(
        store_id=config.BLOB_STORE_ID,
        token=config.BLOB_READ_WRITE_TOKEN,
    )


def _get_or_default(blob_name: str, default: Any) -> Any:
    # Blob might be unavailable/misconfigured on Vercel (env vars not set, wrong token, etc).
    # This function must never crash the app.
    client = _client()
    try:
        resp = client.get(blob_name)
        if isinstance(resp, (bytes, bytearray)):
            return json.loads(resp.decode("utf-8"))
        if isinstance(resp, str):
            return json.loads(resp)
        if hasattr(resp, "data") and resp.data is not None:
            raw = resp.data
            if isinstance(raw, (bytes, bytearray)):
                return json.loads(raw.decode("utf-8"))
            return json.loads(raw)
        if hasattr(resp, "text"):
            return json.loads(resp.text)
        return json.loads(resp)
    except Exception:
        return default



def blob_get_json(kind: str, default: Any) -> Any:
    if kind == "users":
        return _get_or_default(BLOB_PATHS.users, default)
    if kind == "novels":
        return _get_or_default(BLOB_PATHS.novels, default)
    return default


def blob_set_json(kind: str, data: Any) -> None:
    client = _client()
    raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
    if kind == "users":
        client.put(
            blob_name=BLOB_PATHS.users,
            data=raw,
            content_type="application/json",
        )
        return
    if kind == "novels":
        client.put(
            blob_name=BLOB_PATHS.novels,
            data=raw,
            content_type="application/json",
        )
        return
    raise ValueError(f"Unknown blob json kind: {kind}")

