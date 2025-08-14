from platform.app.s2_metadata.pipeline import run_pipeline

class S2UseCases:
    def __init__(self, services):
        self.sv = services

    def generate_metadata(self, root: str):
        return run_pipeline(self.sv, root, lang="python")
