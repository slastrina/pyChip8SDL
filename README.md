# pyChip8SDL

A CHIP-8 emulator written in Python 3 using SDL2.

Project based on the spec at: http://devernay.free.fr/hacks/chip8/C8TECH10.HTM

## Dependencies

### System libraries (Homebrew)

```sh
brew install sdl2 sdl2_mixer sdl2_ttf
```

- `sdl2` — rendering / window / event backend
- `sdl2_mixer` — buzzer sound
- `sdl2_ttf` — text rendering for the debugger window

The Python `pysdl2` package binds to whichever native libraries are installed on the system.

### Python packages

```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running

```sh
# Pick a ROM from a numbered list of bundled ROMs
python -m chip8.app

# Or pass a ROM path directly (relative to src/chip8/roms/, or absolute)
python -m chip8.app "games/Pong [Paul Vervalin, 1990].ch8"
python -m chip8.app /absolute/path/to/rom.ch8
```

107 ROMs ship under `src/chip8/roms/` (demos, programs, games).

## Debugger

A second window opens alongside the emulator showing live state: V0–VF, I, PC, SP, the stack, the delay/sound timers, the keypad, a disassembly window centered on PC, and a hex dump of memory. Closing it leaves the emulator running.

| Key       | Action                                  |
|-----------|-----------------------------------------|
| `Space`   | Toggle pause/resume                     |
| `F10`     | Single-step one CPU instruction (pauses) |
| `F2`      | Reset the CPU and clear the screen      |
| `PgUp`/`PgDn` | Scroll the memory hex dump          |
| `Home`    | Snap the memory view back to following PC |
| `Esc`     | Quit                                    |

When paused, timers stop and the buzzer is silenced; resuming continues from the same state.

## Controls

The CHIP-8 hex keypad is mapped onto the left side of a QWERTY keyboard:

```
CHIP-8 keypad        Keyboard
1 2 3 C              1 2 3 4
4 5 6 D       →      Q W E R
7 8 9 E              A S D F
A 0 B F              Z X C V
```

`Esc` quits the emulator.

Different games use different keys — for example:
- **Pong**: `1` / `Q` (left paddle up/down), `4` / `R` (right paddle up/down)
- **Breakout**: `Q` / `E` (paddle left/right)
- **Tetris**: `Q` / `W` / `E` (rotate / left / right), `A` (drop)
