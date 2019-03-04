"""
Oven device methods.
"""

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

# Copyright (C) Yaacov Zamir (2019) <kobi.zamir@gmail.com>

try:
    import board
    import digitalio
    import busio
    import logging
    from adafruit_bus_device.spi_device import SPIDevice

    FAN = digitalio.DigitalInOut(board.D2)
    FAN.direction = digitalio.Direction.OUTPUT

    COOLING = digitalio.DigitalInOut(board.D3)
    COOLING.direction = digitalio.Direction.OUTPUT

    LIGHT = digitalio.DigitalInOut(board.D4)
    LIGHT.direction = digitalio.Direction.OUTPUT

    TOP = digitalio.DigitalInOut(board.D17)
    TOP.direction = digitalio.Direction.OUTPUT

    BACK = digitalio.DigitalInOut(board.D27)
    BACK.direction = digitalio.Direction.OUTPUT

    BOTTOM = digitalio.DigitalInOut(board.D22)
    BOTTOM.direction = digitalio.Direction.OUTPUT

    SPI = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
    CS = digitalio.DigitalInOut(board.D5)

    SPICDVICE = SPIDevice(SPI, CS)

    BOARD = "OVEN"
except NotImplementedError:
    BOARD = "PC"


def oven_set(state):
    """
    Set oven state.
    """
    if BOARD == "PC":
        return

    # Relays are normally open:
    #   Flase => ON
    #   True  => OFF
    COOLING.value = not state["cooling"]
    FAN.value = not state["fan"]
    LIGHT.value = not state["light"]

    TOP.value = not state["top"]
    BOTTOM.value = not state["bottom"]
    BACK.value = not state["back"]


def _oven_get_temp():
    """
    Get oven temp, once.
    """
    data = bytearray(2)
    with SPICDVICE as dev:
        dev.readinto(data)

    word = (data[0] << 8) | data[1]
    temp = (word >> 3) / 4.0

    return temp


def oven_get_temp():
    """
    Get oven temp.
    """
    _temp = 0
    times = 2

    for i in range(times):
        _temp = _temp + _oven_get_temp()
        time.sleep(0.5)

    temp = _temp / times
    logging.warning("temp:", temp)

    return temp
