"""Python metadata provider using AST parsing."""

import ast
from typing import List
from pathlib import Path
from platform.ports.providers import MetadataProvider
from platform.domain.models.metadata import FileMetadata
from platform.kernel.logging import get_logger

logger = get_logger(__name__)


class PythonMetadataProvider:
    """Python metadata extraction using AST parsing."""

    language = "python"
    extensions = {".py", ".pyi"}

    def parse_file(self, path: Path, content: str) -> FileMetadata:
        """Parse a Python file and extract metadata."""
        try:
            # Parse AST
            tree = ast.parse(content, filename=str(path))

            # Extract metadata
            functions = []
            classes = []
            imports = []

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                elif isinstance(node, ast.AsyncFunctionDef):
                    functions.append(f"async {node.name}")
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        imports.append(f"{module}.{alias.name}")

            # Count lines of code (excluding empty lines and comments)
            lines = content.split("\n")
            loc = sum(1 for line in lines if line.strip() and not line.strip().startswith("#"))

            metadata = FileMetadata(
                path=str(path),
                language=self.language,
                loc=loc,
                functions=functions,
                classes=classes,
                imports=imports,
            )

            logger.debug(
                "Parsed Python file",
                path=str(path),
                functions=len(functions),
                classes=len(classes),
                imports=len(imports),
                loc=loc,
            )

            return metadata

        except SyntaxError as e:
            logger.warning("Syntax error in Python file", path=str(path), error=str(e))
            # Return basic metadata even if parsing fails
            return FileMetadata(
                path=str(path),
                language=self.language,
                loc=len(content.split("\n")),
                functions=[],
                classes=[],
                imports=[],
            )
        except Exception as e:
            logger.error("Failed to parse Python file", path=str(path), error=str(e))
            raise

    def can_handle(self, file_path: Path) -> bool:
        """Check if this provider can handle the given file."""
        return file_path.suffix in self.extensions
