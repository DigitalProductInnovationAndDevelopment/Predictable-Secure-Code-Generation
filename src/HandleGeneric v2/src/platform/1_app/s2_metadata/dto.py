from pydantic import BaseModel

class MetadataInput(BaseModel):
    root: str
    language: str = "python"
