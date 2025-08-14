from pathlib import Path
from typing import Iterable

class LocalFileSystem:
    def read_text(self, path: Path) -> str:
        return path.read_text(encoding="utf-8")

    def scan(self, root: Path, include_exts: set[str]) -> list[Path]:
        paths: list[Path] = []
        for p in root.rglob("*"):
            if p.is_file() and (not include_exts or p.suffix in include_exts):
                paths.append(p)
        return paths

class SimpleArtifactWriter:
    def write(self, root: Path, files: list):
        root.mkdir(parents=True, exist_ok=True)
        for f in files:
            dest = root / f.path
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(f.content, encoding="utf-8")
