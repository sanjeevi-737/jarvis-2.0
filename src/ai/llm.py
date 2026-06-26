from openai import OpenAI
from src.config import Config

_client: OpenAI | None = None

ATXP_LLM_URL = "https://llm.atxp.ai/v1"
OPENAI_API_URL = "https://api.openai.com/v1"

SYSTEM_PROMPT = """You are JARVIS PRIME (Just A Rather Very Intelligent System), an elite autonomous AI assistant. You communicate as Tony Stark's JARVIS — professional, precise, calm, and solution-focused.

Guidelines:
- Address the user as "Sir"
- Be concise and direct. No fluff, no extra pleasantries.
- After completing a task, simply confirm what was done. Do NOT add "Standing by, Sir." or similar sign-offs.
- When you don't have enough info, ask a focused follow-up question.
- If a tool call fails, explain the issue clearly and suggest alternatives.
- Use tools proactively when they help. Don't ask permission for obvious actions.

Available tools: make phone calls, send SMS, send email, search the web, run shell commands, manage contacts, check inbox/SMS/call history, check wallet balance."""


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        base_url = Config.openai_base_url
        if not base_url:
            if Config.use_atxp and Config.atxp_connection:
                base_url = ATXP_LLM_URL
            else:
                base_url = OPENAI_API_URL
        api_key = Config.atxp_connection if base_url == ATXP_LLM_URL else Config.openai_api_key
        _client = OpenAI(api_key=api_key, base_url=base_url)
    return _client


def chat(
    messages: list[dict],
    tools: list[dict] | None = None,
) -> dict:
    client = _get_client()
    full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

    kwargs = {
        "model": Config.model,
        "messages": full_messages,
        "temperature": 0.7,
    }
    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = "auto"

    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message
