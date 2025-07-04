from pathlib import Path

DEEPENGINEER_CODE_DIR = Path(__file__).parent
DEEPENGINEER_SRC_DIR = DEEPENGINEER_CODE_DIR.parent
DEEPENGINEER_ROOT_DIR = DEEPENGINEER_SRC_DIR.parent

assert DEEPENGINEER_CODE_DIR.name == "deepengineer"
assert DEEPENGINEER_SRC_DIR.name == "src"

DATA_DIR = DEEPENGINEER_ROOT_DIR / "data"
assert DATA_DIR.exists()