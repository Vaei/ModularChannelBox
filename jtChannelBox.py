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
# ------------------------------------------------------------------------ #
# This license covers all scripts included with this script that are
#  prefixed with jtChannelBox
# ------------------------------------------------------------------------ #
# To request a commercial license please contact me via my email address:
# jaredtaylor.99@gmail.com
# ------------------------------------------------------------------------ #

import maya.cmds as cmds
import maya.mel as mel
from functools import partial
import jtChannelBox_Commands_System as sysCmd

# reload(sysCmd)

'''
Modular channel box for use in your own scripts or a customized channel box to fit your needs. If you need to modify anything, consult the included documentation.
'''


# ------------------------------------------------------------------------ #
# REPORTING BUGS:
# ------------------------------------------------------------------------ #
# You are encouraged to report any bugs to the email address provided at
# the top of this file. I would appreciate it very much!
#
# If reporting a bug, please include any error messages from Maya which
# should include a file name, line number and error type.
# ------------------------------------------------------------------------ #

# ------------------------------------------------------------------------ #
# DIFFERENCES : Between this and default Maya channelbox
# ------------------------------------------------------------------------ #
# - Command result output may differ including Undo / Redo output
# - Icons above menubar always enabled since they can always affect interaction
# - Extra tooltips have been added
# - Option box added in the freeze submenu to create a useful dialog, try it out
# - Assets / Container options are omitted - For this to change there would
#       have to be a lot of demand
# - Settings that maintain their state will not reset when closing or
#       re-opening maya
# - "Show" menu in the default Maya channel box was prone to error
#       and (subjectively) impractical, and has been redesigned - feedback
#       is welcome and encouraged
# ------------------------------------------------------------------------ #

