DIFFICULTIES = {
    "easy": {
        "name": "Easy",
        "rotation_speed": 1.4,
        "spawn_interval_mod": 1.3,
        "obstacle_speed_mod": 0.85,
        "level_speed_gain": 0.18,
        "color": (80, 220, 120),
    },
    "normal": {
        "name": "Normal",
        "rotation_speed": 1.8,
        "spawn_interval_mod": 1.0,
        "obstacle_speed_mod": 1.0,
        "level_speed_gain": 0.25,
        "color": (80, 220, 255),
    },
    "hard": {
        "name": "Hard",
        "rotation_speed": 2.4,
        "spawn_interval_mod": 0.72,
        "obstacle_speed_mod": 1.25,
        "level_speed_gain": 0.32,
        "color": (255, 90, 90),
    },
}

DIFFICULTY_ORDER = ["easy", "normal", "hard"]


def cycle_difficulty(current_key, direction):
    index = DIFFICULTY_ORDER.index(current_key)
    index = (index + direction) % len(DIFFICULTY_ORDER)
    return DIFFICULTY_ORDER[index]