# SpinJump Dodger

A fun arcade-style dodging game built with Pygame for Stanford's Code in Place final project.

## Features

- Central spinning platform with animated markers
- Jump to dodge incoming obstacles
- Three obstacle types:
  - **Red** — standard speed (10 pts)
  - **Orange** — faster and smaller (15 pts)
  - **Purple** — zigzag path (20 pts, appears from level 3)
- Increasing speed and difficulty per level
- Simple physics: gravity when jumping and falling
- Score, level, and persistent high score
- Procedural sound effects (jump, land, score, level up, game over)
- Particle bursts when dodging or crashing
- Retro feel with basic shapes

## Controls

- **SPACE or UP**: Jump
- **LEFT / RIGHT arrows**: Move left/right on the platform
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