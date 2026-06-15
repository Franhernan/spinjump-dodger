import json
from pathlib import Path

HIGHSCORE_FILE = Path(__file__).parent / "highscore.json"


def load_high_score():
    if not HIGHSCORE_FILE.exists():
        return 0

    try:
        with HIGHSCORE_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
        return int(data.get("high_score", 0))
    except (json.JSONDecodeError, OSError, TypeError, ValueError):
        return 0


def save_high_score(score):
    with HIGHSCORE_FILE.open("w", encoding="utf-8") as file:
        json.dump({"high_score": int(score)}, file)