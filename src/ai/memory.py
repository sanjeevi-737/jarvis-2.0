MAX_MESSAGES = 20


class ConversationMemory:
    def __init__(self, max_messages: int = MAX_MESSAGES):
        self.messages: list[dict] = []
        self.summary: str | None = None
        self.max_messages = max_messages

    def add_user(self, text: str) -> None:
        self.messages.append({"role": "user", "content": text})
        self._trim()

    def add_assistant(self, text: str) -> None:
        self.messages.append({"role": "assistant", "content": text})
        self._trim()

    def add_tool_calls(self, message) -> None:
        content = message.get("content") if isinstance(message, dict) else message.content
        entry = {"role": "assistant", "content": content}
        tool_calls = message.get("tool_calls") if isinstance(message, dict) else getattr(message, "tool_calls", None)
        if tool_calls:
            entry["tool_calls"] = []
            for tc in tool_calls:
                if isinstance(tc, dict):
                    entry["tool_calls"].append({
                        "id": tc["id"],
                        "type": "function",
                        "function": {
                            "name": tc["function"]["name"],
                            "arguments": tc["function"]["arguments"],
                        },
                    })
                else:
                    entry["tool_calls"].append({
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    })
        self.messages.append(entry)
        self._trim()

    def add_tool_result(self, tool_call_id: str, content: str) -> None:
        self.messages.append({
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": content,
        })
        self._trim()

    def get_messages(self) -> list[dict]:
        msgs = list(self.messages)
        if self.summary:
            msgs.insert(0, {
                "role": "system",
                "content": f"[Earlier conversation summary: {self.summary}]",
            })
        return msgs

    def set_summary(self, summary: str) -> None:
        self.summary = summary

    def clear(self) -> None:
        self.messages.clear()
        self.summary = None

    def _trim(self) -> None:
        if len(self.messages) <= self.max_messages:
            return
        keep_from = len(self.messages) - (self.max_messages // 2)
        # Don't split a tool_call message from its tool results
        while keep_from < len(self.messages) and self.messages[keep_from]["role"] == "tool":
            keep_from += 1
        excess = self.messages[:keep_from]
        topics = [
            (m.get("content") or "")[:80]
            for m in excess
            if m["role"] == "user" and m.get("content")
        ]
        self.summary = f"Previous topics: {'; '.join(topics)}" if topics else self.summary
        self.messages = self.messages[keep_from:]
