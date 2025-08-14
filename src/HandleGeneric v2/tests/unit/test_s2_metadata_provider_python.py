from platform.kernel.di import build_app
from pathlib import Path

def test_python_metadata_provider(tmp_path):
    p = tmp_path / "m.py"
    p.write_text("import os\n\nclass A: ...\n\ndef f():\n  return 1\n")
    sv = build_app()
    report = sv.s2_usecases.generate_metadata(str(tmp_path))
    assert report.files
    assert report.languages == ["python"]
