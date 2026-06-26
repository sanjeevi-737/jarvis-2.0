import json

from src.config import ROOT_DIR

CONTACTS_FILE = ROOT_DIR / "config" / "local_contacts.json"


def _load() -> dict:
    if CONTACTS_FILE.exists():
        return json.loads(CONTACTS_FILE.read_text())
    return {}


def _save(data: dict) -> None:
    CONTACTS_FILE.write_text(json.dumps(data, indent=2))


def resolve_name(name: str) -> dict | None:
    contacts = _load()
    name_lower = name.lower()
    for key, info in contacts.items():
        if name_lower in key.lower():
            return {"name": key, **info}
    return None


def add_local(name: str, phone: str = "", email: str = "") -> None:
    contacts = _load()
    contacts[name] = {"phone": phone, "email": email}
    _save(contacts)


def list_local() -> dict:
    return _load()
