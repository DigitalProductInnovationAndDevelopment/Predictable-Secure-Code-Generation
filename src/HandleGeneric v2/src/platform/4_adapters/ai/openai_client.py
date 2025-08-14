# Placeholder adapter – wire your real OpenAI/Azure client here.
class OpenAIClient:
    def complete(self, messages: list[dict], **kw) -> dict:
        # Return a stub response to keep the skeleton runnable offline.
        return {"content": "# generated code\n"}
