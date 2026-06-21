import json
import inspect
from typing import Any, Callable

_TOOLS: dict[str, Callable] = {}
_TOOL_DEFINITIONS: list[dict] = []


def tool(name: str, description: str, parameters: dict):
    def decorator(func: Callable):
        _TOOLS[name] = func
        _TOOL_DEFINITIONS.append({
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": parameters,
                    "required": list(parameters.keys()),
                },
            },
        })
        return func
    return decorator


def get_tool_definitions() -> list[dict]:
    return _TOOL_DEFINITIONS


async def execute_tool(name: str, arguments: dict[str, Any]) -> str:
    func = _TOOLS.get(name)
    if not func:
        return json.dumps({"error": f"Tool '{name}' not found"})
    try:
        if inspect.iscoroutinefunction(func):
            result = await func(**arguments)
        else:
            result = func(**arguments)
        return json.dumps({"result": result})
    except Exception as e:
        return json.dumps({"error": str(e)})


import src.tools.atxp_bridge  # noqa: F401, E402
import src.tools.shell  # noqa: F401, E402
