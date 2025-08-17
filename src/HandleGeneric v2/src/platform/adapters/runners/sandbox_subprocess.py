"""Subprocess-based sandbox for code execution."""

import subprocess
import time
import os
from typing import List, Optional, Dict, Any
from pathlib import Path
from platform.ports.runners import Sandbox, ExecutionResult
from platform.kernel.logging import get_logger

logger = get_logger(__name__)


class SubprocessSandbox:
    """Subprocess-based sandbox implementation."""

    def execute(
        self,
        command: str,
        working_dir: Path,
        timeout_seconds: int = 60,
        env_vars: Optional[Dict[str, str]] = None,
        capture_output: bool = True,
    ) -> ExecutionResult:
        """Execute a command in a subprocess sandbox."""
        start_time = time.time()

        try:
            # Prepare environment
            env = os.environ.copy()
            if env_vars:
                env.update(env_vars)

            logger.info(
                "Executing command in sandbox",
                command=command,
                working_dir=str(working_dir),
                timeout=timeout_seconds,
            )

            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                cwd=working_dir,
                capture_output=capture_output,
                text=True,
                timeout=timeout_seconds,
                env=env,
            )

            execution_time = time.time() - start_time

            execution_result = ExecutionResult(
                return_code=result.returncode,
                stdout=result.stdout or "",
                stderr=result.stderr or "",
                execution_time=execution_time,
            )

            logger.info(
                "Command execution completed",
                return_code=result.returncode,
                execution_time=execution_time,
                success=execution_result.success,
            )

            return execution_result

        except subprocess.TimeoutExpired as e:
            execution_time = time.time() - start_time
            logger.error("Command execution timed out", timeout=timeout_seconds)

            return ExecutionResult(
                return_code=-1,
                stdout=e.stdout or "",
                stderr=f"Command timed out after {timeout_seconds} seconds",
                execution_time=execution_time,
            )

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error("Command execution failed", error=str(e))

            return ExecutionResult(
                return_code=-1,
                stdout="",
                stderr=f"Execution failed: {str(e)}",
                execution_time=execution_time,
            )

    def setup_environment(
        self, working_dir: Path, requirements: Optional[List[str]] = None
    ) -> None:
        """Set up the sandbox environment."""
        try:
            working_dir.mkdir(parents=True, exist_ok=True)

            if requirements:
                # Create requirements.txt
                req_file = working_dir / "requirements.txt"
                req_file.write_text("\n".join(requirements))

                # Install requirements in a virtual environment
                logger.info("Setting up virtual environment", working_dir=str(working_dir))

                # Create virtual environment
                self.execute("python -m venv .venv", working_dir, timeout_seconds=120)

                # Install requirements
                if os.name == "nt":  # Windows
                    pip_cmd = ".venv\\Scripts\\pip install -r requirements.txt"
                else:  # Unix-like
                    pip_cmd = ".venv/bin/pip install -r requirements.txt"

                self.execute(pip_cmd, working_dir, timeout_seconds=300)

            logger.info("Sandbox environment setup completed", working_dir=str(working_dir))

        except Exception as e:
            logger.error("Failed to setup sandbox environment", error=str(e))
            raise

    def cleanup(self, working_dir: Path) -> None:
        """Clean up sandbox resources."""
        try:
            # For subprocess sandbox, we mainly just clean up temporary files
            # In a more advanced implementation, this might stop containers, etc.

            temp_files = [".venv", "*.pyc", "__pycache__", "*.log"]

            for pattern in temp_files:
                if "*" in pattern:
                    for path in working_dir.glob(pattern):
                        if path.is_file():
                            path.unlink()
                        elif path.is_dir():
                            import shutil

                            shutil.rmtree(path, ignore_errors=True)
                else:
                    path = working_dir / pattern
                    if path.exists():
                        if path.is_file():
                            path.unlink()
                        elif path.is_dir():
                            import shutil

                            shutil.rmtree(path, ignore_errors=True)

            logger.info("Sandbox cleanup completed", working_dir=str(working_dir))

        except Exception as e:
            logger.warning("Sandbox cleanup failed", error=str(e))
