import math
import random
import sys

import pygame

pygame.init()

WIDTH, HEIGHT = 800, 600
CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT // 2
FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 60, 60)
BLUE = (60, 140, 255)
GREEN = (40, 200, 90)
YELLOW = (255, 220, 80)
DARK_GREEN = (20, 120, 50)

PLATFORM_RADIUS = 130
PLAYER_RADIUS = 18
OBSTACLE_RADIUS = 14
PLAYER_ORBIT_RADIUS = 118
OBSTACLE_SPAWN_RADIUS = 320
OBSTACLE_DESPAWN_RADIUS = 40

GRAVITY = 0.55
JUMP_VELOCITY = -11
MOVE_SPEED = 4.5
MAX_FALL_RADIUS = 230


class Player:
    def __init__(self):
        self.angle = 0.0
        self.radius = PLAYER_ORBIT_RADIUS
        self.radial_velocity = 0.0
        self.on_platform = True
        self.score = 0

    def update(self, rotation_speed):
        if self.on_platform:
            self.angle = (self.angle + rotation_speed) % 360
            self.radius = PLAYER_ORBIT_RADIUS
            self.radial_velocity = 0.0
        else:
            self.radial_velocity += GRAVITY
            self.radius += self.radial_velocity
            if self.radius <= PLAYER_ORBIT_RADIUS:
                self.radius = PLAYER_ORBIT_RADIUS
                self.radial_velocity = 0.0
                self.on_platform = True

    def jump(self):
        if self.on_platform:
            self.on_platform = False
            self.radial_velocity = JUMP_VELOCITY

    def move(self, direction):
        if self.on_platform:
            self.angle = (self.angle + direction * MOVE_SPEED) % 360

    def get_pos(self):
        radians = math.radians(self.angle)
        x = CENTER_X + self.radius * math.cos(radians)
        y = CENTER_Y + self.radius * math.sin(radians)
        return x, y

    def draw(self, surface):
        x, y = self.get_pos()
        pygame.draw.circle(surface, BLUE, (int(x), int(y)), PLAYER_RADIUS)
        eye_offset = 6
        pygame.draw.circle(surface, WHITE, (int(x + eye_offset), int(y - 4)), 4)
        pygame.draw.circle(surface, BLACK, (int(x + eye_offset + 1), int(y - 4)), 2)

    def has_fallen(self):
        return not self.on_platform and self.radius > MAX_FALL_RADIUS


class Obstacle:
    def __init__(self, angle, speed):
        self.angle = angle
        self.radius = OBSTACLE_SPAWN_RADIUS
        self.speed = speed

    def update(self):
        self.radius -= self.speed

    def get_pos(self):
        radians = math.radians(self.angle)
        x = CENTER_X + self.radius * math.cos(radians)
        y = CENTER_Y + self.radius * math.sin(radians)
        return x, y

    def draw(self, surface):
        x, y = self.get_pos()
        pygame.draw.circle(surface, RED, (int(x), int(y)), OBSTACLE_RADIUS)

    def is_cleared(self):
        return self.radius < OBSTACLE_DESPAWN_RADIUS


def draw_platform(surface, rotation_angle):
    pygame.draw.circle(surface, DARK_GREEN, (CENTER_X, CENTER_Y), PLATFORM_RADIUS + 8)
    pygame.draw.circle(surface, GREEN, (CENTER_X, CENTER_Y), PLATFORM_RADIUS, 18)

    for i in range(8):
        marker_angle = math.radians(rotation_angle + i * 45)
        inner = PLATFORM_RADIUS - 12
        outer = PLATFORM_RADIUS + 12
        x1 = CENTER_X + inner * math.cos(marker_angle)
        y1 = CENTER_Y + inner * math.sin(marker_angle)
        x2 = CENTER_X + outer * math.cos(marker_angle)
        y2 = CENTER_Y + outer * math.sin(marker_angle)
        pygame.draw.line(surface, YELLOW, (x1, y1), (x2, y2), 3)


def check_collision(player, obstacle):
    px, py = player.get_pos()
    ox, oy = obstacle.get_pos()
    distance = math.hypot(px - ox, py - oy)
    return distance < PLAYER_RADIUS + OBSTACLE_RADIUS


def draw_centered_text(surface, font, text, color, y):
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(center=(WIDTH // 2, y))
    surface.blit(rendered, rect)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("SpinJump Dodger")
        self.clock = pygame.time.Clock()
        self.title_font = pygame.font.SysFont(None, 64)
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 28)
        self.reset()

    def reset(self):
        self.player = Player()
        self.obstacles = []
        self.rotation_speed = 1.8
        self.platform_angle = 0.0
        self.level = 1
        self.spawn_timer = 0
        self.game_over = False
        self.started = False

    def spawn_obstacle(self):
        angle = random.uniform(0, 360)
        speed = 2.5 + self.level * 0.45
        self.obstacles.append(Obstacle(angle, speed))

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if not self.started and event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    self.started = True
                elif self.game_over and event.key == pygame.K_r:
                    self.reset()
                    self.started = True

        if not self.started or self.game_over:
            return

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] or keys[pygame.K_UP]:
            self.player.jump()
        if keys[pygame.K_LEFT]:
            self.player.move(-1)
        if keys[pygame.K_RIGHT]:
            self.player.move(1)

    def update(self):
        if not self.started or self.game_over:
            return

        self.platform_angle = (self.platform_angle + self.rotation_speed) % 360
        self.player.update(self.rotation_speed)

        self.spawn_timer += 1
        spawn_interval = max(20, 55 - self.level * 4)
        if self.spawn_timer >= spawn_interval:
            self.spawn_obstacle()
            self.spawn_timer = 0

        for obstacle in self.obstacles[:]:
            obstacle.update()
            if obstacle.is_cleared():
                self.obstacles.remove(obstacle)
                self.player.score += 10
            elif check_collision(self.player, obstacle):
                self.game_over = True

        if self.player.has_fallen():
            self.game_over = True

        next_level_threshold = self.level * 200
        if self.player.score >= next_level_threshold:
            self.level += 1
            self.rotation_speed += 0.25

    def draw(self):
        self.screen.fill(BLACK)
        draw_platform(self.screen, self.platform_angle)

        for obstacle in self.obstacles:
            obstacle.draw(self.screen)

        self.player.draw(self.screen)

        hud = self.font.render(
            f"Score: {self.player.score}   Level: {self.level}",
            True,
            WHITE,
        )
        self.screen.blit(hud, (12, 12))

        controls = self.small_font.render(
            "SPACE/UP: Jump   LEFT/RIGHT: Move",
            True,
            WHITE,
        )
        self.screen.blit(controls, (12, HEIGHT - 34))

        if not self.started:
            draw_centered_text(self.screen, self.title_font, "SpinJump Dodger", YELLOW, HEIGHT // 2 - 60)
            draw_centered_text(
                self.screen,
                self.font,
                "Press SPACE to Start",
                WHITE,
                HEIGHT // 2 + 10,
            )
        elif self.game_over:
            draw_centered_text(self.screen, self.title_font, "GAME OVER", RED, HEIGHT // 2 - 30)
            draw_centered_text(
                self.screen,
                self.font,
                f"Final Score: {self.player.score}",
                WHITE,
                HEIGHT // 2 + 20,
            )
            draw_centered_text(
                self.screen,
                self.small_font,
                "Press R to Restart",
                WHITE,
                HEIGHT // 2 + 60,
            )

        pygame.display.flip()

    def run(self):
        while True:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()