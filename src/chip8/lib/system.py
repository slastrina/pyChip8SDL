from chip8 import resource_path, rom_path
from chip8.lib.cpu import Cpu
from chip8.lib.ram import Ram
from chip8.lib.display import Display
import os


class System:

    flags = {
        'draw': False,
        'running': False
    }

    def __init__(self):
        self.ram = Ram()
        self.display = Display(64, 32)
        self.cpu = Cpu(self.ram.PROG_STD_START, self.ram, self.display)

    def reset(self):
        self.ram.reset()
        self.display.reset()
        self.cpu.reset()

    def load_rom(self, filename):
        path = os.path.join(rom_path, filename)

    def start(self):
        # Consider running in a dedicated thread
        while 1:
            self.cpu.tick()
            break  # TODO remove break
