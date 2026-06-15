import array
import math

import pygame


def _make_tone(frequency, duration_ms, volume=0.25, fade=True):
    sample_rate = 22050
    sample_count = int(sample_rate * duration_ms / 1000)
    buffer = array.array("h")

    for index in range(sample_count):
        time = index / sample_rate
        envelope = 1.0
        if fade:
            envelope = max(0.0, 1.0 - index / sample_count)
        sample = int(32767 * volume * envelope * math.sin(2 * math.pi * frequency * time))
        buffer.append(sample)
        buffer.append(sample)

    return pygame.mixer.Sound(buffer=buffer)


class SoundManager:
    def __init__(self):
        self.enabled = True
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.jump = _make_tone(520, 90, volume=0.2)
            self.land = _make_tone(280, 70, volume=0.15)
            self.score = _make_tone(760, 60, volume=0.18)
            self.level_up = _make_tone(620, 140, volume=0.22)
            self.game_over = _make_tone(180, 320, volume=0.28, fade=False)
        except pygame.error:
            self.enabled = False

    def play(self, sound):
        if self.enabled and sound is not None:
            sound.play()