from collections import defaultdict
from random import randint


class Cpu:

    MASK_OPCODE = 0xF000
    MASK_INDEX = 0x0FFF
    MASK_LOGICAL_ROUTINE = 0x000F
    MASK_MISC_ROUTINE = 0x00FF

    memory = None
    display = None
    registers = None
    timers = None
    key = None
    start_addr = None
    running = False
    mode = 'NORMAL'

    def __init__(self, start_addr, memory, display):
        self.memory = memory
        self.display = display
        self.start_addr = start_addr

        self.opcode = None
        self.nxxx = None  # 0xF000
        self.xnxx = None  # 0x0F00
        self.xxnx = None  # 0x00F0
        self.xxxn = None  # 0x000F
        self.xxnn = None  # 0x00FF
        self.xnnn = None  # 0x0FFF

        self.reset()

    def reset(self):
        self.running = False
        self.mode = 'NORMAL'

        self.registers = {
            # 16 general purpose 8-bit registers, usually referred to as Vx, where x is a hexadecimal digit (0 - F)
            'v': defaultdict(lambda: 0),

            # 16-bit reg. This reg is used to store memory addresses so only the lowest (rightmost) 12 bits are used
            'i': 0,

            # Stack pointer used to point to the topmost level of the stack
            'sp': 0,

            # Program Counter 16-bit is used to store the currently executing address
            'pc': int(self.start_addr),

            # 16x16bit val used to store the address that the interpreter should return to when finished with subroutine
            'stack': []
        }

        # Timer Registers: When these registers are non-zero, they are automatically decremented at a rate of 60Hz
        self.timers = {
            'delay': [],
            'sound': []
        }

        self.key = bytearray(16)

    def fetch(self):
        # Retrieve 2 bytes, the PC and PC+1
        # We need to join these 2 bytes so we shift PC left by adding 8 zeroes (X<<8) and or'ing PC+1 with it
        self.opcode = self.memory[self.registers['pc']] << 8 | self.memory[self.registers['pc'] + 1]
        self.nxxx = self.opcode & 0xF000
        self.xnxx = self.opcode & 0x0F00
        self.xxnx = self.opcode & 0x00F0
        self.xxxn = self.opcode & 0x000F
        self.xxnn = self.opcode & 0x00FF
        self.xnnn = self.opcode & 0x0FFF
        self.registers['pc'] += 2

    def clear_return(self):
        ops = {  # Clear Return
            0x00E0: self.clear_screen,
            0x00EE: self.return_from_subroutine,
            0x00FB: self.screen_scroll_right,
            0x00FC: self.screen_scroll_left,
            0x00FD: self.stop_running,
            0x00FE: self.disable_extended_mode,
            0x00FF: self.enable_extended_mode,
        }

        if self.xxnx == 0x00C0:  # special case since 0x000F is variable it cant be matched directly
            self.screen_scroll_down()

        try:
            ops[self.xxnn]()
        except Exception as ex:
            raise Exception(f"Unknown Opcode {self.opcode}")

    def clear_screen(self):  # 0x00E0
        self.display.reset()

    def return_from_subroutine(self):  # 0x00EE
        # self.registers['sp'] -= 1
        # self.registers['pc'] = self.memory[self.registers['sp']] << 8
        #
        # self.registers['sp'] -= 1
        # self.registers['pc'] = self.memory[self.registers['sp']]
        self.registers['pc'] = self.registers['stack'].pop()

    def screen_scroll_down(self):
        num_lines = self.xxxn

    def screen_scroll_right(self):
        pass

    def screen_scroll_left(self):
        pass

    def stop_running(self):
        self.running = False

    def disable_extended_mode(self):
        pass

    def enable_extended_mode(self):
        pass

    def jump_to_address(self):
        self.registers['pc'] = self.xnnn

    def call_address(self):
        self.registers['stack'].append(self.registers['pc'])
        self.registers['pc'] = self.xnnn

    def skip_instruction_register_eq_value(self):
        source = self.xnnn >> 8

        if self.registers['v'][source] == self.xxnn:
            self.registers['pc'] += 2

    def skip_instruction_register_neq_value(self):
        source = self.xnxx >> 8

        if self.registers['v'][source] != self.xxnn:
            self.registers['pc'] += 2

    def skip_instruction_register_eq_register(self):
        source = self.xnxx >> 8
        target = self.xxnx >> 4
        if self.registers['v'][source] == self.registers['v'][target]:
            self.registers['pc'] += 2

    def move_into_register(self):
        target = self.xnxx >> 8
        self.registers['v'][target] = self.xxnn

    def add_to_register(self):
        target = self.xnxx >> 8
        temp = self.registers['v'][target] + self.xxnn
        self.registers['v'][target] = temp if temp < 256 else temp - 256

    def bitwise_operators(self):
        ops = {  # Bitwise Operations
            0x8000: self.reg_load,  # 8xy0 Load (Vx = Vy)
            0x8001: self.bit_or,    # 8xy1 Bitwise OR (Vx = Vx || Vy)
            0x8002: self.bit_and,   # 8xy2 Bitwise AND (Vx = Vx & Vy)
            0x8003: self.bit_xor,   # 8xy3 Bitwise XOR (Vx = Vx || Vy)
            0x8004: self.reg_add,   # 8xy4 ADD
            0x8005: self.reg_sub,   # 8xy5 SUB
            0x8006: self.reg_shr,   # 8xy6 SHR
            0x8007: self.reg_subn,  # 8xy7 SUBN
            0x800E: self.reg_shl,   # 8xyE SHL
        }

        try:
            ops[self.opcode & 0xF00F]()
        except Exception as ex:
            raise Exception(f"Unknown Opcode {self.opcode}")

    def reg_load(self):
        x = self.xnxx >> 8
        y = self.xxnx >> 4

        self.registers['v'][x] = self.registers['v'][y]

    def bit_or(self):
        x = self.xnxx >> 8
        y = self.xxnx >> 4

        self.registers['v'][x] = self.registers['v'][x] | self.registers['v'][y]

    def bit_and(self):
        x = self.xnxx >> 8
        y = self.xxnx >> 4

        self.registers['v'][x] = self.registers['v'][x] & self.registers['v'][y]

    def bit_xor(self):
        x = self.xnxx >> 8
        y = self.xxnx >> 4

        self.registers['v'][x] = self.registers['v'][x] ^ self.registers['v'][y]

    def reg_add(self):
        x =self.xnxx >> 8
        y =self.xxnx >> 4

        temp = self.registers['v'][x] + self.registers['v'][y]

        if temp > 255:
            # overflow, we need to set overflow bit in Vf
            self.registers['v'][x] = temp - 256
            self.registers['v'][0xF] = 1
        else:
            self.registers['v'][x] = temp
            self.registers['v'][0xF] = 0

    def reg_sub(self):
        x = self.xnxx >> 8
        y = self.xxnx >> 4

        if self.registers['v'][x] > self.registers['v'][y]:
            self.registers['v'][x] = self.registers['v'][x] - self.registers['v'][y]
            self.registers['v'][0xF] = 1
        else:
            self.registers['v'][x] = 256 + self.registers['v'][x] - self.registers['v'][y]
            self.registers['v'][0xF] = 0

    def reg_shr(self):
        x = self.xnxx >> 8
        y = self.xxnx >> 4

        self.registers['v'][0xF] = self.registers['v'][x] & 0x1
        self.registers['v'][y] = self.registers['v'][x] >> 1

    def reg_subn(self):
        x = self.xnxx >> 8
        y = self.xxnx >> 4

        if self.registers['v'][y] > self.registers['v'][x]:
            self.registers['v'][x] = self.registers['v'][y] - self.registers['v'][x]
            self.registers['v'][0xF] = 1
        else:
            self.registers['v'][x] = 256 + self.registers['v'][y] - self.registers['v'][x]
            self.registers['v'][0xF] = 0

    def reg_shl(self):
        x = self.xnxx >> 8
        y = self.xxnx >> 4

        self.registers['v'][0xF] = (self.registers['v'][x] & 0x80) >> 1
        self.registers['v'][y] = self.registers['v'][x] << 1


    def skip_instruction_register_neq_register(self):
        source = self.xnxx >> 8
        target = self.xxnx >> 4
        if self.registers['v'][source] != self.registers['v'][target]:
            self.registers['pc'] += 2

    def set_index_register(self):
        self.registers['i'] = self.xnnn

    def jump_to_address_plus_value(self):
        self.registers['pc'] = self.registers['i'] + self.xnnn

    def random_number_generator(self):
        value = self.xxnn
        target = self.xnxx >> 8
        self.registers['v'][target] = value & randint(0, 255)

    def draw_sprite(self):
        x_source = self.xnxx >> 8
        y_source = self.xxnx >> 4
        x_pos = self.registers['v'][x_source]
        y_pos = self.registers['v'][y_source]
        num_bytes = self.xxxn
        self.registers['v'][0xF] = 0

        if self.mode == 'EXTENDED' and num_bytes == 0:
            pass
        else:
            pass

    def keyboard_event(self):
        pass

    def other_routines(self):
        pass

    operations = {
        0x0000: clear_return,
        0x1000: jump_to_address,
        0x2000: call_address,
        0x3000: skip_instruction_register_eq_value,
        0x4000: skip_instruction_register_neq_value,
        0x5000: skip_instruction_register_eq_register,
        0x6000: move_into_register,
        0x7000: add_to_register,
        0x8000: bitwise_operators,
        0x9000: skip_instruction_register_neq_register,
        0xA000: set_index_register,
        0xB000: jump_to_address_plus_value,
        0xC000: random_number_generator,
        0xD000: draw_sprite,
        0xE000: keyboard_event,
        0xF000: other_routines,
        }

    def tick(self):
        self.fetch()

        try:
            self.operations[self.nxxx](self)
        except Exception as ex:
            raise Exception(f"Unknown Opcode {self.opcode}")