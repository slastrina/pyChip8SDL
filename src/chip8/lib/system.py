import os
import tkinter as tk
from tkinter import filedialog

from chip8 import rom_path
from chip8.lib.cpu import Cpu
from chip8.lib.display import Display
from chip8.lib.ram import Ram


class System:

    flags = {
        'draw': False,
        'running': False
    }

    def __init__(self):
        self.ram = Ram()
        self.display = Display(64, 32)
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
            file_path = os.path.join(rom_path, filename)
        else:
            root = tk.Tk()
            root.withdraw()
            file_path = filedialog.askopenfilename(initialdir=rom_path)

        with open(file_path, 'rb') as f:
            self.ram.set_block(f.read(), self.ram.get_program_address())

    def start(self):
        # Consider running in a dedicated thread
        self.cpu.running = True

        while self.cpu.running:
            self.cpu.tick()