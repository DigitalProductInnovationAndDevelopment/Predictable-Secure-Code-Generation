from pathlib import Path
from typing import List
from platform.domain.models.requirements import Requirement
from platform.app.s1_codegen.pipeline import run_pipeline

class S1UseCases:
    def __init__(self, services):
        self.sv = services

    def generate(self, reqs: List[Requirement], lang: str, out_dir: str):
        Path(out_dir).mkdir(parents=True, exist_ok=True)
        return run_pipeline(self.sv, lang, reqs, out_dir)
