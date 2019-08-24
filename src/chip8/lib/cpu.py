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

        self.reset()

    def reset(self):
        self.running = False
        self.mode = 'NORMAL'

        self.registers = {
            # 16 general purpose 8-bit registers, usually referred to as Vx, where x is a hexadecimal digit (0 - F)
            'v': [],

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

    def process_opcode(self):
        def fetch():
            # Retrieve 2 bytes, the PC and PC+1
            # We need to join these 2 bytes so we shift PC left by adding 8 zeroes (X<<8) and or'ing PC+1 with it
            return self.memory[self.registers['pc']] << 8 | self.memory[self.registers['pc'] + 1]

        def decode(opcode):

            op = opcode & self.MASK_OPCODE  # 0xF000
            nnn = opcode & self.MASK_INDEX  # 0x0FFF

            def clear_return():
                def clear_screen():
                    pass

                def return_from_subroutine():  # 0x00EE
                    self.registers['sp'] -= 1
                    self.registers['pc'] = self.memory[self.registers['sp']] << 8

                    self.registers['sp'] -= 1
                    self.registers['pc'] = self.memory[self.registers['sp']]

                def screen_scroll_down():
                    num_lines = subroutine & 0x000F

                def screen_scroll_right():
                    pass

                def screen_scroll_left():
                    pass

                def stop_running():
                    self.running = False

                def disable_extended_mode():
                    pass

                def enable_extended_mode():
                    pass

                routines = {
                    0x00E0: clear_screen,
                    0x00EE: return_from_subroutine,
                    0x00FB: screen_scroll_right,
                    0x00FC: screen_scroll_left,
                    0x00FD: stop_running,
                    0x00FE: disable_extended_mode,
                    0x00FF: enable_extended_mode,
                }

                routine = nnn & 0x00FF
                subroutine = nnn & 0x00F0

                try:
                    if subroutine == 0x00C0:
                        screen_scroll_down()
                    else:
                        routines[routine]()
                except Exception as ex:
                    raise Exception(f"Unknown opcode {opcode}")

            def jump_to_address():
                self.registers['pc'] = nnn

            def call_address():
                pass

            def skip_instruction_register_eq_value():
                pass

            def skip_instruction_register_neq_value():
                pass

            def skip_instruction_register_eq_register():
                pass

            def move_into_register():
                pass

            def add_to_register():
                pass

            def bitwise_operations():

                def reg_load():
                    x = (self.operand & 0x0F00) >> 8
                    y = (self.operand & 0x00F0) >> 4

                    self.registers['v'][x] = self.registers['v'][y]

                def bit_or():
                    x = (self.operand & 0x0F00) >> 8
                    y = (self.operand & 0x00F0) >> 4

                    self.registers['v'][x] = self.registers['v'][x] | self.registers['v'][y]

                def bit_and():
                    x = (self.operand & 0x0F00) >> 8
                    y = (self.operand & 0x00F0) >> 4

                    self.registers['v'][x] = self.registers['v'][x] & self.registers['v'][y]

                def bit_xor():
                    x = (self.operand & 0x0F00) >> 8
                    y = (self.operand & 0x00F0) >> 4

                    self.registers['v'][x] = self.registers['v'][x] ^ self.registers['v'][y]

                def reg_add():
                    x = (self.operand & 0x0F00) >> 8
                    y = (self.operand & 0x00F0) >> 4

                    temp = self.registers['v'][x] + self.registers['v'][y]

                    if temp > 255:
                        # overflow, we need to set overflow bit in Vf
                        self.registers['v'][x] = temp - 256
                        self.registers['v'][0xF] = 1
                    else:
                        self.registers['v'][x] = temp
                        self.registers['v'][0xF] = 0

                def reg_sub():
                    x = (self.operand & 0x0F00) >> 8
                    y = (self.operand & 0x00F0) >> 4

                    if self.registers['v'][x] > self.registers['v'][y]:
                        self.registers['v'][x] = self.registers['v'][x] - self.registers['v'][y]
                        self.registers['v'][0xF] = 1
                    else:
                        self.registers['v'][x] = 256 + self.registers['v'][x] - self.registers['v'][y]
                        self.registers['v'][0xF] = 0

                def reg_shr():
                    x = (self.operand & 0x0F00) >> 8
                    y = (self.operand & 0x00F0) >> 4

                    self.registers['v'][0xF] = self.registers['v'][x] & 0x1
                    self.registers['v'][y] = self.registers['v'][x] >> 1

                def reg_subn():
                    x = (self.operand & 0x0F00) >> 8
                    y = (self.operand & 0x00F0) >> 4

                    if self.registers['v'][y] > self.registers['v'][x]:
                        self.registers['v'][x] = self.registers['v'][y] - self.registers['v'][x]
                        self.registers['v'][0xF] = 1
                    else:
                        self.registers['v'][x] = 256 + self.registers['v'][y] - self.registers['v'][x]
                        self.registers['v'][0xF] = 0

                def reg_shl():
                    x = (self.operand & 0x0F00) >> 8
                    y = (self.operand & 0x00F0) >> 4

                    self.registers['v'][0xF] = (self.registers['v'][x] & 0x80) >> 1
                    self.registers['v'][y] = self.registers['v'][x] << 1

                subroutines = {
                    0x0000: reg_load,  # 8xy0 Load (Vx = Vy)
                    0x0001: bit_or,    # 8xy1 Bitwise OR (Vx = Vx || Vy)
                    0x0002: bit_and,   # 8xy2 Bitwise AND (Vx = Vx & Vy)
                    0x0003: bit_xor,   # 8xy3 Bitwise XOR (Vx = Vx || Vy)
                    0x0004: reg_add,   # 8xy4 ADD
                    0x0005: reg_sub,   # 8xy5 SUB
                    0x0006: reg_shr,   # 8xy6 SHR
                    0x0007: reg_subn,  # 8xy7 SUBN
                    0x000E: reg_shl    # 8xyE SHL
                }

                subroutine = nnn & self.MASK_LOGICAL_ROUTINE

                try:
                    subroutines[subroutine]()
                except Exception as ex:
                    raise Exception(f"Unknown opcode {opcode}")

            def skip_instruction_register_neq_register():
                pass

            def set_index_register():
                pass

            def jump_to_address_plus_value():
                pass

            def random_number_generator():
                pass

            def draw_sprite():
                pass

            def keyboard_event():
                pass

            def other_routines():
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
                0x8000: bitwise_operations,
                0x9000: skip_instruction_register_neq_register,
                0xA000: set_index_register,
                0xB000: jump_to_address_plus_value,
                0xC000: random_number_generator,
                0xD000: draw_sprite,
                0xE000: keyboard_event,
                0xF000: other_routines,
            }

            try:
                return operations[op]()
            except Exception as ex:
                raise Exception(f"Unknown Opcode {opcode}")

        operation = decode(fetch())  # the opcode fn to run
        operation()

    def tick(self):
        self.process_opcode()
