from platform.domain.models.generation import GeneratedFile
from platform.domain.models.requirements import Requirement

class PythonCodeGenProvider:
    language = "python"

    def build_prompt(self, requirement: Requirement, context: dict) -> str:
        return f"""Generate a Python module that implements:
Title: {requirement.title}
Description: {requirement.description}
Acceptance:
- {'\n- '.join(requirement.acceptance)}"""

    def postprocess(self, files: list[GeneratedFile]) -> list[GeneratedFile]:
        # Hook: format with black/isort if desired
        return files
