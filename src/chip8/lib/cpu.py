class Cpu:

    MASK_OPCODE = 0xF000
    MASK_INDEX = 0x0FFF

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

            op = opcode & self.MASK_OPCODE
            index = opcode & self.MASK_INDEX

            def clear_return():
                if 0x00E0 == index:
                    pass
                elif 0x00EE == index:
                    pass

            def jump_to_address():
                pass

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
                pass

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
                raise Exception(f"Invalid Opcode {opcode}")

        operation = decode(fetch())
        operation()

    def tick(self):
        self.process_opcode()
