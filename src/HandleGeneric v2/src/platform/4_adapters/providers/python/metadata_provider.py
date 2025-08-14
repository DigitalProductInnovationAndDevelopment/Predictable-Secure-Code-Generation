import ast, os
from pathlib import Path
from platform.domain.models.metadata import FileMetadata

class PythonMetadataProvider:
    language = "python"
    extensions = {".py"}

    def parse_file(self, path: Path, content: str) -> FileMetadata:
        tree = ast.parse(content)
        funcs, classes, imports = [], [], []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                funcs.append(node.name)
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(getattr(node, "module", None) or "import")
        loc = len(content.splitlines())
        return FileMetadata(path=str(path), language=self.language, loc=loc,
                            functions=funcs, classes=classes, imports=imports)
