from platform.kernel.registry import ProviderRegistry
from platform.adapters.fs.local_fs import LocalFileSystem, SimpleArtifactWriter
from platform.adapters.ai.openai_client import OpenAIClient

class Services:
    def __init__(self, providers, fs, writer, ai):
        self.providers = providers
        self.fs = fs
        self.writer = writer
        self.ai = ai

    # Lazy imports to avoid circulars
    @property
    def s1_usecases(self):
        from platform.app.s1_codegen.use_cases import S1UseCases
        return S1UseCases(self)

    @property
    def s2_usecases(self):
        from platform.app.s2_metadata.use_cases import S2UseCases
        return S2UseCases(self)

    @property
    def s3_usecases(self):
        from platform.app.s3_validation.use_cases import S3UseCases
        return S3UseCases(self)

def build_app() -> Services:
    providers = ProviderRegistry()
    fs = LocalFileSystem()
    writer = SimpleArtifactWriter()
    ai = OpenAIClient()
    return Services(providers, fs, writer, ai)
