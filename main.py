import math
import random
import sys

import pygame

from highscore import load_high_score, save_high_score
from sounds import SoundManager

pygame.init()

WIDTH, HEIGHT = 800, 600
CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT // 2
FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 60, 60)
ORANGE = (255, 140, 40)
PURPLE = (180, 80, 255)
BLUE = (60, 140, 255)
GREEN = (40, 200, 90)
YELLOW = (255, 220, 80)
DARK_GREEN = (20, 120, 50)
CYAN = (80, 220, 255)
OVERLAY = (0, 0, 0, 170)

PLATFORM_RADIUS = 130
PLAYER_RADIUS = 18
PLAYER_ORBIT_RADIUS = 118
OBSTACLE_SPAWN_RADIUS = 320
OBSTACLE_DESPAWN_RADIUS = 40

GRAVITY = 0.55
JUMP_VELOCITY = -11
MOVE_SPEED = 4.5
MAX_FALL_RADIUS = 230
COMBO_WINDOW = 120
MAX_COMBO_MULTIPLIER = 5


class Particle:
    def __init__(self, x, y, color):
        angle = random.uniform(0, math.tau)
        speed = random.uniform(1.5, 4.5)
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.color = color
        self.life = random.randint(18, 30)
        self.radius = random.randint(2, 4)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.08
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)


class Player:
    def __init__(self):
        self.angle = 0.0
        self.radius = PLAYER_ORBIT_RADIUS
        self.radial_velocity = 0.0
        self.on_platform = True
        self.score = 0
        self.was_on_platform = True

    def update(self, rotation_speed):
        self.was_on_platform = self.on_platform

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
            return True
        return False

    def just_landed(self):
        return self.on_platform and not self.was_on_platform

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
    kind = "normal"
    color = RED
    radius = 14
    points = 10

    def __init__(self, angle, speed):
        self.angle = angle
        self.radius = OBSTACLE_SPAWN_RADIUS
        self.speed = speed

    def update(self):
        self.radius -= self.speed

    def effective_angle(self):
        return self.angle

    def get_pos(self):
        radians = math.radians(self.effective_angle())
        x = CENTER_X + self.radius * math.cos(radians)
        y = CENTER_Y + self.radius * math.sin(radians)
        return x, y

    def draw(self, surface):
        x, y = self.get_pos()
        pygame.draw.circle(surface, self.color, (int(x), int(y)), self.radius)

    def is_cleared(self):
        return self.radius < OBSTACLE_DESPAWN_RADIUS


class FastObstacle(Obstacle):
    kind = "fast"
    color = ORANGE
    radius = 10
    points = 15

    def __init__(self, angle, speed):
        super().__init__(angle, speed * 1.45)


class ZigzagObstacle(Obstacle):
    kind = "zigzag"
    color = PURPLE
    radius = 13
    points = 20

    def __init__(self, angle, speed):
        super().__init__(angle, speed)
        self.wobble_speed = random.uniform(3.0, 6.0)
        self.wobble_amount = random.uniform(8.0, 15.0)
        self.time = 0.0

    def update(self):
        super().update()
        self.time += 1.0

    def effective_angle(self):
        wobble = self.wobble_amount * math.sin(math.radians(self.time * self.wobble_speed))
        return self.angle + wobble

    def draw(self, surface):
        x, y = self.get_pos()
        pygame.draw.circle(surface, self.color, (int(x), int(y)), self.radius)
        pygame.draw.circle(surface, WHITE, (int(x), int(y)), self.radius, 2)


def create_obstacle(level):
    angle = random.uniform(0, 360)
    speed = 2.5 + level * 0.45

    roll = random.random()
    if level >= 3 and roll < 0.2:
        return ZigzagObstacle(angle, speed)
    if level >= 2 and roll < 0.45:
        return FastObstacle(angle, speed)
    return Obstacle(angle, speed)


def draw_platform(surface, rotation_angle):
    pygame.draw.circle(surface, DARK_GREEN, (CENTER_X, CENTER_Y), PLATFORM_RADIUS + 8)
    pygame.draw.circle(surface, GREEN, (CENTER_X, CENTER_Y), PLATFORM_RADIUS, 18)

    for index in range(8):
        marker_angle = math.radians(rotation_angle + index * 45)
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
    return distance < PLAYER_RADIUS + obstacle.radius