class ChannelBox(object):
    def __init__(self, layout, menu_module, state_file, persistent_state):
        # PARAMETERS:
        # layout         : The layout that contains this channel box, eg. cmds.frameLayout()
        # menu_module     : String containing module name with menu variables, eg. "jtchannelBox_Menu_Default"
        # state_file      : String containing file name for saved states - Does not have to exist,
        #                    eg. "jtchannelBox_State_Default" - Will be created alongside this script (same folder)
        # saveState      : Boolean value whether to save the state to a file, if False you can specify state_file as ""
        # displayOptions : Array of 3 Boolean values for the following : [Show label on right click menu,
        #                    Hide unavailable items instead of disabling, Show Icons]

        def init_setup(box):
            # ---------------------------------------------------------------#
            # INIT : Restoring Serialized Settings
            # This is where any serialized values are restored when creating
            # the channel box
            # ---------------------------------------------------------------#
            try:  # read the state file if it exists
                sysCmd.channelbox_pickle_read_state(box)
            except IOError:  # create if it doesn't
                sysCmd.channelbox_pickle_write_state(box)

            for key, value in box.saved_states.iteritems():  # restore our channelbox states from saved data
                if value[1] == 1:
                    if key == "hyperbolic":
                        cmds.channelBox(box.channelbox, e=1, hyperbolic=value[0])

                    if key == "showNamespace":
                        cmds.channelBox(box.channelbox, e=1, showNamespace=value[0])

                    if key == "assetsShowTop":
                        cmds.channelBox(box.channelbox, e=1, containerAtTop=value[0])

                    if key == "changePrecision":
                        cmds.channelBox(box.channelbox, e=1, pre=value[0])

                    if key == "fieldWidth":
                        cmds.channelBox(box.channelbox, e=1, fieldWidth=value[0])

                    if key == "namesState":
                        if value[0] == 1:
                            cmds.channelBox(box.channelbox, e=1, ln=1, nn=1)
                        elif value[0] == 2:
                            cmds.channelBox(box.channelbox, e=1, ln=1, nn=0)
                        else:
                            cmds.channelBox(box.channelbox, e=1, ln=0, nn=0)

                    if key == "speedState":
                        if value[0] == 1:
                            cmds.channelBox(box.channelbox, e=1, speed=0.1)
                        elif value[0] == 2:
                            cmds.channelBox(box.channelbox, e=1, speed=1)
                        else:
                            cmds.channelBox(box.channelbox, e=1, speed=10)

                    if key == "manipsState":
                        if value[0] == 1:
                            cmds.channelBox(box.channelbox, e=1, useManips="none")
                        elif value[0] == 2:
                            cmds.channelBox(box.channelbox, e=1, useManips="invisible")
                        else:
                            cmds.channelBox(box.channelbox, e=1, useManips="standard")

            if self.saved_states["showIcons"][0]:
                cmds.formLayout(box.symbol_layout, e=1, m=1)
                for key in box.symbols:
                    box.sym["update"](box, key)
            else:  # don't need the layout taking up space if not drawing buttons
                cmds.formLayout(box.symbol_layout, e=1, m=0)

        # ---------------------------------------------------------------#
        # CORE SYSTEM : Modify at own risk
        # ---------------------------------------------------------------#
        with sysCmd.Undo(0):  # prevents the creation of this UI being placed in the undo queue
            try:
                _menu = __import__(menu_module, globals(), locals(), [],
                                   -1)  # __import__ used instead of import to allow module provided as string
                reload(_menu)
            except RuntimeError:
                cmds.error("Menu failed to load. Files are missing or parameters are set incorrectly. Exiting.")

            self.state_file = state_file  # file containing menu states
            self.state_persist = persistent_state

            self.menus = _menu.menus  # menu dict from given file
            self.sym = _menu.symbol_commands  # dict containing commands for symbol buttons (icon bar)

            self.saved_states = _menu.saved_states  # menu states from given file
            self.menu_jobs = _menu.jobIDs  # script job IDs from given file
            self.filter = cmds.itemFilterAttr()  # filter created within class as with self so everything can access it
            self.filter_items = []  # all-accessible filtered pre-defined attributes
            self.filter_attrs = {}  # all-accessible filtered user-defined attributes

            # copy the default state of anything to be serialized for resetting later if user wants
            self.menu_default_states = {k: v for k, v in _menu.saved_states.iteritems() if v[1] == 1}
            self.symbols = {}  # saved symbolButton elements for accessing later.

            # Layouts
            self.layout = cmds.formLayout(p=layout)  # root layout containing all other layouts
            self.symbol_layout = cmds.formLayout(
                p=self.layout)  # layout containing the 3 symbol buttons (manipulator, speed, hyperbolic)
            self.menubar_layout = cmds.menuBarLayout(p=self.layout)
            self.channelbox = cmds.channelBox(p=self.layout)

            cmds.formLayout(self.layout, e=1, attachForm=[
                (self.symbol_layout, "top", 0), (self.symbol_layout, "right", 0),
                (self.channelbox, "right", 0), (self.channelbox, "bottom", 0),
                (self.channelbox, "left", 0), (self.menubar_layout, "left", 0),
                (self.menubar_layout, "right", 0)],
                            attachControl=[
                                (self.menubar_layout, "top", 0, self.symbol_layout),
                                (self.channelbox, "top", 0, self.menubar_layout)]
                            )

            # Initialize
            self.re_init = init_setup  # For resetting attributes via menu. note: storing the function itself, not a result
            init_setup(self)

            channelbox_symbols(self)
            channelbox_setup(self, "Channels", "Edit")


# ---------------------------------------------------------------#
# MODIFYABLE SYSTEM : 
# If you want more features, you may want to add things here
# ---------------------------------------------------------------#

def channelbox_setup(box, pop_menu, pop_ctrl_modifier, *args):
    # -----------------------------------------------------------------------------------#
    # MENU INIT : Initial Menu Setup
    # If you want to add custom menus that use data in a way that isn't default,
    # behaviour you can add them here for your menus by adding conditionals on the
    # 'name' variable during the for loop on box.menus
    # -----------------------------------------------------------------------------------#
    for name, menuItems in box.menus.iteritems():
        if not name == "Objects":  # object menu is unique and based on list of selected objects, need custom creation
            menu = cmds.menu(l=name, p=box.menubar_layout)  # create the menu
            cmds.menu(menu, e=1, pmc=partial(channelbox_menu_rebuild, box, menu, menuItems,
                                             False))  # add the command to rebuild the menu when opened
        else:  # object menu creation
            menu_object = cmds.menu(l="Objects", p=box.menubar_layout)
            cmds.menu(menu_object, e=1, pmc=partial(channelbox_menu_object, box, menu_object))

    # right click / popup menu creation (different commands are used for a popup)
    menu_pop = cmds.popupMenu(b=3, allowOptionBoxes=1, p=box.channelbox)
    cmds.popupMenu(menu_pop, e=1, pmc=partial(channelbox_menu_rebuild, box, menu_pop, box.menus[pop_menu], True))

    menu_pop = cmds.popupMenu(b=3, ctrlModifier=1, allowOptionBoxes=1,
                              p=box.channelbox)  # right click menu for user holding ctrl when right clicking
    cmds.popupMenu(menu_pop, e=1,
                   pmc=partial(channelbox_menu_rebuild, box, menu_pop, box.menus[pop_ctrl_modifier], True))


