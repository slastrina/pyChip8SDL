from chip8.lib import ram

class cpu():

    def __init__(self, screen):
        self.screen = screen
        self.memory = ram


        self.registers = {
            'v': [],  # 16 general purpose 8-bit registers, usually referred to as Vx, where x is a hexadecimal digit (0 through F)
            'i': 0,  # 16-bit register. This register is used to store memory addresses so only the lowest (rightmost) 12 bits are used
            'sp': 0,  # Stack pointer used to point to the topmost level of the stack
            'pc': 0,  # Program Counter 16-bit is used to store the currently executing address
            'stack': []  # 16 x 16bit values used to store the address that the interpreter shoud return to when finished with a subroutine
        }

        # Timer Registers: When these registers are non-zero, they are automatically decremented at a rate of 60Hz
        self.timers = {
            'delay': [],
            'sound': []
        }
