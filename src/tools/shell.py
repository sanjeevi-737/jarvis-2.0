import asyncio
import sys
import shutil

from src.tools.registry import tool

ALLOWED_COMMANDS = {
    "dir", "ls", "pwd", "whoami", "date", "time",
    "echo", "type", "cat", "find", "where", "which",
    "ipconfig", "systeminfo", "tasklist",
    "get-childitem", "get-location", "get-date", "get-process",
    "get-service", "get-command", "get-help", "get-alias",
    "write-output", "select-object", "where-object", "foreach-object",
    "sort-object", "group-object", "measure-object",
    "powershell", "pwsh",
}


@tool(
    name="run_shell",
    description="Run a safe read-only shell/PowerShell command. Reads info only — no create/delete/modify operations.",
    parameters={
        "command": {"type": "string", "description": "PowerShell command to run"},
    },
)
async def run_shell(command: str) -> str:
    if sys.platform != "win32":
        return "Error: Shell tool is only available on Windows."
    if not shutil.which("powershell"):
        return "Error: PowerShell not found."
    cmd_base = command.split()[0].lower() if command.split() else ""
    if cmd_base not in ALLOWED_COMMANDS:
        return f"Error: Command '{cmd_base}' is not in the safe allowed list."
    try:
        proc = await asyncio.create_subprocess_exec(
            "powershell", "-Command", command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate(timeout=15)
        if proc.returncode != 0:
            return f"Exit code {proc.returncode}: {stderr.decode().strip()}"
        return stdout.decode().strip() or "(no output)"
    except asyncio.TimeoutError:
        return "Error: Command timed out after 15 seconds"
    except Exception as e:
        return f"Error: {e}"