# used to check if attributes are selected for menu items specified as disabled when none selected
def channelbox_menu_states(box, item_key, *args):
    # -----------------------------------------------------------------------------------#
    # MENU STATES : For enabling or disabling menu items based on conditions
    # This will determine if our menuItem is enabled or not, if you want to add a
    # custom menu item with different conditions for being enabled you can do it
    # here by returning prior to the 'return result' on the final line
    #
    # For this to function the "_hasEnableConditions" must be set to true/1
    # -----------------------------------------------------------------------------------#

    # ---------------- MANUALLY ADDED CONDITIONS ----------------#
    # Put your enabled/disabled state overrides here, example:
    # if item_key == "keyForManualOverride":
    #   return 0 to disable or return 1 to enable
    # -----------------------------------------------------------#
    if item_key == "invertShown":
        return 1 if len(box.filter_attrs) >= 1 or len(box.filter_items) >= 1 else 0

    if item_key == "createFilterSet":
        if len(box.filter_attrs) >= 1 or len(box.filter_items) >= 1:
            return 1
        else:
            return 0

    if item_key == "selectFilterSet":
        if "savedFilters" in box.saved_states and len(box.saved_states["savedFilters"][0]) >= 1:
            return 1
        else:
            return 0

    return channelbox_menu_selected_channels(box)


# ----------------------------------------------------------------------------------- #

# ----------------------------------------------------------------------------------- #
# CUSTOM MENU TYPES : Anything set as a "custom" type in the menu can have it's
# behaviour set here by checking for it's unique key
# ----------------------------------------------------------------------------------- #
def channelbox_menu_custom(box, item_key, item_type, label, command, parent, enabled):
    if item_key == "selectFilterSet":
        m_item = cmds.menuItem(l=label, en=enabled, subMenu=1, p=parent)
        for f in box.saved_states["savedFilters"][0]:
            item = cmds.menuItem(l=f, p=m_item)
            item_ob = cmds.menuItem(l=f, ob=1, p=m_item)
            cmds.menuItem(item, e=1, c=sysCmd.rpartial(command, box, item, item_key))
            cmds.menuItem(item_ob, e=1, c=sysCmd.rpartial(command, box, item_ob, item_key))


# ----------------------------------------------------------------------------------- #

# ----------------------------------------------------------------------------------- #
# CUSTOM MENU "Objects" : Use this also as an example for implementing a custom menu
# ----------------------------------------------------------------------------------- #
def channelbox_command_objectmenu(box, menu, menu_item, m_item, *args):
    state = cmds.menuItem(menu_item, q=1, isOptionBox=1)
    item = cmds.menuItem(menu_item if not state else m_item, q=1, l=1)

    cmds.select(item, deselect=1)
    cmds.select(item, add=1)

    if state:
        mel.eval("editSelected")


def channelbox_menu_object(box, menu, *args):
    cmds.menu(menu, e=1, deleteAllItems=1)

    sel = cmds.ls(os=1)

    if not sel:
        cmds.menuItem(l="Nothing selected", p=menu)
        return

    sel.reverse()
    first = 1

    for i in sel:
        m_item = cmds.menuItem(l=i, p=menu)
        m_item_box = cmds.menuItem(m_item, optionBox=1, p=menu)
        cmds.menuItem(m_item, e=1, c=sysCmd.rpartial(channelbox_command_objectmenu, box, menu, m_item, "select " + i))
        cmds.menuItem(m_item_box, e=1, c=sysCmd.rpartial(channelbox_command_objectmenu, box, menu, m_item_box, m_item,
                                                         "select " + i + " [  ]"))

        if first:
            cmds.menuItem(divider=1, p=menu)
            first = 0


# -----------------------------------------------------------------------------------#

