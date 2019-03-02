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
oven_interval_sec = 5
temp_min_c = 10
temp_cooling_c = 100
temp_histeresis_c = 10

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
    
    _state = state.get()

    # Get temp.
    t = dev.oven_get_temp()

    # Check for cooling.
    if t > temp_cooling_c:
        _state["cooling"] = True
    if t < (temp_cooling_c - temp_histeresis_c):
       _state["cooling"] = False

    # Set heating elements.
    if _state["set_temp"] > temp_min_c:
        if t > _state["set_temp"]:
            # Turn heating off
            _state["top"] = False
            _state["bottom"] = False
            _state["back"] = False
        
        if t < (_state["set_temp"] - temp_histeresis_c):
            # Turn heating on
            _state["top"] = _state["set_top"]
            _state["bottom"] = _state["set_bottom"]
            _state["back"] = _state["set_back"]
    else:
        # Turn heating off
        _state["top"] = False
        _state["bottom"] = False
        _state["back"] = False

    # Set light.
    _state["light"] = _state["set_light"]

    # Set back fan, must turn fan on when using back heating.
    if _state["back"]:
        _state["fan"] = True
    else:
        _state["fan"] = _state["set_fan"]
    
    # Set oven.
    dev.oven_set(_state)

@app.route('/status')
def status():
    _state = state.get()

    # Get temp.
    t = dev.oven_get_temp()
    _state["temp"] = t

    return jsonify(_state)

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
        
            if value == "high":
                v = 250
            if value == "low":
                v = 180

        if v >= 0 and v <= 500:
            error = {"error": None}
            state.write_key("set_temp", int(v))
        else:
            error = {
                "error": "can't set temp to " + value,
            }

    if d in ["fan", "light", "top", "bottom", "back"]:
        t = value in ['on', 'On', '1']
        f = value in ['off', 'Off', '0']
        field = "set_" + d

        if t:
            error = {"error": None}
            state.write_key(field, True)
        if f:
            error = {"error": None}
            state.write_key(field, False)

    if error["error"] != None:
        return jsonify(error)

    _state = state.get()

    # Get temp.
    t = dev.oven_get_temp()
    _state["temp"] = t

    return jsonify(_state)

CORS(app)

if __name__ == '__main__':
    app.config.from_object(Config())

    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()

    app.run(host='0.0.0.0')