# SpinJump Dodger

A fun arcade-style dodging game built with Pygame for Stanford's Code in Place final project.

## Features

- Central spinning platform with animated markers
- Jump outward to dodge incoming obstacles
- Three obstacle types:
  - **Red** — standard speed (10 pts)
  - **Orange** — faster and smaller (15 pts)
  - **Purple** — zigzag path (20 pts, appears from level 3)
- Three difficulty modes: **Easy**, **Normal**, **Hard**
  - **Easy** — only slow red balls, slower pacing, great for learning
  - **Normal** — mixed obstacles with balanced challenge
  - **Hard** — faster platform spin and tougher spawns
- Collectible power-ups:
  - **Shield** — blocks one hit (stack up to 2)
  - **Slow-Mo** — slows obstacles and platform spin for 5 seconds
  - **2x Score** — doubles points for 8 seconds
- Gradual per-level speed scaling
- Simple physics: gravity when jumping and landing back on the platform
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
- **SPACE or UP**: Jump outward over incoming obstacles
- **Hold LEFT / RIGHT**: Move around the platform
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

3. Optional smoke test:

   ```bash
   python test_game.py
   ```

Enjoy spinning and jumping!

Made with love for Code in Place.