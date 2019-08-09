from hexdump import hexdump


class ram():

    RAM_START = 0x000       # (0) to 0x1FF reserved for interpreter
    PROG_STD_START = 0x200  # (512) Start of most Chip-8 programs
    PROG_ETI_START = 0x600  # (1536) Start of ETI 660 Chip-8 programs
    RAM_END = 0xFFF         # (4095) End of Chip-8 RAM

    def __init__(self):
        self.ram = bytearray(4096)

    def set_byte(self, idx, val):
        self.ram[idx] = val

    def get_byte(self, idx):
        return self.ram[idx]

    def get_interpreter_block(self):
        return self.ram[self.RAM_START:self.PROG_STD_START]

    def get_std_prog_block(self):
        return self.ram[self.PROG_STD_START:self.RAM_END]

    def get_eti_prog_block(self):
        return self.ram[self.PROG_ETI_START:self.RAM_END]

    def clear(self):
        self.ram = bytearray(4096)

    def dump(self):
        hexdump(self.ram)