# -----------------------------------------------------------------------------------#
# This is where the menu icons are setup
# You probably don't need to modify this, unless you have your own icons to add
# -----------------------------------------------------------------------------------#
def channelbox_symbols(box, *args):
    # create buttons for each menu icon
    b_manip = cmds.symbolButton(p=box.symbol_layout)
    b_speed = cmds.symbolButton(p=box.symbol_layout)
    b_hyper = cmds.symbolButton(p=box.symbol_layout)
    # attach buttons to form layout
    cmds.formLayout(box.symbol_layout, e=1, attachForm=[
        (b_manip, "top", 0),
        (b_manip, "bottom", 1),
        (b_speed, "top", 0),
        (b_speed, "bottom", 1),
        (b_hyper, "top", 0),
        (b_hyper, "bottom", 1),
        (b_hyper, "right", 2),

    ],
                    attachNone=[
                        (b_manip, "left"),
                        (b_speed, "left"),
                        (b_hyper, "left")
                    ],
                    attachControl=[
                        (b_manip, "right", 2, b_speed),
                        (b_speed, "right", 2, b_hyper)

                    ])

    # add the commands for each button (stored in box.sym)
    cmds.symbolButton(b_manip, e=1, c=sysCmd.rpartial(box.sym["pressed"], box, "manipsState"))
    cmds.symbolButton(b_speed, e=1, c=sysCmd.rpartial(box.sym["pressed"], box, "speedState"))
    cmds.symbolButton(b_hyper, e=1, c=sysCmd.rpartial(box.sym["pressed"], box, "hyperbolic"))

    # store the buttons themselves for updating when changed via menu options instead of button presses
    box.symbols["manipsState"] = b_manip
    box.symbols["speedState"] = b_speed
    box.symbols["hyperbolic"] = b_hyper

    # call their update function on creation to set them to their current states (because data is serialized,
    # may not be default on creation)
    for key in box.symbols:
        box.sym["update"](box, key)


# -----------------------------------------------------------------------------------

# ----------------------------------------
# -- MODIFY BELOW THIS LINE AT OWN RISK --
#       You will break many things
# ----------------------------------------

# --------------------------------------------------------------------------------------
# CORE SYSTEM : This is setup very specifically to NOT require you to modify this part
#
# If you need changes here, feel free to email me at the address provided if you feel
# that they could benefit everyone
# --------------------------------------------------------------------------------------