def draw_centered_text(surface, font, text, color, y, shake_x=0):
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(center=(WIDTH // 2 + shake_x, y))
    surface.blit(rendered, rect)


def spawn_particles(particles, x, y, color, count=10):
    for _ in range(count):
        particles.append(Particle(x, y, color))


def combo_multiplier(combo_count):
    return min(MAX_COMBO_MULTIPLIER, 1 + combo_count // 3)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("SpinJump Dodger")
        self.clock = pygame.time.Clock()
        self.title_font = pygame.font.SysFont(None, 64)
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 28)
        self.sounds = SoundManager()
        self.high_score = load_high_score()
        self.overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.reset()

    def reset(self):
        self.player = Player()
        self.obstacles = []
        self.demo_obstacles = []
        self.particles = []
        self.rotation_speed = 1.8
        self.platform_angle = 0.0
        self.level = 1
        self.spawn_timer = 0
        self.demo_spawn_timer = 0
        self.game_over = False
        self.started = False
        self.paused = False
        self.level_banner_timer = 0
        self.death_shake_timer = 0
        self.new_high_score = False
        self.title_timer = 0
        self.combo_count = 0
        self.combo_timer = 0
        self.combo_banner_timer = 0
        self.combo_banner_text = ""

    def spawn_obstacle(self):
        self.obstacles.append(create_obstacle(self.level))

    def spawn_demo_obstacle(self):
        angle = random.uniform(0, 360)
        speed = random.uniform(2.0, 3.5)
        choices = [Obstacle, FastObstacle, ZigzagObstacle]
        obstacle_class = random.choice(choices)
        self.demo_obstacles.append(obstacle_class(angle, speed))

    def register_dodge(self, obstacle):
        self.combo_count += 1
        self.combo_timer = COMBO_WINDOW
        multiplier = combo_multiplier(self.combo_count)
        points = obstacle.points * multiplier
        self.player.score += points

        if self.combo_count % 3 == 0:
            self.combo_banner_timer = 60
            self.combo_banner_text = f"x{multiplier} COMBO!"
            self.sounds.play(self.sounds.combo)

        self.sounds.play(self.sounds.score)
        ox, oy = obstacle.get_pos()
        spawn_particles(self.particles, ox, oy, obstacle.color, count=8 + multiplier)

    def end_game(self):
        if self.game_over:
            return

        self.game_over = True
        self.death_shake_timer = 24
        self.combo_count = 0
        self.combo_timer = 0
        self.sounds.play(self.sounds.game_over)

        px, py = self.player.get_pos()
        spawn_particles(self.particles, px, py, RED, count=18)

        if self.player.score > self.high_score:
            self.high_score = self.player.score
            save_high_score(self.high_score)
            self.new_high_score = True

    def toggle_pause(self):
        if self.started and not self.game_over:
            self.paused = not self.paused
            self.sounds.play(self.sounds.pause)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if not self.started and event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    self.started = True
                    self.demo_obstacles.clear()
                elif self.started and not self.game_over:
                    if event.key in (pygame.K_p, pygame.K_ESCAPE):
                        self.toggle_pause()
                    elif not self.paused:
                        if event.key in (pygame.K_SPACE, pygame.K_UP):
                            if self.player.jump():
                                self.sounds.play(self.sounds.jump)
                        elif event.key == pygame.K_LEFT:
                            self.player.move(-1)
                        elif event.key == pygame.K_RIGHT:
                            self.player.move(1)
                elif self.game_over and event.key == pygame.K_r:
                    self.reset()
                    self.started = True

    def update_particles_and_timers(self):
        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)

        if self.level_banner_timer > 0:
            self.level_banner_timer -= 1

        if self.death_shake_timer > 0:
            self.death_shake_timer -= 1

        if self.combo_banner_timer > 0:
            self.combo_banner_timer -= 1

        self.title_timer += 1

    def update_title_demo(self):
        self.platform_angle = (self.platform_angle + 1.2) % 360
        self.demo_spawn_timer += 1
        if self.demo_spawn_timer >= 45:
            self.spawn_demo_obstacle()
            self.demo_spawn_timer = 0

        for obstacle in self.demo_obstacles[:]:
            obstacle.update()
            if obstacle.is_cleared():
                self.demo_obstacles.remove(obstacle)

    def update_gameplay(self):
        if self.combo_timer > 0:
            self.combo_timer -= 1
            if self.combo_timer == 0:
                self.combo_count = 0

        self.platform_angle = (self.platform_angle + self.rotation_speed) % 360
        self.player.update(self.rotation_speed)

        if self.player.just_landed():
            self.sounds.play(self.sounds.land)

        self.spawn_timer += 1
        spawn_interval = max(20, 55 - self.level * 4)
        if self.spawn_timer >= spawn_interval:
            self.spawn_obstacle()
            self.spawn_timer = 0

        for obstacle in self.obstacles[:]:
            obstacle.update()
            if obstacle.is_cleared():
                self.obstacles.remove(obstacle)
                self.register_dodge(obstacle)
            elif check_collision(self.player, obstacle):
                self.end_game()
                return

        if self.player.has_fallen():
            self.end_game()
            return

        next_level_threshold = self.level * 200
        if self.player.score >= next_level_threshold:
            self.level += 1
            self.rotation_speed += 0.25
            self.level_banner_timer = 90
            self.sounds.play(self.sounds.level_up)

    def update(self):
        self.update_particles_and_timers()

        if self.game_over:
            return

        if not self.started:
            self.update_title_demo()
            return

        if self.paused:
            return

        self.update_gameplay()

    def shake_offset(self):
        if self.death_shake_timer <= 0:
            return 0
        return random.randint(-4, 4)

    def title_color(self):
        pulse = (math.sin(self.title_timer * 0.08) + 1) / 2
        red = int(200 + 55 * pulse)
        green = int(160 + 60 * pulse)
        blue = int(40 + 40 * (1 - pulse))
        return red, green, blue

    def title_bounce_y(self, base_y):
        return base_y + int(math.sin(self.title_timer * 0.1) * 8)

    def draw_world(self):
        draw_platform(self.screen, self.platform_angle)

        active_obstacles = self.demo_obstacles if not self.started else self.obstacles
        for obstacle in active_obstacles:
            obstacle.draw(self.screen)

        if self.started:
            self.player.draw(self.screen)

        for particle in self.particles:
            particle.draw(self.screen)

    def draw_hud(self):
        multiplier = combo_multiplier(self.combo_count) if self.combo_count > 0 else 1
        combo_text = f"   Combo: x{multiplier}" if self.combo_count > 0 else ""
        hud = self.font.render(
            f"Score: {self.player.score}   Level: {self.level}   Best: {self.high_score}{combo_text}",
            True,
            WHITE,
        )
        self.screen.blit(hud, (12, 12))

        if self.started and not self.game_over:
            controls = self.small_font.render(
                "SPACE/UP: Jump   LEFT/RIGHT: Move   P: Pause",
                True,
                WHITE,
            )
            self.screen.blit(controls, (12, HEIGHT - 34))

    def draw_pause_overlay(self):
        self.overlay.fill(OVERLAY)
        self.screen.blit(self.overlay, (0, 0))
        draw_centered_text(self.screen, self.title_font, "PAUSED", WHITE, HEIGHT // 2 - 20)
        draw_centered_text(
            self.screen,
            self.small_font,
            "Press P or ESC to Resume",
            CYAN,
            HEIGHT // 2 + 30,
        )

    def draw(self):
        self.screen.fill(BLACK)
        shake = self.shake_offset()
        self.draw_world()
        self.draw_hud()

        if not self.started:
            draw_centered_text(
                self.screen,
                self.title_font,
                "SpinJump Dodger",
                self.title_color(),
                self.title_bounce_y(HEIGHT // 2 - 80),
            )
            draw_centered_text(
                self.screen,
                self.font,
                "Press SPACE to Start",
                WHITE,
                HEIGHT // 2,
            )
            draw_centered_text(
                self.screen,
                self.small_font,
                f"High Score: {self.high_score}",
                CYAN,
                HEIGHT // 2 + 45,
            )
            self._draw_obstacle_legend()
        elif self.game_over:
            draw_centered_text(self.screen, self.title_font, "GAME OVER", RED, HEIGHT // 2 - 50, shake)
            draw_centered_text(
                self.screen,
                self.font,
                f"Final Score: {self.player.score}",
                WHITE,
                HEIGHT // 2,
                shake,
            )
            if self.new_high_score:
                draw_centered_text(
                    self.screen,
                    self.small_font,
                    "NEW HIGH SCORE!",
                    YELLOW,
                    HEIGHT // 2 + 40,
                    shake,
                )
            draw_centered_text(
                self.screen,
                self.small_font,
                "Press R to Restart",
                WHITE,
                HEIGHT // 2 + 80,
                shake,
            )
        elif self.level_banner_timer > 0:
            draw_centered_text(
                self.screen,
                self.title_font,
                f"LEVEL {self.level}!",
                YELLOW,
                HEIGHT // 2 - 20,
            )

        if self.combo_banner_timer > 0 and self.started and not self.game_over:
            draw_centered_text(
                self.screen,
                self.font,
                self.combo_banner_text,
                CYAN,
                HEIGHT // 2 + 50,
            )

        if self.paused:
            self.draw_pause_overlay()

        pygame.display.flip()

    def _draw_obstacle_legend(self):
        legend_y = HEIGHT // 2 + 95
        entries = [
            (RED, "Red: standard"),
            (ORANGE, "Orange: fast"),
            (PURPLE, "Purple: zigzag"),
        ]
        for index, (color, label) in enumerate(entries):
            x = WIDTH // 2 - 150 + index * 155
            pygame.draw.circle(self.screen, color, (x, legend_y), 8)
            text = self.small_font.render(label, True, WHITE)
            self.screen.blit(text, (x + 14, legend_y - 10))

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