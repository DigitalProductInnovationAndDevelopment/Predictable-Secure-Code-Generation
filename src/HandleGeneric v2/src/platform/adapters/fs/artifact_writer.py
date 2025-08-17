"""Artifact writer for generated code files."""

import json
from typing import List, Dict, Any
from pathlib import Path
from platform.ports.fs import ArtifactWriter
from platform.domain.models.generation import GeneratedFile
from platform.kernel.logging import get_logger

logger = get_logger(__name__)


class LocalArtifactWriter:
    """Local file system artifact writer."""

    def write(self, root: Path, files: List[GeneratedFile]) -> None:
        """Write generated files to the specified root directory."""
        try:
            # Ensure root directory exists
            root.mkdir(parents=True, exist_ok=True)

            for file in files:
                file_path = root / file.path
                file_path.parent.mkdir(parents=True, exist_ok=True)

                file_path.write_text(file.content, encoding="utf-8")
                logger.debug(
                    "Wrote generated file",
                    path=str(file_path),
                    size=len(file.content),
                    language=file.language,
                )

            logger.info("All generated files written", root=str(root), file_count=len(files))

        except Exception as e:
            logger.error("Failed to write artifacts", root=str(root), error=str(e))
            raise

    def write_report(self, root: Path, report: Dict[str, Any]) -> Path:
        """Write a generation report to the root directory."""
        try:
            report_path = root / "generation_report.json"
            report_path.parent.mkdir(parents=True, exist_ok=True)

            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, default=str)

            logger.info("Generation report written", path=str(report_path))
            return report_path

        except Exception as e:
            logger.error("Failed to write report", root=str(root), error=str(e))
            raise
