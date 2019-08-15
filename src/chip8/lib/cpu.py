class Cpu:

    memory = None
    display = None
    registers = None
    timers = None
    key = None
    start_addr = None

    def __init__(self, start_addr, memory, display):
        self.memory = memory
        self.display = display
        self.start_addr = start_addr

        self.reset()

    def reset(self):
        self.registers = {
            # 16 general purpose 8-bit registers, usually referred to as Vx, where x is a hexadecimal digit (0 - F)
            'v': [],

            # 16-bit reg. This reg is used to store memory addresses so only the lowest (rightmost) 12 bits are used
            'i': int(self.start_addr),

            # Stack pointer used to point to the topmost level of the stack
            'sp': 0,

            # Program Counter 16-bit is used to store the currently executing address
            'pc': 0,

            # 16x16bit val used to store the address that the interpreter should return to when finished with subroutine
            'stack': []
        }

        # Timer Registers: When these registers are non-zero, they are automatically decremented at a rate of 60Hz
        self.timers = {
            'delay': [],
            'sound': []
        }

        self.key = bytearray(16)

    def process_opcode(self):
        def fetch():
            return self.memory[self.registers['pc']] | self.memory[self.registers['pc'] + 1]

        print(fetch())

    def cycle(self):
        self.process_opcode()
