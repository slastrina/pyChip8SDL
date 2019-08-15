from hexdump import hexdump


class Ram:
    RAM_START = 0x000       # (0) to 0x1FF reserved for interpreter
    PROG_STD_START = 0x200  # (512) Start of most Chip-8 programs
    PROG_ETI_START = 0x600  # (1536) Start of ETI 660 Chip-8 programs
    RAM_END = 0xFFF         # (4095) End of Chip-8 RAM

    _ram = None
    _size = None

    def __init__(self, size=4096):
        self._size = size
        self.reset()

    def __setitem__(self, idx, val):
        self._ram[idx] = val

    def __getitem__(self, idx):
        return self._ram[idx]

    def get_range(self, start, end):
        return self._ram[start:end]

    def get_interpreter_block(self):
        return self._ram[self.RAM_START:self.PROG_STD_START]

    def get_std_prog_block(self):
        return self._ram[self.PROG_STD_START:self.RAM_END]

    def get_eti_prog_block(self):
        return self._ram[self.PROG_ETI_START:self.RAM_END]

    def reset(self):
        self._ram = bytearray(self._size)

    def dump(self):
        hexdump(self._ram)
