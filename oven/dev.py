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
    import busio
    import digitalio
    import json
    import logging
    import time

    from adafruit_bus_device.spi_device import SPIDevice

    FAN = digitalio.DigitalInOut(board.D2)
    FAN.direction = digitalio.Direction.OUTPUT
    FAN.value = True

    COOLING = digitalio.DigitalInOut(board.D3)
    COOLING.direction = digitalio.Direction.OUTPUT
    COOLING.value = True

    LIGHT = digitalio.DigitalInOut(board.D4)
    LIGHT.direction = digitalio.Direction.OUTPUT
    LIGHT.value = True

    TOP = digitalio.DigitalInOut(board.D17)
    TOP.direction = digitalio.Direction.OUTPUT
    TOP.value = True

    BACK = digitalio.DigitalInOut(board.D27)
    BACK.direction = digitalio.Direction.OUTPUT
    BACK.value = True

    BOTTOM = digitalio.DigitalInOut(board.D22)
    BOTTOM.direction = digitalio.Direction.OUTPUT
    BOTTOM.value = True

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


def oven_get():
    """
    Get oven state.
    """
    if BOARD == "PC":
        return {"temp": 20}

    data = bytearray(2)
    with SPICDVICE as dev:
        dev.readinto(data)

    word = (data[0] << 8) | data[1]
    temp = int((word >> 3) / 4.0)

    # Relays are normally open:
    #   Flase => ON
    #   True  => OFF
    state = {
        "temp": temp,
        
        "cooling": not COOLING.value,
        "fan": not FAN.value,
        "light": not LIGHT.value,

        "top": not TOP.value,
        "bottom": not BOTTOM.value,
        "back": not BACK.value,
    }

    # Return state.
    logging.info("state: %s", json.dumps(state))
    return state
