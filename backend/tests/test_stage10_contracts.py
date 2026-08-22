import ast
from pathlib import Path

def test_production_files_exist():
    root = Path(__file__).parents[1]
    assert (root / "Dockerfile").exists()
    assert (root.parent / "render.yaml").exists()

def test_python_sources_parse():
    root = Path(__file__).parents[1] / "app"
    for path in root.rglob("*.py"):
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
