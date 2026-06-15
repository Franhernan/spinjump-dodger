"""Quick smoke test to verify SpinJump Dodger runs without errors."""

import sys

import pygame

from difficulty import DIFFICULTIES
from main import Game, create_obstacle, combo_multiplier
from powerups import PowerUp, random_powerup_kind
from stats import load_stats, record_game_end


def test_imports_and_init():
    pygame.init()
    game = Game()
    assert game.difficulty_key == "normal"
    assert game.difficulty["name"] == "Normal"
    assert game.best_for_difficulty >= 0
    pygame.quit()
    print("PASS: Game initializes")


def test_obstacles_and_combos():
    obstacle = create_obstacle(level=3, speed_mod=1.0)
    assert obstacle.points >= 10
    assert combo_multiplier(0) == 1
    assert combo_multiplier(6) == 3
    print("PASS: Obstacles and combo math")


def test_powerups():
    kind = random_powerup_kind()
    assert kind in ("shield", "slow", "boost")
    powerup = PowerUp(kind, 45, 400, 300, 118)
    x, y = powerup.get_pos()
    assert 0 <= x <= 800
    assert 0 <= y <= 600
    print("PASS: Power-ups")


def test_stats():
    stats = load_stats()
    assert "high_scores" in stats
    for key in DIFFICULTIES:
        assert key in stats["high_scores"]
    print("PASS: Stats load")


def test_simulated_frames():
    pygame.init()
    pygame.display.set_mode((800, 600))
    game = Game()
    game.started = True
    game.shield_charges = 5

    for _ in range(120):
        pygame.event.pump()
        game.update()
        game.draw()

    assert game.level >= 1
    assert game.player.score >= 0
    pygame.quit()
    print("PASS: 120 simulated frames")


def main():
    tests = [
        test_imports_and_init,
        test_obstacles_and_combos,
        test_powerups,
        test_stats,
        test_simulated_frames,
    ]

    for test in tests:
        test()

    print("\nAll tests passed. Run 'python main.py' to play the game.")
    return 0


if __name__ == "__main__":
    sys.exit(main())