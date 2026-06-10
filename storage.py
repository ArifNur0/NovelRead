import json
import os
import threading
from typing import Any

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


def get_users():
    return load_json(USERS_PATH)


def get_novels():
    return load_json(NOVELS_PATH)


def add_user(username: str, password_hash: str) -> dict:
    users = get_users()
    if any(u.get("username") == username for u in users):
        raise ValueError("username already exists")
    next_id = (max([u.get("id", 0) for u in users]) + 1) if users else 1
    user = {"id": next_id, "username": username, "password": password_hash}
    users.append(user)
    save_json(USERS_PATH, users)
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
    save_json(NOVELS_PATH, novels)
    return novel


def delete_novel(user_id: int, novel_id: int) -> bool:
    """Hapus novel milik user tertentu (JSON storage)."""
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
        save_json(NOVELS_PATH, new_list)
    return deleted


