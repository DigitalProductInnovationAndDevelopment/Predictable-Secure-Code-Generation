from pydantic import BaseModel

class ValidationInput(BaseModel):
    root: str
    run_tests: bool = True
    ai_check: bool = False
