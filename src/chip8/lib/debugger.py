import ctypes
import os

import sdl2
import sdl2.sdlttf as ttf


FONT_CANDIDATES = [
    "/System/Library/Fonts/Menlo.ttc",
    "/System/Library/Fonts/Courier.ttc",
    "/System/Library/Fonts/SFNSMono.ttf",
    "/Library/Fonts/Menlo.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
]

WHITE = sdl2.SDL_Color(230, 230, 230, 255)
GREEN = sdl2.SDL_Color(120, 220, 120, 255)
YELLOW = sdl2.SDL_Color(230, 220, 100, 255)
DIM = sdl2.SDL_Color(110, 110, 110, 255)
ACCENT = sdl2.SDL_Color(120, 180, 255, 255)


def disassemble(opcode):
    n = opcode & 0xF000
    x = (opcode >> 8) & 0xF
    y = (opcode >> 4) & 0xF
    nn = opcode & 0xFF
    nnn = opcode & 0xFFF
    nibble = opcode & 0xF

    if opcode == 0x00E0:
        return "CLS"
    if opcode == 0x00EE:
        return "RET"
    if n == 0x0000:
        return f"SYS {nnn:03X}"
    if n == 0x1000:
        return f"JP  {nnn:03X}"
    if n == 0x2000:
        return f"CALL {nnn:03X}"
    if n == 0x3000:
        return f"SE  V{x:X}, {nn:02X}"
    if n == 0x4000:
        return f"SNE V{x:X}, {nn:02X}"
    if n == 0x5000:
        return f"SE  V{x:X}, V{y:X}"
    if n == 0x6000:
        return f"LD  V{x:X}, {nn:02X}"
    if n == 0x7000:
        return f"ADD V{x:X}, {nn:02X}"
    if n == 0x8000:
        return {
            0x0: f"LD  V{x:X}, V{y:X}",
            0x1: f"OR  V{x:X}, V{y:X}",
            0x2: f"AND V{x:X}, V{y:X}",
            0x3: f"XOR V{x:X}, V{y:X}",
            0x4: f"ADD V{x:X}, V{y:X}",
            0x5: f"SUB V{x:X}, V{y:X}",
            0x6: f"SHR V{x:X}",
            0x7: f"SUBN V{x:X}, V{y:X}",
            0xE: f"SHL V{x:X}",
        }.get(nibble, f".db {opcode:04X}")
    if n == 0x9000:
        return f"SNE V{x:X}, V{y:X}"
    if n == 0xA000:
        return f"LD  I, {nnn:03X}"
    if n == 0xB000:
        return f"JP  V0, {nnn:03X}"
    if n == 0xC000:
        return f"RND V{x:X}, {nn:02X}"
    if n == 0xD000:
        return f"DRW V{x:X}, V{y:X}, {nibble:X}"
    if n == 0xE000:
        if nn == 0x9E:
            return f"SKP V{x:X}"
        if nn == 0xA1:
            return f"SKNP V{x:X}"
    if n == 0xF000:
        return {
            0x07: f"LD  V{x:X}, DT",
            0x0A: f"LD  V{x:X}, K",
            0x15: f"LD  DT, V{x:X}",
            0x18: f"LD  ST, V{x:X}",
            0x1E: f"ADD I, V{x:X}",
            0x29: f"LD  F, V{x:X}",
            0x33: f"LD  B, V{x:X}",
            0x55: f"LD  [I], V{x:X}",
            0x65: f"LD  V{x:X}, [I]",
        }.get(nn, f".db {opcode:04X}")
    return f".db {opcode:04X}"


