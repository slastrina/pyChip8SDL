import os
from . import asset_path
from src.chip8.lib.ram import Ram


def test_ram_fill():
    ram_disk = Ram()
    assert len(ram_disk._ram) == 4096


def test_ram_set_byte():
    address = 0xFF1
    byte = 0x1F

    ram_disk = Ram()
    ram_disk[address] = byte

#    print(ram_disk.dump())

    assert ram_disk[address] == byte


def test_ram_clear():
    address = 0xFF1
    byte = 0x1F

    # Create Ramdisk
    ram_disk = Ram()

    # Set address to example byte
    ram_disk[address] = byte

    # check address was set
#    print(ram_disk.get_byte(address))

    # clear ram
    ram_disk.reset()

    # check address was set to 0x00
#    print(ram_disk.get_byte(address))

    # Success if byte at given address is 0x00
    assert ram_disk[address] == 0x00
