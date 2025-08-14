from pathlib import Path
from platform.domain.models.validation import SyntaxResult, TestResult, AILogicReport

def run_pipeline(services, root: str, run_tests: bool = True, ai_check: bool = False):
    # Syntax quick pass over *.py
    syntax = []
    for p in Path(root).rglob("*.py"):
        res = services.providers.get_syntax("python").validate(p, p.read_text(encoding="utf-8"))
        syntax.append(res)
    # Aggregate syntax
    status = "valid" if all(s.status == "valid" for s in syntax) else "invalid"
    syntax_result = {"status": status, "files_checked": len(syntax)}

    # Tests
    test_result: dict | None = None
    if run_tests:
        test_result = services.__dict__.get("pytest_runner") or services.__dict__.setdefault(
            "pytest_runner", None
        )
        # Use the adapter directly (simple case)
        from platform.adapters.runners.pytest_runner import PytestRunner
        runner = PytestRunner()
        test_result = runner.run(root)

    # AI logic (stubbed)
    ai_report: dict | None = None
    if ai_check:
        ai_report = {"status": "warnings", "findings": []}

    return {"syntax": syntax_result, "tests": test_result, "ai": ai_report}
