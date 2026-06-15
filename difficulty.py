OBSTACLE_BASE_SPEED = 1.4
OBSTACLE_SPEED_PER_LEVEL = 0.14
OBSTACLE_MAX_SPEED = 3.8

DIFFICULTIES = {
    "easy": {
        "name": "Easy",
        "rotation_speed": 1.1,
        "spawn_interval_mod": 1.4,
        "obstacle_speed_mod": 0.72,
        "level_speed_gain": 0.1,
        "color": (80, 220, 120),
    },
    "normal": {
        "name": "Normal",
        "rotation_speed": 1.4,
        "spawn_interval_mod": 1.15,
        "obstacle_speed_mod": 0.88,
        "level_speed_gain": 0.14,
        "color": (80, 220, 255),
    },
    "hard": {
        "name": "Hard",
        "rotation_speed": 1.8,
        "spawn_interval_mod": 0.9,
        "obstacle_speed_mod": 1.05,
        "level_speed_gain": 0.18,
        "color": (255, 90, 90),
    },
}


def obstacle_speed_for_level(level, speed_mod):
    speed = OBSTACLE_BASE_SPEED + (level - 1) * OBSTACLE_SPEED_PER_LEVEL
    return min(speed, OBSTACLE_MAX_SPEED) * speed_mod

DIFFICULTY_ORDER = ["easy", "normal", "hard"]


def cycle_difficulty(current_key, direction):
    index = DIFFICULTY_ORDER.index(current_key)
    index = (index + direction) % len(DIFFICULTY_ORDER)
    return DIFFICULTY_ORDER[index]