import os
from . import asset_path
from src.chip8.lib.ram import ram


def test_ram_fill():
    ram_disk = ram()
    assert len(ram_disk.ram) == 4096


def test_ram_set_byte():
    address = 0xFF1
    byte = 0x1F

    ram_disk = ram()
    ram_disk.set_byte(address, byte)

#    print(ram_disk.dump())

    assert ram_disk.get_byte(address) == byte

def test_ram_clear():
    address = 0xFF1
    byte = 0x1F

    # Create Ramdisk
    ram_disk = ram()

    # Set address to example byte
    ram_disk.set_byte(address, byte)

    # check address was set
#    print(ram_disk.get_byte(address))

    # clear ram
    ram_disk.clear()

    # check address was set to 0x00
#    print(ram_disk.get_byte(address))

    # Success if byte at given address is 0x00
    assert ram_disk.get_byte(address) == 0x00
