from pathlib import Path
from platform.domain.models.metadata import ProjectMetadata

def run_pipeline(services, root: str, lang: str = "python") -> ProjectMetadata:
    provider = services.providers.get_metadata(lang)
    exts = provider.extensions
    paths = services.fs.scan(Path(root), exts)
    metas = []
    for p in paths:
        content = services.fs.read_text(p)
        metas.append(provider.parse_file(p, content))
    languages = sorted(set(m.language for m in metas))
    return ProjectMetadata(files=metas, languages=languages)
