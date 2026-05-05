import sys

from chip8.lib.system import System


def main():
    rom = sys.argv[1] if len(sys.argv) > 1 else None

    chip8 = System()
    chip8.load_font()
    chip8.load_rom(rom)
    chip8.start()


if __name__ == '__main__':
    main()
