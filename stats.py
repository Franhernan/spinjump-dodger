import json
from pathlib import Path

STATS_FILE = Path(__file__).parent / "stats.json"
LEGACY_HIGHSCORE_FILE = Path(__file__).parent / "highscore.json"

DEFAULT_STATS = {
    "high_scores": {"easy": 0, "normal": 0, "hard": 0},
    "games_played": 0,
    "best_combo": 0,
    "recent_runs": [],
}


def _migrate_legacy_score():
    if not LEGACY_HIGHSCORE_FILE.exists():
        return 0

    try:
        with LEGACY_HIGHSCORE_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
        return int(data.get("high_score", 0))
    except (json.JSONDecodeError, OSError, TypeError, ValueError):
        return 0


def load_stats():
    if not STATS_FILE.exists():
        stats = json.loads(json.dumps(DEFAULT_STATS))
        legacy_score = _migrate_legacy_score()
        if legacy_score > 0:
            stats["high_scores"]["normal"] = legacy_score
        return stats

    try:
        with STATS_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (json.JSONDecodeError, OSError):
        return json.loads(json.dumps(DEFAULT_STATS))

    stats = json.loads(json.dumps(DEFAULT_STATS))
    stats["high_scores"].update(data.get("high_scores", {}))
    stats["games_played"] = int(data.get("games_played", 0))
    stats["best_combo"] = int(data.get("best_combo", 0))
    stats["recent_runs"] = list(data.get("recent_runs", []))[:5]
    return stats


def save_stats(stats):
    with STATS_FILE.open("w", encoding="utf-8") as file:
        json.dump(stats, file, indent=2)


def get_high_score(stats, difficulty):
    return int(stats["high_scores"].get(difficulty, 0))


def record_game_end(stats, difficulty, score, level, best_combo):
    stats["games_played"] = int(stats.get("games_played", 0)) + 1
    stats["best_combo"] = max(int(stats.get("best_combo", 0)), int(best_combo))

    current_best = get_high_score(stats, difficulty)
    if score > current_best:
        stats["high_scores"][difficulty] = int(score)

    recent_runs = list(stats.get("recent_runs", []))
    recent_runs.append(
        {
            "score": int(score),
            "difficulty": difficulty,
            "level": int(level),
        }
    )
    recent_runs.sort(key=lambda run: run["score"], reverse=True)
    stats["recent_runs"] = recent_runs[:5]
    save_stats(stats)
    return score > current_best