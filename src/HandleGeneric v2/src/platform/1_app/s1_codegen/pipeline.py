from pathlib import Path
from platform.domain.models.generation import GeneratedFile, CodeGenReport
from platform.domain.models.requirements import Requirement

def run_pipeline(services, lang: str, reqs: list[Requirement], out_dir: str) -> CodeGenReport:
    provider = services.providers.get_codegen(lang)
    # Build a trivial "generated file" to demonstrate flow
    files = []
    for r in reqs:
        content = f""""""
# Auto-generated module
"""
def feature():
    """{r.title}: {r.description}"""
    return True
"""
        files.append(GeneratedFile(path=f"{r.id}.py", content=content))
    files = provider.postprocess(files)
    services.writer.write(Path(out_dir), files)
    return CodeGenReport(files=files, rationale="stub rationale", cost_tokens=0)
