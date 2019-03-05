#!/usr/bin/env python3

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

from flask import Flask
from flask import jsonify
from flask import request
from flask_apscheduler import APScheduler
from flask_cors import CORS

from oven import dev
from oven import db

# Consts.
oven_interval_sec = 1
temp_cooling_c = 100
temp_histeresis_c = 4

app = Flask(__name__)
state = db.DB()


class Config():
    JOBS = [
        {
            'id': 'oven',
            'func': 'main:run',
            'trigger': 'interval',
            'seconds': oven_interval_sec,
        }
    ]


def run():
    """
    A job periodically running and setting new oven state.
    """

    # Get current state.
    _state = state.get()

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
    dev.oven_set(_state)


@app.route('/status')
def status():
    # Get state.
    return jsonify(state.get())


@app.route('/set')
def set():
    error = {
        "error": "can't parse request",
    }

    d = request.args.get('dev')
    value = request.args.get('value')

    if d == "temp":
        try:
            v = float(value)
        except:
            v = -1

        if v >= 0 and v <= 500:
            error = {"error": None}
            state.write_key("set_temp", int(v))
        else:
            error = {
                "error": "can't set temp to " + value,
            }

    if d in ["light", "fan", "top", "bottom", "back"]:
        t = value in ['on', 'On', '1', 'true', 'True']
        f = value in ['off', 'Off', '0', 'false', 'False']
        field = "set_" + d

        if t:
            error = {"error": None}
            state.write_key(field, True)
        if f:
            error = {"error": None}
            state.write_key(field, False)

    if error["error"] != None:
        return jsonify(error)

    # Get state.
    return jsonify(state.get())


CORS(app)

if __name__ == '__main__':
    app.config.from_object(Config())

    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()

    app.run(host='0.0.0.0')
