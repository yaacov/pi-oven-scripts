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
from collections import deque

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
temp_trend = deque()

# State variables.
state = {
    "set_temp": 0,
    "set_light": False,
    "set_fan": False,
    "set_top": False,
    "set_bottom": False,
    "set_back": False,
    "timer": False,
    "timer_start": int(time.time()),
    "timer_minutes": 0,
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

    # Check timer.
    sec_passed = int(time.time()) - _state["timer_start"]
    timer_left = _state["timer_minutes"] - int(sec_passed / 60.0)
    if _state["timer"] and timer_left <= 0:
        # Turn heating off
        _state["top"] = False
        _state["bottom"] = False
        _state["back"] = False

    # Set back fan, must turn fan on when using back heating.
    if _state["back"]:
        _state["fan"] = True
    else:
        _state["fan"] = _state["set_fan"]

    # Set light
    _state["light"] = _state["set_light"]

    # Set oven.
    set(_state)


def set_timer(minutes):
    """
    Set timer to N minutes from now.

    minutes = 0 => set timer to manual.
    minutes > 0 => set timer to N minutes from now.
    """
    if minutes == 0:
        state["timer"] = False

    # Check for valid minutes value.
    if minutes > 0:
        state["timer"] = True
        state["timer_minutes"] = minutes
        state["timer_start"] = int(time.time())

    return


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


def get_trend():
    """
    Get temp trend
    """
    return list(temp_trend)


def get_hw():
    """
    Get oven hardware state.
    """
    # Get device temperature.
    if BOARD == "PC":
        temp = mock_temp()

    if BOARD == "OVEN":
        data = bytearray(2)
        with dev["spi_device"] as device:
            device.readinto(data)

        word = (data[0] << 8) | data[1]
        temp = (word >> 3) / 4.0

    # Update timer state.
    timer_left = 0
    if state["timer"]:
        sec_passed = int(time.time()) - state["timer_start"]
        timer_left = state["timer_minutes"] - int(sec_passed / 60.0)
        if timer_left < 0:
            timer_left = 0

    # Update temp trend.
    timestamp = int(time.time())
    temp_trend.append({"time": timestamp, "temp": temp})
    if len(temp_trend) > 10:
        temp_trend.popleft()

    # Relays are normally open:
    #   False => ON
    #   True  => OFF
    _state = {
        "temp": int(temp),

        "cooling": not dev["cooling"].value,
        "fan": not dev["fan"].value,
        "light": not dev["light"].value,

        "top": not dev["top"].value,
        "bottom": not dev["bottom"].value,
        "back": not dev["back"].value,

        "timer_left": timer_left,
    }

    # Return state.
    logging.info("state: %s", json.dumps(_state))
    return _state


def mock_temp():
    """
    Mock temperature for devices without sensors.
    """
    # Some coafisionts.
    room_temp = 20.0
    e_to_c = 0.02
    lose_r = 180.0
    back_e = 2.0
    bottom_e = 3.0
    top_e = 3.0

    # If we do not have enough data, return room temp.
    if len(temp_trend) != 10:
        return room_temp

    # Get current de / dt in energy units.
    e_diff = (temp_trend[9]["temp"] - temp_trend[9]["temp"]) / e_to_c

    # Get lose energy.
    e_diff = e_diff - (temp_trend[9]["temp"] - room_temp) / e_to_c / lose_r

    # Get input energy.
    if not dev["top"].value:
        e_diff = e_diff + top_e
    if not dev["bottom"].value:
        e_diff = e_diff + bottom_e
    if not dev["back"].value:
        e_diff = e_diff + back_e

    # Return last temp + energy diff in deg c.
    return temp_trend[9]["temp"] + e_diff * e_to_c