class Debugger:
    WIDTH = 720
    HEIGHT = 600
    MEMORY_Y = 320

    def __init__(self):
        self.window = None
        self.renderer = None
        self.font = None
        self.window_id = None
        self.line_h = 16
        self.enabled = False
        self.mem_offset = 0x200
        self.follow_pc = True

    def open(self, x=None, y=None):
        if ttf.TTF_Init() != 0:
            print(f"[debugger] TTF_Init failed: {ttf.TTF_GetError().decode()}")
            return

        font_path = next((p for p in FONT_CANDIDATES if os.path.exists(p)), None)
        if not font_path:
            print("[debugger] No usable monospace font found; debugger disabled")
            ttf.TTF_Quit()
            return

        self.font = ttf.TTF_OpenFont(font_path.encode('utf-8'), 14)
        if not self.font:
            print(f"[debugger] TTF_OpenFont failed: {ttf.TTF_GetError().decode()}")
            ttf.TTF_Quit()
            return

        self.line_h = ttf.TTF_FontHeight(self.font) + 2

        self.window = sdl2.SDL_CreateWindow(
            b"pyChip8SDL - debugger",
            sdl2.SDL_WINDOWPOS_CENTERED if x is None else x,
            sdl2.SDL_WINDOWPOS_CENTERED if y is None else y,
            self.WIDTH, self.HEIGHT,
            sdl2.SDL_WINDOW_SHOWN,
        )
        if not self.window:
            print(f"[debugger] SDL window creation failed: {sdl2.SDL_GetError().decode()}")
            return
        self.window_id = sdl2.SDL_GetWindowID(self.window)

        self.renderer = sdl2.SDL_CreateRenderer(
            self.window, -1, sdl2.SDL_RENDERER_ACCELERATED
        )
        if not self.renderer:
            print(f"[debugger] SDL renderer creation failed: {sdl2.SDL_GetError().decode()}")
            return

        self.enabled = True

    def jump_to_pc(self):
        self.follow_pc = True

    def scroll(self, delta):
        self.follow_pc = False
        self.mem_offset = max(0, min(0xFFF, self.mem_offset + delta))

    def _draw_text(self, text, x, y, color=WHITE):
        if not text:
            return
        surface = ttf.TTF_RenderText_Blended(self.font, text.encode('utf-8'), color)
        if not surface:
            return
        texture = sdl2.SDL_CreateTextureFromSurface(self.renderer, surface)
        s = surface.contents
        rect = sdl2.SDL_Rect(x, y, s.w, s.h)
        sdl2.SDL_RenderCopy(self.renderer, texture, None, ctypes.byref(rect))
        sdl2.SDL_FreeSurface(surface)
        sdl2.SDL_DestroyTexture(texture)

    def render(self, cpu, ram, paused):
        if not self.enabled:
            return

        sdl2.SDL_SetRenderDrawColor(self.renderer, 18, 20, 28, 255)
        sdl2.SDL_RenderClear(self.renderer)

        regs = cpu.registers
        timers = cpu.timers
        stack = regs['stack']
        pc = regs['pc']
        ram_size = len(ram._ram)

        # Status line
        status = "PAUSED" if paused else "RUNNING"
        status_color = YELLOW if paused else GREEN
        self._draw_text(f"[{status}]", 8, 8, status_color)
        self._draw_text(
            "Space pause   F10 step   F2 reset   PgUp/PgDn scroll   Home follow PC   Esc quit",
            80, 8, DIM,
        )

        # Registers column (4 regs per row -> 4 rows)
        reg_x = 8
        y = 36
        self._draw_text("REGISTERS", reg_x, y, ACCENT)
        y += self.line_h
        for base_r in (0, 4, 8, 12):
            text = " ".join(f"V{base_r + i:X}={regs['v'][base_r + i]:02X}" for i in range(4))
            self._draw_text(text, reg_x, y)
            y += self.line_h
        y += 6
        self._draw_text(f"PC={pc:03X}  I={regs['i']:03X}", reg_x, y); y += self.line_h
        self._draw_text(
            f"DT={timers['delay']:02X}  ST={timers['sound']:02X}  SP={len(stack)}",
            reg_x, y,
        ); y += self.line_h
        y += 6
        self._draw_text("STACK", reg_x, y, ACCENT); y += self.line_h
        stack_max_y = self.MEMORY_Y - 6
        if not stack:
            self._draw_text("  (empty)", reg_x, y, DIM)
        else:
            for depth, addr in enumerate(reversed(stack[-8:])):
                if y + self.line_h > stack_max_y:
                    break
                self._draw_text(f"  {depth}: {addr:03X}", reg_x, y)
                y += self.line_h

        # Disassembly column
        dis_x = 240
        dis_y = 36
        self._draw_text("DISASM", dis_x, dis_y, ACCENT)
        rows_before = 3
        rows_after = 10
        for idx, i in enumerate(range(-rows_before, rows_after + 1)):
            addr = pc + i * 2
            line_y = dis_y + self.line_h * (idx + 1)
            if line_y + self.line_h > self.MEMORY_Y - 6:
                break
            if addr < 0 or addr + 1 >= ram_size:
                continue
            opcode = (ram[addr] << 8) | ram[addr + 1]
            color = YELLOW if i == 0 else (DIM if i < 0 else WHITE)
            marker = "->" if i == 0 else "  "
            self._draw_text(
                f"{marker} {addr:03X}: {opcode:04X}  {disassemble(opcode)}",
                dis_x, line_y, color,
            )

        # Keypad state
        key_x = 540
        key_y = 36
        self._draw_text("KEYS", key_x, key_y, ACCENT)
        keypad = [
            (0x1, 0, 0), (0x2, 1, 0), (0x3, 2, 0), (0xC, 3, 0),
            (0x4, 0, 1), (0x5, 1, 1), (0x6, 2, 1), (0xD, 3, 1),
            (0x7, 0, 2), (0x8, 1, 2), (0x9, 2, 2), (0xE, 3, 2),
            (0xA, 0, 3), (0x0, 1, 3), (0xB, 2, 3), (0xF, 3, 3),
        ]
        for k, cx, cy in keypad:
            color = GREEN if cpu.key[k] else DIM
            self._draw_text(
                f"{k:X}",
                key_x + cx * 32,
                key_y + self.line_h * (cy + 1) + 4,
                color,
            )

        # Memory hex dump (fixed Y so it never overlaps the panels above)
        if self.follow_pc:
            self.mem_offset = pc & ~0xF
        mem_x = 8
        mem_y = self.MEMORY_Y
        title = f"MEMORY @ {self.mem_offset:03X}"
        if self.follow_pc:
            title += "   (following PC)"
        self._draw_text(title, mem_x, mem_y, ACCENT)
        offset = self.mem_offset & ~0xF

        available = self.HEIGHT - (mem_y + self.line_h) - 8
        rows = max(1, available // self.line_h)
        for r in range(rows):
            base = offset + r * 16
            if base >= ram_size:
                break
            hex_part = " ".join(f"{ram[base + c]:02X}" for c in range(16) if base + c < ram_size)
            ascii_part = "".join(
                chr(ram[base + c]) if 32 <= ram[base + c] < 127 else "."
                for c in range(16) if base + c < ram_size
            )
            color = YELLOW if base <= pc < base + 16 else WHITE
            self._draw_text(
                f"{base:03X}: {hex_part}  {ascii_part}",
                mem_x, mem_y + self.line_h * (r + 1),
                color,
            )

        sdl2.SDL_RenderPresent(self.renderer)

    def shutdown(self):
        if self.font:
            ttf.TTF_CloseFont(self.font)
            self.font = None
        if self.renderer:
            sdl2.SDL_DestroyRenderer(self.renderer)
            self.renderer = None
        if self.window:
            sdl2.SDL_DestroyWindow(self.window)
            self.window = None
        if self.enabled:
            ttf.TTF_Quit()
            self.enabled = False
        self.window_id = None
