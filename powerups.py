import math
import random

import pygame

POWERUP_RADIUS = 12
POWERUP_LIFETIME = 420

POWERUP_TYPES = {
    "shield": {
        "color": (80, 220, 255),
        "label": "Shield",
        "duration": 0,
    },
    "slow": {
        "color": (255, 120, 220),
        "label": "Slow-Mo",
        "duration": 300,
    },
    "boost": {
        "color": (255, 215, 60),
        "label": "2x Score",
        "duration": 480,
    },
}


class PowerUp:
    def __init__(self, kind, angle, center_x, center_y, orbit_radius):
        self.kind = kind
        self.angle = angle
        self.center_x = center_x
        self.center_y = center_y
        self.orbit_radius = orbit_radius
        self.lifetime = POWERUP_LIFETIME
        self.pulse = random.uniform(0, math.tau)
        self.info = POWERUP_TYPES[kind]

    def update(self):
        self.lifetime -= 1
        self.pulse += 0.12

    def expired(self):
        return self.lifetime <= 0

    def get_pos(self):
        radians = math.radians(self.angle)
        x = self.center_x + self.orbit_radius * math.cos(radians)
        y = self.center_y + self.orbit_radius * math.sin(radians)
        return x, y

    def draw(self, surface):
        x, y = self.get_pos()
        pulse_radius = POWERUP_RADIUS + int(math.sin(self.pulse) * 2)
        pygame.draw.circle(surface, self.info["color"], (int(x), int(y)), pulse_radius + 3, 2)
        pygame.draw.circle(surface, self.info["color"], (int(x), int(y)), pulse_radius)

    def collides_with_player(self, player_x, player_y, player_radius):
        px, py = self.get_pos()
        distance = math.hypot(player_x - px, player_y - py)
        return distance < player_radius + POWERUP_RADIUS


def random_powerup_kind():
    return random.choice(list(POWERUP_TYPES.keys()))