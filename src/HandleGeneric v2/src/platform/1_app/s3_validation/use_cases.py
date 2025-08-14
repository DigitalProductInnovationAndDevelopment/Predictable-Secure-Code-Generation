from platform.app.s3_validation.pipeline import run_pipeline

class S3UseCases:
    def __init__(self, services):
        self.sv = services

    def validate(self, root: str, run_tests: bool = True, ai_check: bool = False):
        return run_pipeline(self.sv, root, run_tests=run_tests, ai_check=ai_check)