def channelbox_menu_rebuild(box, menu, menu_items, popup, *args):  # build the menu when a menu is opened
    def menu_counter(items):
        if items[2] is not "":  # if a parent is set then this is an item of the given type
            if items[1] >= items[0]:  # then we've completed the last item for the given type
                items = [0, 0,
                         ""]  # resets the array, clearing parent allows next menu item to know it's not a given type
            else:
                items[1] += 1  # counter for remaining amount of items
        return items

    cmds.menu(menu, e=1, deleteAllItems=1) if popup else cmds.popupMenu(menu, e=1, deleteAllItems=1)

    # initialize required variables
    sub = [0, 0, ""]  # [total submenu items, remaining, submenu parent]
    radio = [0, 0, "", ""]  # [total radio items, remaining, radio parent, radio key]
    radio_key = ""
    last_added_type = ""  #

    if box.saved_states["popupLabel"][0] and popup:  # draw title label on popup menu if desired
        # print [key for key, menu in box.menus.iteritems() if menu == menu_items]
        # print menu
        cmds.menuItem(l=[key for key, value in box.menus.iteritems() if value == menu_items][0],
                      p=menu)  # Gets the label from the menu key in box.menus by looping through the dict
        # for menu_items identical to the given one
        cmds.menuItem(divider=1, p=menu)

    for key, values in menu_items.iteritems():
        label = values[0]  # display name
        selected_only = values[1]  # only enable if attributes are selected
        item_type = values[2]  # eg default, checkbox, submenu, radio button
        command = values[3]  # function used as command
        tooltip = "" if not len(values) == 5 else values[4]

        enabled = 1  # should enable or disable?
        no_edit = 0  # should add partial command?
        parent = menu  # compensate for adding submenu items to correct parent

        if sub[2] != "":  # submenu counter is active, this item is in a submenu
            parent = sub[2]
        elif radio[2] != "":  # radio counter is active, this item is in a radio collection
            parent = radio[2]

        if selected_only:  # check if this only gets enabled when an attribute is selected
            enabled = channelbox_menu_states(box, key, key)  # check if attribute is selected
            if not enabled and box.saved_states["hideUnavailable"][
                0]:  # if chosen not to display unavailable attributes nothing more needs doing, move on
                continue

        if item_type == "divider":
            if last_added_type != "divider":  # prevent stacking dividers when disabled options are hidden
                cmds.menuItem(divider=1, p=parent)
                last_added_type = item_type
            continue

        if item_type == "custom":
            channelbox_menu_custom(box, key, item_type, label, command, parent, enabled)
            last_added_type = item_type
            continue

        if "radio" in item_type:
            radio[0] = values[3]  # how many following items are put in radio collection
            radio[1] = 0
            m_item = cmds.radioMenuItemCollection(p=parent)
            radio[2] = m_item
            radio_key = key
            last_added_type = item_type
            continue

        if "checkbox" in item_type:
            m_item = cmds.menuItem(l=label, en=enabled, cb=box.saved_states[key][0] if key in box.saved_states else 0,
                                   annotation=tooltip, p=parent)
            if command != "":
                cmds.menuItem(m_item, e=1, c=sysCmd.rpartial(command, box, m_item, key, label))
            no_edit = 1
        elif "submenu" in item_type:
            sub[0] = values[3]  # how many following items are put in submenu
            sub[1] = 0
            m_item = cmds.menuItem(l=label, en=enabled, subMenu=1, p=parent)
            sub[2] = m_item  # set the parent for the submenus created after this
            no_edit = 1
        elif radio[2] is not "":  # radio counter is active
            if radio_key in box.saved_states:
                if radio[0] >= 2:
                    which_radio = radio[1] == box.saved_states[radio_key][0] - 1
                else:
                    which_radio = 0 if box.saved_states[radio_key][0] - 1 == radio[
                        1] else 1  # can't use division on a 0, nor do we need to shift the range for 2 numbers
            else:
                which_radio = 1 if radio[1] == 0 else 0  # no setting, assume the first item is selected by default
            m_item = cmds.menuItem(l=label, en=enabled, radioButton=which_radio, annotation=tooltip, p=parent)
            if command != "":
                cmds.menuItem(m_item, e=1, c=partial(command, box, m_item, key))
            no_edit = 1
        else:
            m_item = cmds.menuItem(l=label, en=enabled, annotation=tooltip, p=parent)
            if item_type == "optionbox":
                m_item2 = cmds.menuItem(m_item, ob=1, p=parent)
                if command != "":
                    cmds.menuItem(m_item2, e=1, c=sysCmd.rpartial(command, box, m_item2, key, label))

        if not no_edit:
            if command != "":
                cmds.menuItem(m_item, e=1, c=sysCmd.rpartial(command, box, m_item, key, label if sub[
                    2] == "" else "> " + label))  # add command after declaration to provide itself as parameter

        sub = menu_counter(sub)
        radio = menu_counter(radio)
        last_added_type = item_type


def channelbox_menu_selected_channels(box):
    obj_list = cmds.channelBox(box.channelbox, q=1, mainObjectList=1)
    attr_list = cmds.channelBox(box.channelbox, q=1, selectedMainAttributes=1)

    if obj_list and attr_list and len(obj_list) > 0 and len(attr_list) > 0:
        return 1

    obj_list = cmds.channelBox(box.channelbox, q=1, shapeObjectList=1)
    attr_list = cmds.channelBox(box.channelbox, q=1, selectedShapeAttributes=1)

    if obj_list and attr_list and len(obj_list) > 0 and len(attr_list) > 0:
        return 1

    obj_list = cmds.channelBox(box.channelbox, q=1, historyObjectList=1)
    attr_list = cmds.channelBox(box.channelbox, q=1, selectedHistoryAttributes=1)

    if obj_list and attr_list and len(obj_list) > 0 and len(attr_list) > 0:
        return 1

    obj_list = cmds.channelBox(box.channelbox, q=1, outputObjectList=1)
    attr_list = cmds.channelBox(box.channelbox, q=1, selectedOutputAttributes=1)

    if obj_list and attr_list and len(obj_list) > 0 and len(attr_list) > 0:
        return 1

    return 0
