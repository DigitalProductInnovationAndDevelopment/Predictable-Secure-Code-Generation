from pydantic import BaseModel
import os

class Settings(BaseModel):
    llm_backend: str = os.getenv("LLM_BACKEND", "openai")
    model: str = os.getenv("MODEL", "gpt-4o-mini")
    temperature: float = float(os.getenv("TEMPERATURE", "0"))
