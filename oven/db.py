"""
Persistant value store for oven.
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


class DB():
    """
    Persist oven state.
    """

    def __init__(self):
        state = {
            "cooling": False,
            "fan": False,
            "light": False,

            "top": False,
            "bottom": False,
            "back": False,

            "set_temp": 0,
            "set_fan": False,
            "set_top": False,
            "set_bottom": False,
            "set_back": False,
        }
        self.write(state)

    @staticmethod
    def get():
        """
        Get oven state struct.
        """
        with open('oven.json') as json_data:
            data = json.load(json_data)
            return data

        return {"error": "can't readn data"}

    @staticmethod
    def write(state):
        """
        Write oven state struct.
        """
        logging.warning('writing state to file')

        with open('oven.json', 'w') as json_data:
            json.dump(state, json_data)

    def write_key(self, key, value):
        """
        Write one key if valid and changed.
        """
        if key not in ["cooling", "fan", "light", "top", "bottom", "back", "set_temp", "set_fan", "set_top", "set_bottom", "set_back"]:
            logging.info("can't set unknown key %s", key)

            return

        state = self.get()
        if state[key] != value:
            logging.info('%s set to %s', key, value)

            state[key] = value
            self.write(state)
