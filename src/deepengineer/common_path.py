from pathlib import Path
import os

def is_on_spaces():
    return "SPACE_ID" in os.environ or "HF_SPACE_ID" in os.environ


DEEPENGINEER_CODE_DIR = Path(__file__).parent
DEEPENGINEER_SRC_DIR = DEEPENGINEER_CODE_DIR.parent
DEEPENGINEER_ROOT_DIR = DEEPENGINEER_SRC_DIR.parent

assert DEEPENGINEER_CODE_DIR.name == "deepengineer"
assert DEEPENGINEER_SRC_DIR.name == "src"

if is_on_spaces():
    DATA_DIR = Path("/data")
else:
    DATA_DIR = DEEPENGINEER_ROOT_DIR / "data"

assert DATA_DIR.exists()