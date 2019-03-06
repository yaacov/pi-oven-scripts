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

import json
import logging
import time

try:
    import board
    import busio
    import digitalio

    from adafruit_bus_device.spi_device import SPIDevice

    SPI = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
    CS = digitalio.DigitalInOut(board.D5)

    BOARD = "OVEN"
except (NotImplementedError, ModuleNotFoundError):
    BOARD = "PC"

# Constants.
temp_cooling_c = 100
temp_histeresis_c = 4

# State variables.
state = {
    "set_temp": 0,
    "set_light": False,
    "set_fan": False,
    "set_top": False,
    "set_bottom": False,
    "set_back": False,
}

# Hardware state and variables.
if BOARD == "OVEN":
    # Create global device dictionary.
    dev = {
        "fan": digitalio.DigitalInOut(board.D2),
        "cooling": digitalio.DigitalInOut(board.D3),
        "light": digitalio.DigitalInOut(board.D4),
        "top": digitalio.DigitalInOut(board.D17),
        "back": digitalio.DigitalInOut(board.D27),
        "bottom": digitalio.DigitalInOut(board.D22),

        "spi_device": SPIDevice(SPI, CS),
    }

    # Turn all devices off.
    dev["fan"].direction = digitalio.Direction.OUTPUT
    dev["fan"].value = True
    dev["cooling"].direction = digitalio.Direction.OUTPUT
    dev["cooling"].value = True
    dev["light"].direction = digitalio.Direction.OUTPUT
    dev["light"].value = True
    dev["top"].direction = digitalio.Direction.OUTPUT
    dev["top"].value = True
    dev["back"].direction = digitalio.Direction.OUTPUT
    dev["back"].value = True
    dev["bottom"].direction = digitalio.Direction.OUTPUT
    dev["bottom"].value = True

if BOARD == "PC":
    class mockDev:
        """
        Mocks a raspberry pi device.
        """
        value = True

    # Create mock global device dictionary.
    dev = {
        "fan": mockDev(),
        "cooling": mockDev(),
        "light": mockDev(),
        "top": mockDev(),
        "back": mockDev(),
        "bottom": mockDev(),

        "spi_device": None,
    }


def run():
    """
    A job periodically running and setting new oven state.
    """
    # Get current state.
    _state = get()

    temp = _state["temp"]

    # Check for cooling.
    if temp > temp_cooling_c:
        _state["cooling"] = True
    if temp < (temp_cooling_c - temp_histeresis_c):
        _state["cooling"] = False

    # Set heating elements.
    if temp > _state["set_temp"]:
        # Turn heating off
        _state["top"] = False
        _state["bottom"] = False
        _state["back"] = False

    if temp < (_state["set_temp"] - temp_histeresis_c):
        # Turn heating on
        _state["top"] = _state["set_top"]
        _state["bottom"] = _state["set_bottom"]
        _state["back"] = _state["set_back"]

    # Set back fan, must turn fan on when using back heating.
    if _state["back"]:
        _state["fan"] = True
    else:
        _state["fan"] = _state["set_fan"]

    # Set light
    _state["light"] = _state["set_light"]

    # Set oven.
    set(_state)


def get():
    """
    Get oven full state.
    """
    # Get current state.
    _state = state.copy()

    # Get hardware state.
    hw_state = get_hw()

    # Merge db data with hardware state.
    _state = {**_state, **hw_state}

    return _state


def write_key(key, value):
    """
    Write one key if valid and changed.
    """
    if key not in state.keys():
        logging.info("can't set unknown key %s", key)
        return

    state[key] = value

    return state


def set(_state):
    """
    Set oven state.
    """
    # Relays are normally open:
    #   Flase => ON
    #   True  => OFF
    dev["cooling"].value = not _state["cooling"]
    dev["fan"].value = not _state["fan"]
    dev["light"].value = not _state["light"]

    dev["top"].value = not _state["top"]
    dev["bottom"].value = not _state["bottom"]
    dev["back"].value = not _state["back"]


def get_hw():
    """
    Get oven hardware state.
    """
    # Get device temperature.
    if BOARD == "PC":
        temp = 20

    if BOARD == "OVEN":
        data = bytearray(2)
        with dev["spi_device"] as device:
            device.readinto(data)

        word = (data[0] << 8) | data[1]
        temp = int((word >> 3) / 4.0)

    # Relays are normally open:
    #   False => ON
    #   True  => OFF
    state = {
        "temp": temp,

        "cooling": not dev["cooling"].value,
        "fan": not dev["fan"].value,
        "light": not dev["light"].value,

        "top": not dev["top"].value,
        "bottom": not dev["bottom"].value,
        "back": not dev["back"].value,
    }

    # Return state.
    logging.info("state: %s", json.dumps(state))
    return state
