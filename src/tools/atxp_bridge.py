import asyncio
import json
import shlex
from typing import Optional

from src.tools.registry import tool


async def _run_npx(args: list[str]) -> str:
    cmd = ["atxp.cmd"] + args
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        return f"Error: {stderr.decode().strip()}"
    return stdout.decode().strip()


@tool(
    name="send_sms",
    description="Send an SMS message to a phone number",
    parameters={
        "to": {"type": "string", "description": "Phone number (E.164 format, e.g. +1234567890)"},
        "body": {"type": "string", "description": "SMS message text"},
    },
)
async def send_sms(to: str, body: str) -> str:
    return await _run_npx(["phone", "send-sms", "--to", to, "--body", body])


@tool(
    name="make_call",
    description="Make a voice call to a phone number. JARVIS will speak the instruction to the recipient.",
    parameters={
        "to": {"type": "string", "description": "Phone number (E.164 format)"},
        "instruction": {"type": "string", "description": "What JARVIS should say on the call"},
    },
)
async def make_call(to: str, instruction: str) -> str:
    return await _run_npx(["phone", "call", "--to", to, "--instruction", instruction])


@tool(
    name="send_email",
    description="Send an email message",
    parameters={
        "to": {"type": "string", "description": "Recipient email address"},
        "subject": {"type": "string", "description": "Email subject line"},
        "body": {"type": "string", "description": "Email body text"},
    },
)
async def send_email(to: str, subject: str, body: str) -> str:
    return await _run_npx(["email", "send", "--to", to, "--subject", subject, "--body", body])


@tool(
    name="check_inbox",
    description="Check email inbox for new messages",
    parameters={},
)
async def check_inbox() -> str:
    return await _run_npx(["email", "inbox"])


@tool(
    name="check_sms",
    description="Check SMS inbox for new messages",
    parameters={
        "unread_only": {"type": "boolean", "description": "Only show unread messages"},
    },
)
async def check_sms(unread_only: bool = True) -> str:
    args = ["phone", "sms"]
    if unread_only:
        args.append("--unread-only")
    return await _run_npx(args)


@tool(
    name="search_web",
    description="Search the web for information",
    parameters={
        "query": {"type": "string", "description": "Search query"},
    },
)
async def search_web(query: str) -> str:
    return await _run_npx(["search", query])


@tool(
    name="lookup_contact",
    description="Search contacts by name or query",
    parameters={
        "query": {"type": "string", "description": "Name or query to search"},
    },
)
async def lookup_contact(query: str) -> str:
    return await _run_npx(["contacts", "search", query])


@tool(
    name="list_contacts",
    description="List all saved contacts",
    parameters={},
)
async def list_contacts() -> str:
    return await _run_npx(["contacts", "list"])


@tool(
    name="check_balance",
    description="Check ATXP account balance",
    parameters={},
)
async def check_balance() -> str:
    return await _run_npx(["balance"])


@tool(
    name="read_call_history",
    description="Check recent call history",
    parameters={
        "direction": {"type": "string", "description": "Filter: 'incoming' or 'sent'", "enum": ["incoming", "sent"]},
    },
)
async def read_call_history(direction: str = "") -> str:
    args = ["phone", "calls"]
    if direction:
        args.extend(["--direction", direction])
    return await _run_npx(args)


@tool(
    name="add_contact",
    description="Add a new contact",
    parameters={
        "name": {"type": "string", "description": "Contact name"},
        "phone": {"type": "string", "description": "Phone number (optional)"},
        "email": {"type": "string", "description": "Email address (optional)"},
        "notes": {"type": "string", "description": "Notes (optional)"},
    },
)
async def add_contact(name: str, phone: str = "", email: str = "", notes: str = "") -> str:
    args = ["contacts", "add", "--name", name]
    if phone:
        args.extend(["--phone", phone])
    if email:
        args.extend(["--email", email])
    if notes:
        args.extend(["--notes", notes])
    return await _run_npx(args)
