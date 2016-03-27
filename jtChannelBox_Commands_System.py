# jtChannelBox - Modular / Customizeable Channel Box
# Copyright (C) 2016 Jared Taylor
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# --------------------------------------------------------------------------#
# To request a commercial license please email me at my address:
# jaredtaylor.99@gmail.com
# --------------------------------------------------------------------------#

import maya.cmds as cmds
import os
from functools import partial

try:
    import cPickle as pickle
except:
    import pickle


# -------------------------------------------------------------------------------- #
#                             CUSTOM SYSTEM METHODS                                #
#                    Define Any Custom Save Behaviour Here                         #
# -------------------------------------------------------------------------------- #


# -------------------------------------------------------------------------------- #
#                     -- MODIFY BELOW THIS LINE AT OWN RISK --                     #
#                           You will break many things                             #
# -------------------------------------------------------------------------------- #

# UNDO() : This is an essential class and should not be modified nor should it be ignored in your own commands
# USAGE 1: For preventing encased code from being placed into the undo queue (such as UI interactions).
#   This is not a boolean, 0 is the only valid parameter.
# with Undo(0):
#   ..code here..
# USAGE 2: Group the encased code into a single undo chunk
# with Undo():
#   ..code here..
class Undo(object):
    def __init__(self, result=1):
        self.result = result

    def __enter__(self):
        if self.result == 0:
            cmds.undoInfo(stateWithoutFlush=0)
        else:
            cmds.undoInfo(openChunk=1)

    def __exit__(self, *exc_info):
        if self.result == 0:
            cmds.undoInfo(stateWithoutFlush=1)
        else:
            cmds.undoInfo(closeChunk=1)


# -------------------------------------------------------------------------------- #

# RPARTIAL() : Subclass of partial used instead to set maya's Undo/Redo output appropriately
class rpartial(partial):
    def __init__(self, *args):
        self.result = args[-1]

    def __repr__(self):
        return self.result


# -------------------------------------------------------------------------------- #

# SaveState : For saving any savedState values to the disk to persist next run
# Using this over channelBox_WriteState allows defining anything that runs prior
#   or following writing data & is more readable in code
def channelbox_save_state(box, *args):
    channelbox_pickle_write_state(box)


# -------------------------------------------------------------------------------- #

# -------------------------------------------------------------------------------- #    
# SERIALIZATION COMMANDS : used for saving states to file, it's unlikely you'll need to call these directly
# -------------------------------------------------------------------------------- #
def channelbox_get_path():
    return os.path.realpath(__file__).split(os.path.basename(__file__))[0]


def channelbox_pickle_write_state(box, *args):
    if not box.state_persist:
        return

    with open(channelbox_get_path() + box.state_file + ".data", "wb") as _file:
        try:
            _dict = {k: v for k, v in box.saved_states.iteritems() if v[1] == 1}
            pickle.dump(_dict, _file)
        except IndexError:
            cmds.error("Could not load state file")


def channelbox_pickle_read_state(box, *args):
    if not box.state_persist:
        return

    with open(channelbox_get_path() + box.state_file + ".data", "rb") as _file:
        try:
            _dict = pickle.load(_file)
            for k, v in box.saved_states.iteritems():
                box.saved_states[k] = _dict[k] if k in _dict and v[1] == 1 else v
        except IOError, EOFError:
            cmds.error("Could not load state file")


def channelbox_pickle_delete_state(box):
    if not box.state_persist:
        return

    os.remove(channelbox_get_path() + box.state_file + ".data")
