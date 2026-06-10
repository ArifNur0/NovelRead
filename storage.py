import json
import os
import threading
from typing import Any

import config

_LOCK = threading.Lock()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

USERS_PATH = os.path.join(DATA_DIR, "users.json")
NOVELS_PATH = os.path.join(DATA_DIR, "novels.json")


def _ensure_files_exist() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    for p, default in [(USERS_PATH, []), (NOVELS_PATH, [])]:
        if not os.path.exists(p):
            with open(p, "w", encoding="utf-8") as f:
                json.dump(default, f)


def load_json(path: str) -> Any:
    _ensure_files_exist()
    with _LOCK:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)


def save_json(path: str, data: Any) -> None:
    _ensure_files_exist()
    with _LOCK:
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)


def _kv_enabled() -> bool:
    return bool(getattr(config, "KV_URL", ""))


def _kv_key(kind: str) -> str:
    return f"{config.KV_PREFIX}{kind}"  # includes trailing colon in prefix if desired


def _kv_get_json(kind: str, default: Any) -> Any:
    # Uses redis-compatible KV (Upstash). Requires KV_URL env.
    if not _kv_enabled():
        # fallback file system
        if kind == "users":
            return load_json(USERS_PATH)
        if kind == "novels":
            return load_json(NOVELS_PATH)
        return default

    import redis  # lazy import

    r = redis.from_url(config.KV_URL, decode_responses=True)
    key = _kv_key(kind)
    val = r.get(key)
    if val is None:
        return default
    return json.loads(val)


def _kv_set_json(kind: str, data: Any) -> None:
    if not _kv_enabled():
        if kind == "users":
            save_json(USERS_PATH, data)
        elif kind == "novels":
            save_json(NOVELS_PATH, data)
        return

    import redis  # lazy import

    r = redis.from_url(config.KV_URL, decode_responses=True)
    key = _kv_key(kind)
    r.set(key, json.dumps(data, ensure_ascii=False))


def get_users():
    return _kv_get_json("users", default=[])


def get_novels():
    return _kv_get_json("novels", default=[])


def add_user(username: str, password_hash: str) -> dict:
    users = get_users()
    if any(u.get("username") == username for u in users):
        raise ValueError("username already exists")
    next_id = (max([u.get("id", 0) for u in users]) + 1) if users else 1
    user = {"id": next_id, "username": username, "password": password_hash}
    users.append(user)
    _kv_set_json("users", users)
    return user


def find_user_by_username(username: str):
    users = get_users()
    for u in users:
        if u.get("username") == username:
            return u
    return None


def add_novel(user_id: int, title: str, author: str | None, cover_path: str, pdf_path: str) -> dict:
    novels = get_novels()
    next_id = (max([n.get("id", 0) for n in novels]) + 1) if novels else 1
    novel = {
        "id": next_id,
        "title": title,
        "author": author,
        "cover_path": cover_path,
        "pdf_path": pdf_path,
        "uploaded_at": None,  # optional; set in app
        "user_id": user_id,
    }
    novels.append(novel)
    _kv_set_json("novels", novels)
    return novel


def delete_novel(user_id: int, novel_id: int) -> bool:
    """Hapus novel milik user tertentu (JSON -> file system atau KV)."""
    novels = get_novels()
    new_list = []
    deleted = False

    for n in novels:
        if int(n.get("id", -1)) == int(novel_id):
            if int(n.get("user_id")) != int(user_id):
                # found but not owned
                new_list.append(n)
                continue
            deleted = True
            continue
        new_list.append(n)

    if deleted:
        _kv_set_json("novels", new_list)
    return deleted



