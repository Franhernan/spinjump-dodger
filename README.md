# SpinJump Dodger

A fun arcade-style dodging game built with Pygame for Stanford's Code in Place final project.

## Features

- Central spinning platform with animated markers
- Jump to dodge incoming obstacles
- Three obstacle types:
  - **Red** — standard speed (10 pts)
  - **Orange** — faster and smaller (15 pts)
  - **Purple** — zigzag path (20 pts, appears from level 3)
- Three difficulty modes: **Easy**, **Normal**, **Hard**
- Collectible power-ups:
  - **Shield** — blocks one hit (stack up to 2)
  - **Slow-Mo** — slows obstacles and platform spin for 5 seconds
  - **2x Score** — doubles points for 8 seconds
- Increasing speed and difficulty per level
- Simple physics: gravity when jumping and falling
- Per-difficulty high scores and local stats leaderboard
- Procedural sound effects
- Particle bursts when dodging, collecting power-ups, or crashing
- Combo multiplier for consecutive dodges within 2 seconds (up to x5)
- Animated title screen with demo obstacles
- Pause menu
- Retro feel with basic shapes

## Controls

### Title Screen
- **SPACE or ENTER**: Start game
- **LEFT / RIGHT** or **1 / 2 / 3**: Select difficulty
- **TAB**: Open stats screen
- **ESC**: Close stats screen

### Gameplay
- **SPACE or UP**: Jump
- **LEFT / RIGHT arrows**: Move left/right on the platform
- **P or ESC**: Pause / resume
- **R**: Restart after game over

## How to Run

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Start the game:

   ```bash
   python main.py
   ```

Enjoy spinning and jumping!

Made with love for Code in Place.