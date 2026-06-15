import math
import random
import sys

import pygame

from difficulty import DIFFICULTIES, cycle_difficulty, obstacle_speed_for_level
from powerups import POWERUP_TYPES, PowerUp, random_powerup_kind
from stats import get_high_score, load_stats, record_game_end
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

GRAVITY = 0.48
JUMP_VELOCITY = 9
MOVE_SPEED = 4.5
MAX_FALL_RADIUS = 220
COMBO_WINDOW = 120
MAX_COMBO_MULTIPLIER = 5
MAX_SHIELD_CHARGES = 2
POWERUP_SPAWN_INTERVAL = 360


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
            self.radial_velocity -= GRAVITY
            self.radius += self.radial_velocity
            if self.radius <= PLAYER_ORBIT_RADIUS and self.radial_velocity <= 0:
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

    def draw(self, surface, shield_charges=0):
        x, y = self.get_pos()
        if not self.on_platform:
            shadow_radians = math.radians(self.angle)
            shadow_x = CENTER_X + PLAYER_ORBIT_RADIUS * math.cos(shadow_radians)
            shadow_y = CENTER_Y + PLAYER_ORBIT_RADIUS * math.sin(shadow_radians)
            pygame.draw.circle(surface, (30, 30, 30), (int(shadow_x), int(shadow_y)), 10)
        if shield_charges > 0:
            pygame.draw.circle(surface, CYAN, (int(x), int(y)), PLAYER_RADIUS + 8, 2)
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
        self.base_speed = speed
        self.speed = speed

    def update(self, speed_multiplier=1.0):
        self.speed = self.base_speed * speed_multiplier
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
        super().__init__(angle, speed * 1.22)


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

    def update(self, speed_multiplier=1.0):
        super().update(speed_multiplier)
        self.time += 1.0

    def effective_angle(self):
        wobble = self.wobble_amount * math.sin(math.radians(self.time * self.wobble_speed))
        return self.angle + wobble

    def draw(self, surface):
        x, y = self.get_pos()
        pygame.draw.circle(surface, self.color, (int(x), int(y)), self.radius)
        pygame.draw.circle(surface, WHITE, (int(x), int(y)), self.radius, 2)


