import ctypes
import os
import time

import sdl2

from chip8 import rom_path
from chip8.lib.cpu import Cpu
from chip8.lib.display import Display
from chip8.lib.ram import Ram


# Standard CHIP-8 keypad mapped onto the left side of a QWERTY keyboard:
#   1 2 3 C        1 2 3 4
#   4 5 6 D   →    Q W E R
#   7 8 9 E        A S D F
#   A 0 B F        Z X C V
KEY_MAP = {
    sdl2.SDLK_1: 0x1, sdl2.SDLK_2: 0x2, sdl2.SDLK_3: 0x3, sdl2.SDLK_4: 0xC,
    sdl2.SDLK_q: 0x4, sdl2.SDLK_w: 0x5, sdl2.SDLK_e: 0x6, sdl2.SDLK_r: 0xD,
    sdl2.SDLK_a: 0x7, sdl2.SDLK_s: 0x8, sdl2.SDLK_d: 0x9, sdl2.SDLK_f: 0xE,
    sdl2.SDLK_z: 0xA, sdl2.SDLK_x: 0x0, sdl2.SDLK_c: 0xB, sdl2.SDLK_v: 0xF,
}

CYCLES_PER_FRAME = 10  # ~600 Hz CPU at 60 fps
FRAME_TIME = 1.0 / 60.0


class System:

    def __init__(self):
        self.ram = Ram()
        self.display = Display(64, 32, scale=12, title="pyChip8SDL")
        self.cpu = Cpu(self.ram.get_program_address(), self.ram, self.display)

    def reset(self):
        self.ram.reset()
        self.display.reset()
        self.cpu.reset()

    def load_font(self):

        font = [0xF0, 0x90, 0x90, 0x90, 0xF0,  # 0
                0x20, 0x60, 0x20, 0x20, 0x70,  # 1
                0xF0, 0x10, 0xF0, 0x80, 0xF0,  # 2
                0xF0, 0x10, 0xF0, 0x10, 0xF0,  # 3
                0x90, 0x90, 0xF0, 0x10, 0x10,  # 4
                0xF0, 0x80, 0xF0, 0x10, 0xF0,  # 5
                0xF0, 0x80, 0xF0, 0x90, 0xF0,  # 6
                0xF0, 0x10, 0x20, 0x40, 0x40,  # 7
                0xF0, 0x90, 0xF0, 0x90, 0xF0,  # 8
                0xF0, 0x90, 0xF0, 0x10, 0xF0,  # 9
                0xF0, 0x90, 0xF0, 0x90, 0x90,  # A
                0xE0, 0x90, 0xE0, 0x90, 0xE0,  # B
                0xF0, 0x80, 0x80, 0x80, 0xF0,  # C
                0xE0, 0x90, 0x90, 0x90, 0xE0,  # D
                0xF0, 0x80, 0xF0, 0x80, 0xF0,  # E
                0xF0, 0x80, 0xF0, 0x80, 0x80]  # F

        self.ram.set_block(font, 0)

    def load_rom(self, filename=None):
        if filename:
            file_path = filename if os.path.isabs(filename) else os.path.join(rom_path, filename)
        else:
            file_path = self._pick_rom_from_console()

        if not file_path:
            raise RuntimeError("No ROM was selected.")

        with open(file_path, 'rb') as f:
            self.ram.set_block(f.read(), self.ram.get_program_address())

    @staticmethod
    def _pick_rom_from_console():
        roms = []
        for dirpath, _, filenames in os.walk(rom_path):
            for name in filenames:
                if name.lower().endswith('.ch8'):
                    full = os.path.join(dirpath, name)
                    rel = os.path.relpath(full, rom_path)
                    roms.append((rel, full))
        roms.sort(key=lambda r: r[0].lower())

        if not roms:
            raise RuntimeError(f"No .ch8 ROMs found under {rom_path}")

        print("\nAvailable ROMs:\n")
        width = len(str(len(roms)))
        for i, (rel, _) in enumerate(roms, start=1):
            print(f"  {i:>{width}}. {rel}")

        while True:
            choice = input(f"\nSelect a ROM [1-{len(roms)}] (or q to quit): ").strip()
            if choice.lower() in ('q', 'quit', 'exit'):
                return None
            if choice.isdigit():
                idx = int(choice)
                if 1 <= idx <= len(roms):
                    return roms[idx - 1][1]
            print("Invalid selection.")

    def _pump_events(self):
        event = sdl2.SDL_Event()
        while sdl2.SDL_PollEvent(ctypes.byref(event)):
            if event.type == sdl2.SDL_QUIT:
                self.cpu.running = False
            elif event.type == sdl2.SDL_KEYDOWN:
                sym = event.key.keysym.sym
                if sym == sdl2.SDLK_ESCAPE:
                    self.cpu.running = False
                elif sym in KEY_MAP:
                    self.cpu.key[KEY_MAP[sym]] = 1
            elif event.type == sdl2.SDL_KEYUP:
                sym = event.key.keysym.sym
                if sym in KEY_MAP:
                    self.cpu.key[KEY_MAP[sym]] = 0

    def start(self):
        if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO) != 0:
            raise RuntimeError(f"SDL_Init failed: {sdl2.SDL_GetError().decode()}")
        self.display.open()

        self.cpu.running = True
        next_frame = time.perf_counter()

        try:
            while self.cpu.running:
                self._pump_events()

                for _ in range(CYCLES_PER_FRAME):
                    if not self.cpu.running:
                        break
                    self.cpu.tick()

                if self.cpu.timers['delay'] > 0:
                    self.cpu.timers['delay'] -= 1
                if self.cpu.timers['sound'] > 0:
                    self.cpu.timers['sound'] -= 1

                self.display.render()

                next_frame += FRAME_TIME
                now = time.perf_counter()
                if now < next_frame:
                    time.sleep(next_frame - now)
                else:
                    next_frame = now
        finally:
            self.shutdown()

    def shutdown(self):
        self.display.shutdown()
        sdl2.SDL_Quit()
