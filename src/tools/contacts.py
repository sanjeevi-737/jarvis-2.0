"""
Local contact store — offline fallback when ATXP is not configured.

These functions are internal helpers. They are NOT registered as LLM tools
because the ATXP bridge (atxp_bridge.py) already exposes lookup_contact,
list_contacts, and add_contact as proper tools backed by the ATXP CLI.

Use this module directly in Python code when you need offline contact
resolution (e.g. pre-filling a phone number before calling _run_npx).
"""

import json
from src.config import ROOT_DIR

CONTACTS_FILE = ROOT_DIR / "config" / "local_contacts.json"


def _load() -> dict:
    if CONTACTS_FILE.exists():
        try:
            return json.loads(CONTACTS_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save(data: dict) -> None:
    CONTACTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONTACTS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def resolve_name(name: str) -> dict | None:
    """Return the first contact whose name contains `name` (case-insensitive)."""
    contacts = _load()
    name_lower = name.lower()
    for key, info in contacts.items():
        if name_lower in key.lower():
            return {"name": key, **info}
    return None


def add_local(name: str, phone: str = "", email: str = "") -> None:
    """Upsert a contact in the local JSON store."""
    contacts = _load()
    contacts[name] = {"phone": phone, "email": email}
    _save(contacts)


def list_local() -> dict:
    """Return all local contacts."""
    return _load()
