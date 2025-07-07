import sys, pathlib

# Add the repo root (one level up from tests/) to sys.path
root = pathlib.Path(__file__).resolve().parents[1]
if str(root) not in sys.path:
    sys.path.insert(0, str(root)) 