def create_obstacle(level, speed_mod):
    angle = random.uniform(0, 360)
    speed = obstacle_speed_for_level(level, speed_mod)

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
        self.stats = load_stats()
        self.difficulty_key = "normal"
        self.show_stats_screen = False
        self.overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.reset()

    @property
    def difficulty(self):
        return DIFFICULTIES[self.difficulty_key]

    @property
    def best_for_difficulty(self):
        return get_high_score(self.stats, self.difficulty_key)

    def reset(self):
        self.player = Player()
        self.obstacles = []
        self.demo_obstacles = []
        self.powerups = []
        self.particles = []
        self.rotation_speed = self.difficulty["rotation_speed"]
        self.platform_angle = 0.0
        self.level = 1
        self.spawn_timer = 0
        self.demo_spawn_timer = 0
        self.powerup_spawn_timer = 0
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
        self.session_max_combo = 0
        self.shield_charges = 0
        self.slow_mo_timer = 0
        self.score_boost_timer = 0
        self.powerup_banner_timer = 0
        self.powerup_banner_text = ""

    def gameplay_speed_multiplier(self):
        return 0.45 if self.slow_mo_timer > 0 else 1.0

    def score_multiplier(self):
        multiplier = combo_multiplier(self.combo_count) if self.combo_count > 0 else 1
        if self.score_boost_timer > 0:
            multiplier *= 2
        return multiplier

    def spawn_obstacle(self):
        self.obstacles.append(create_obstacle(self.level, self.difficulty["obstacle_speed_mod"]))

    def spawn_demo_obstacle(self):
        angle = random.uniform(0, 360)
        speed = random.uniform(1.0, 1.8)
        choices = [Obstacle, FastObstacle, ZigzagObstacle]
        self.demo_obstacles.append(random.choice(choices)(angle, speed))

    def try_spawn_powerup(self):
        if len(self.powerups) >= 1:
            return

        self.powerups.append(
            PowerUp(
                random_powerup_kind(),
                random.uniform(0, 360),
                CENTER_X,
                CENTER_Y,
                PLAYER_ORBIT_RADIUS,
            )
        )

    def collect_powerup(self, powerup):
        info = POWERUP_TYPES[powerup.kind]
        self.powerup_banner_timer = 75
        self.powerup_banner_text = info["label"]
        self.sounds.play(self.sounds.powerup)

        if powerup.kind == "shield":
            self.shield_charges = min(MAX_SHIELD_CHARGES, self.shield_charges + 1)
        elif powerup.kind == "slow":
            self.slow_mo_timer = info["duration"]
        elif powerup.kind == "boost":
            self.score_boost_timer = info["duration"]

        px, py = powerup.get_pos()
        spawn_particles(self.particles, px, py, info["color"], count=14)

    def register_dodge(self, obstacle):
        self.combo_count += 1
        self.combo_timer = COMBO_WINDOW
        self.session_max_combo = max(self.session_max_combo, self.combo_count)
        multiplier = self.score_multiplier()
        points = obstacle.points * multiplier
        self.player.score += points

        if self.combo_count % 3 == 0:
            self.combo_banner_timer = 60
            self.combo_banner_text = f"x{combo_multiplier(self.combo_count)} COMBO!"
            self.sounds.play(self.sounds.combo)

        self.sounds.play(self.sounds.score)
        ox, oy = obstacle.get_pos()
        spawn_particles(self.particles, ox, oy, obstacle.color, count=8 + multiplier)

    def absorb_hit(self, obstacle):
        self.shield_charges -= 1
        self.obstacles.remove(obstacle)
        self.sounds.play(self.sounds.shield)
        ox, oy = obstacle.get_pos()
        spawn_particles(self.particles, ox, oy, CYAN, count=16)
        px, py = self.player.get_pos()
        spawn_particles(self.particles, px, py, CYAN, count=10)

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

        self.new_high_score = record_game_end(
            self.stats,
            self.difficulty_key,
            self.player.score,
            self.level,
            self.session_max_combo,
        )

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
                if not self.started:
                    if self.show_stats_screen and event.key in (pygame.K_TAB, pygame.K_ESCAPE):
                        self.show_stats_screen = False
                    elif self.show_stats_screen:
                        pass
                    elif event.key == pygame.K_TAB:
                        self.show_stats_screen = True
                    elif event.key == pygame.K_LEFT:
                        self.difficulty_key = cycle_difficulty(self.difficulty_key, -1)
                    elif event.key == pygame.K_RIGHT:
                        self.difficulty_key = cycle_difficulty(self.difficulty_key, 1)
                    elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                        keys = ["easy", "normal", "hard"]
                        index = event.key - pygame.K_1
                        if index < len(keys):
                            self.difficulty_key = keys[index]
                    elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
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

    def update_effect_timers(self):
        if self.slow_mo_timer > 0:
            self.slow_mo_timer -= 1
        if self.score_boost_timer > 0:
            self.score_boost_timer -= 1
        if self.powerup_banner_timer > 0:
            self.powerup_banner_timer -= 1

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
        self.update_effect_timers()

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

    def update_powerups(self):
        for powerup in self.powerups[:]:
            powerup.update()
            if powerup.expired():
                self.powerups.remove(powerup)
                continue

            px, py = self.player.get_pos()
            if powerup.collides_with_player(px, py, PLAYER_RADIUS):
                self.collect_powerup(powerup)
                self.powerups.remove(powerup)

    def update_gameplay(self):
        if self.combo_timer > 0:
            self.combo_timer -= 1
            if self.combo_timer == 0:
                self.combo_count = 0

        speed_multiplier = self.gameplay_speed_multiplier()
        rotation_speed = self.rotation_speed * (0.5 if self.slow_mo_timer > 0 else 1.0)

        self.platform_angle = (self.platform_angle + rotation_speed) % 360
        self.player.update(rotation_speed)

        if self.player.just_landed():
            self.sounds.play(self.sounds.land)

        self.spawn_timer += 1
        spawn_interval = max(40, int((80 - self.level * 2) * self.difficulty["spawn_interval_mod"]))
        if self.spawn_timer >= spawn_interval:
            self.spawn_obstacle()
            self.spawn_timer = 0

        self.powerup_spawn_timer += 1
        if self.powerup_spawn_timer >= POWERUP_SPAWN_INTERVAL:
            self.try_spawn_powerup()
            self.powerup_spawn_timer = 0

        self.update_powerups()

        for obstacle in self.obstacles[:]:
            obstacle.update(speed_multiplier)
            if obstacle.is_cleared():
                self.obstacles.remove(obstacle)
                self.register_dodge(obstacle)
            elif check_collision(self.player, obstacle):
                if self.shield_charges > 0:
                    self.absorb_hit(obstacle)
                else:
                    self.end_game()
                    return

        if self.player.has_fallen():
            self.end_game()
            return

        next_level_threshold = self.level * 200
        if self.player.score >= next_level_threshold:
            self.level += 1
            self.rotation_speed += self.difficulty["level_speed_gain"]
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
        base = self.difficulty["color"]
        return tuple(int(component * (0.75 + 0.25 * pulse)) for component in base)

    def title_bounce_y(self, base_y):
        return base_y + int(math.sin(self.title_timer * 0.1) * 8)

    def draw_world(self):
        draw_platform(self.screen, self.platform_angle)

        active_obstacles = self.demo_obstacles if not self.started else self.obstacles
        for obstacle in active_obstacles:
            obstacle.draw(self.screen)

        for powerup in self.powerups:
            powerup.draw(self.screen)

        if self.started:
            self.player.draw(self.screen, self.shield_charges)

        for particle in self.particles:
            particle.draw(self.screen)

    def draw_hud(self):
        multiplier = self.score_multiplier() if self.combo_count > 0 or self.score_boost_timer > 0 else 1
        extras = []
        if self.combo_count > 0:
            extras.append(f"Combo x{combo_multiplier(self.combo_count)}")
        if self.score_boost_timer > 0:
            extras.append("2x Boost")
        if self.slow_mo_timer > 0:
            extras.append("Slow-Mo")
        if self.shield_charges > 0:
            extras.append(f"Shield x{self.shield_charges}")

        extra_text = f"   {' | '.join(extras)}" if extras else ""
        hud = self.font.render(
            f"Score: {self.player.score}   Level: {self.level}   Best: {self.best_for_difficulty}{extra_text}",
            True,
            WHITE,
        )
        self.screen.blit(hud, (12, 12))

        if self.started and not self.game_over:
            controls = self.small_font.render(
                "SPACE/UP: Jump outward   LEFT/RIGHT: Move   P: Pause",
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

    def draw_stats_screen(self):
        self.overlay.fill((0, 0, 0, 210))
        self.screen.blit(self.overlay, (0, 0))
        draw_centered_text(self.screen, self.title_font, "STATS", YELLOW, 70)

        lines = [
            f"Games Played: {self.stats['games_played']}",
            f"Best Combo: {self.stats['best_combo']}",
            "",
            "High Scores",
            f"  Easy:   {get_high_score(self.stats, 'easy')}",
            f"  Normal: {get_high_score(self.stats, 'normal')}",
            f"  Hard:   {get_high_score(self.stats, 'hard')}",
            "",
            "Top Runs",
        ]

        recent_runs = self.stats.get("recent_runs", [])
        if recent_runs:
            for index, run in enumerate(recent_runs, start=1):
                difficulty_name = DIFFICULTIES[run["difficulty"]]["name"]
                lines.append(
                    f"  {index}. {run['score']} pts ({difficulty_name}, Lv {run['level']})"
                )
        else:
            lines.append("  No runs yet")

        y = 130
        for line in lines:
            if line:
                text = self.small_font.render(line, True, WHITE)
                rect = text.get_rect(center=(WIDTH // 2, y))
                self.screen.blit(text, rect)
            y += 30

        draw_centered_text(
            self.screen,
            self.small_font,
            "Press TAB or ESC to Close",
            CYAN,
            HEIGHT - 40,
        )

    def draw_title_screen(self):
        draw_centered_text(
            self.screen,
            self.title_font,
            "SpinJump Dodger",
            self.title_color(),
            self.title_bounce_y(HEIGHT // 2 - 110),
        )
        draw_centered_text(
            self.screen,
            self.font,
            "Press SPACE to Start",
            WHITE,
            HEIGHT // 2 - 30,
        )

        diff_color = self.difficulty["color"]
        draw_centered_text(
            self.screen,
            self.font,
            f"Difficulty: {self.difficulty['name']}",
            diff_color,
            HEIGHT // 2 + 15,
        )
        draw_centered_text(
            self.screen,
            self.small_font,
            "LEFT/RIGHT or 1-3 to change   TAB for stats",
            WHITE,
            HEIGHT // 2 + 55,
        )
        draw_centered_text(
            self.screen,
            self.small_font,
            f"Best ({self.difficulty['name']}): {self.best_for_difficulty}",
            CYAN,
            HEIGHT // 2 + 90,
        )
        self._draw_obstacle_legend(HEIGHT // 2 + 130)
        self._draw_powerup_legend(HEIGHT // 2 + 175)

    def draw(self):
        self.screen.fill(BLACK)
        shake = self.shake_offset()
        self.draw_world()
        self.draw_hud()

        if not self.started:
            self.draw_title_screen()
            if self.show_stats_screen:
                self.draw_stats_screen()
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
                    f"NEW {self.difficulty['name'].upper()} HIGH SCORE!",
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

        if self.powerup_banner_timer > 0 and self.started and not self.game_over:
            draw_centered_text(
                self.screen,
                self.small_font,
                self.powerup_banner_text,
                YELLOW,
                HEIGHT // 2 + 85,
            )

        if self.paused:
            self.draw_pause_overlay()

        pygame.display.flip()

    def _draw_obstacle_legend(self, legend_y):
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

    def _draw_powerup_legend(self, legend_y):
        entries = [
            (POWERUP_TYPES["shield"]["color"], "Shield"),
            (POWERUP_TYPES["slow"]["color"], "Slow-Mo"),
            (POWERUP_TYPES["boost"]["color"], "2x Score"),
        ]
        for index, (color, label) in enumerate(entries):
            x = WIDTH // 2 - 150 + index * 155
            pygame.draw.circle(self.screen, color, (x, legend_y), 7)
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