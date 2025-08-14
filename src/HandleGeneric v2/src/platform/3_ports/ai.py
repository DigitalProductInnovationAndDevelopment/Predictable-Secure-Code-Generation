from typing import Protocol, Any

class LLMClient(Protocol):
    def complete(self, messages: list[dict[str, Any]], **kw) -> dict: ...
