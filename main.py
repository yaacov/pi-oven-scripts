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

app = Flask(__name__)


class Config():
    JOBS = [
        {
            'id': 'oven',
            'func': 'oven:dev.run',
            'trigger': 'interval',
            'seconds': 1,
        }
    ]


def get_dev(args):
    """
    Get the device name from the url query.
    """
    for d in ["light", "fan", "top", "bottom", "back", "temp"]:
        if d in args:
            return d

    return None


@app.route('/status')
def status():
    # Get state.
    return jsonify(dev.get())


@app.route('/set')
def set():
    error = None

    d = get_dev(request.args)
    value = request.args.get(d)

    if d == "temp":
        try:
            v = float(value)
        except:
            v = -1

        if v >= 0 and v < 500:
            dev.write_key("set_temp", int(v))
        else:
            error = {
                "error": "can't set temp to " + str(value),
            }

    elif d in ["light", "fan", "top", "bottom", "back"]:
        t = value in ['on', 'On', '1', 'true', 'True', 't', 'T']
        f = value in ['off', 'Off', '0', 'false', 'False', 'f', 'F']
        field = "set_" + d

        if t:
            dev.write_key(field, True)
        elif f:
            dev.write_key(field, False)
        else:
            error = {
                "error": "can't set " + d + " to " + str(value),
            }
    else:
        error = {
            "error": "can't parse request",
        }

    # Check for errors.
    if error:
        return jsonify(error)

    # Get state.
    return jsonify(dev.get())


CORS(app)

if __name__ == '__main__':
    app.config.from_object(Config())

    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()

    app.run(host='0.0.0.0')
