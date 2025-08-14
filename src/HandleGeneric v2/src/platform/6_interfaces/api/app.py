from fastapi import FastAPI
from pydantic import BaseModel
from platform.kernel.di import build_app

app = FastAPI(title="Handle Platform API")
sv = build_app()

class CodegenBody(BaseModel):
    language: str
    requirements: list[dict]
    out_dir: str = "out"

@app.post("/s1/generate")
def s1_generate(body: CodegenBody):
    from platform.domain.models.requirements import Requirement
    reqs = [Requirement(**r) for r in body.requirements]
    rep = sv.s1_usecases.generate(reqs, body.language, body.out_dir)
    return rep.model_dump()

class MetadataBody(BaseModel):
    root: str

@app.post("/s2/metadata")
def s2_metadata(body: MetadataBody):
    report = sv.s2_usecases.generate_metadata(body.root)
    return report.model_dump()

class ValidateBody(BaseModel):
    root: str
    run_tests: bool = True
    ai_check: bool = False

@app.post("/s3/validate")
def s3_validate(body: ValidateBody):
    res = sv.s3_usecases.validate(body.root, body.run_tests, body.ai_check)
    return res
