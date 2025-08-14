from platform.adapters.providers.python.codegen_provider import PythonCodeGenProvider
from platform.adapters.providers.python.metadata_provider import PythonMetadataProvider
from platform.adapters.providers.python.syntax_validator import PythonSyntaxValidator

class ProviderRegistry:
    def __init__(self):
        self.codegen = {"python": PythonCodeGenProvider()}
        self.metadata = {"python": PythonMetadataProvider()}
        self.syntax = {"python": PythonSyntaxValidator()}

    def get_codegen(self, lang: str):
        return self.codegen[lang]

    def get_metadata(self, lang: str):
        return self.metadata[lang]

    def get_syntax(self, lang: str):
        return self.syntax[lang]
