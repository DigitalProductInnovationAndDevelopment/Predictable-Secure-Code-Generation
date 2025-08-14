import subprocess, json, tempfile, os

class PytestRunner:
    def run(self, root: str, selector: str | None = None):
        cmd = ["pytest", "-q"]
        if selector:
            cmd.append(selector)
        try:
            subprocess.check_call(cmd, cwd=root)
            return {"status":"passed", "passed": 1, "failed": 0, "errors": 0}
        except subprocess.CalledProcessError:
            return {"status":"failed", "passed": 0, "failed": 1, "errors": 0}
