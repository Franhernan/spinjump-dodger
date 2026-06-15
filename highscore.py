from stats import get_high_score, load_stats, save_stats


def load_high_score():
    stats = load_stats()
    return max(get_high_score(stats, key) for key in ("easy", "normal", "hard"))


def save_high_score(score):
    stats = load_stats()
    stats["high_scores"]["normal"] = max(get_high_score(stats, "normal"), int(score))
    save_stats(stats)