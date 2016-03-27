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
# --------------------------------------------------------------------------
# To request a commercial license please email me at my address:
# jaredtaylor.99@gmail.com
# --------------------------------------------------------------------------

from collections import OrderedDict
import jtChannelBox_Commands_Default as cbc

reload(cbc)

# --------------------------------------------------------------------------
#                             HELPER FUNCTIONS                             
#                          Used for menu creation                          
# --------------------------------------------------------------------------
# Variables used for helper functions
divider_step = [
    0]  # as list containing one int, because list is mutable and therefore passed by reference (so function can
# directly affect it without setting the variable)
menu_step = [0,
             "genericKey"]  # the key built off this becomes "genericKey_0", +1 is added to the 0 each time, it's
#  used to generate unique keys


# --------------------------------------------------------------------------
# Helper function for creating dividers.
# USAGE: divider(menu_name)
def divider(_menu, step=divider_step):
    _menu["divider_" + str(step[0])] = ["", 0, "divider", ""]
    step[0] += 1


# --------------------------------------------------------------------------
# Helper function for creating menu items.
# USAGE:
# _menu : this is the OrderedDict storing the menu
# _label : the label for the menu item that the user sees on the menu
# _hasEnableConditions : if 0/False will always be available, if 1/True then will have conditions to meet before being
#  enabled, by default this is whether an
#     attribute is selected or not, you can overwride it in jtChannelBox.py function channelBox_Menu_States
# _type : various types are available and will be listed after the definition below, however for a default menu item
# simply enter "" with nothing in the string (empty string)
# _command : the function that is executed when the menu item is pressed
# _tooltip : (optional if no _key entered) this is assigned a default value of "" which equates to no tooltip, it is
#  optional unless you enter a menu key
# _key : (optional) set a custom menu key, only required if you need to refer to the menu item later, will always need
#  this for a checkbox or optionbox to query
#     the state or when there's a corresponding variable attached in saved_states, if you enter a key, you must also
#  enter a tooltip (can simply be "" for no tooltip)
#     or the system will think the key is the tooltip

# Without using the function it would be: menu_channels["keyItem"] = ["Key Selected", 1, "", cbc.channelbox_command_
# keyItem]
# With the function the equivelant is: menu(menu_channels, "Key Selected", 1, "", cbc.channelbox_command_keyItem) -
# but the key will be set automatically to genericKey_0, which is OK,
#   we don't need to refer back to this menu item

# all KEYS must be UNIQUE per dict in python. This function handles it for you unless you need a specific key.
# Duplicate keys will be excluded/ignored.

def menu(_menu, _label, _has_enable_conditions, _type, _command, _tooltip="", _key=menu_step):
    key = _key[1] + "_" + str(_key[0])  # build key based off menu_step
    if _key is menu_step:  # check if no custom key entered, increment step if true
        _key[0] += 1
    else:  # custom key was entered, use that instead
        key = _key
    _menu[key] = [_label, _has_enable_conditions, _type, _command, _tooltip if _tooltip is not "" else None]


# TYPES for _type:
#   "checkbox" : can be enabled or disabled with a box to the left of the item, you will need to set a custom key and
#  add it also to the saved_states
#   "optionbox" : has a secondary function that is used when clicking the option box, which is placed to the right of
#  the item, you do not have to set a custom key
#   "submenu" : replace the _command with integer defining how many of the following menu items are placed in this
#  submenu, you do not have to set a custom key
#   "radio" : replace the _command with integer defining how many of following menu items are a part of this radio
# collection, you will need to set a custom key and add it also to the saved_states
#   "custom" : for behaviour that is not defined here, add to the function in jtChannelBox.py called channelBox_Menu
# _Custom for what happens for this specific key, you will need to set a custom key - for example, look at
# "selectFilterSet" and the specified function
#   "divider" : this is also a type, but you would usually use the divider() function instead
# ----------------------End : Helper Functions End--------------------------
# --------------------------------------------------------------------------


# --------------------------------------------------------------------------
#                            MENU ITEMS DICTS                              
#                  This is where you add your own menus                    
# --------------------------------------------------------------------------
#  Read the "USAGE" for the helper functions if you don't know what to do  
# --------------------------------------------------------------------------

# ------------------------------CHANNEL MENU--------------------------------
menu_channels = OrderedDict()
# --------------------------------------------------------------------------
menu(menu_channels, "Key Selected", 1, "", cbc.channelbox_command_keyItem)
menu(menu_channels, "Key All Keyable", 0, "", cbc.channelbox_command_keyAll)
menu(menu_channels, "Breakdown Selected", 1, "", cbc.channelbox_command_breakdown)
menu(menu_channels, "Breakdown All", 0, "", cbc.channelbox_command_breakdownAll)
menu(menu_channels, "Mute Selected", 1, "", cbc.channelbox_command_mute)
menu(menu_channels, "Mute All", 0, "", cbc.channelbox_command_muteAll)
menu(menu_channels, "Unmute Selected", 1, "", cbc.channelbox_command_unmute)
menu(menu_channels, "Unmute All", 0, "", cbc.channelbox_command_unmuteAll)
divider(menu_channels)

menu(menu_channels, "Sync Graph Editor Display", 0, "checkbox", cbc.channelbox_command_syncGraph,
     "Update Graph Editor based on selected channel box entries and set keyframes only on selected entries."
     " Active list is used when there is no channel box selection", "syncGraphEditor")
menu(menu_channels, "Sync Timeline Display", 0, "checkbox", cbc.channelbox_command_syncTimeline,
     "Update timeline ticks based on selected channel box entries. Active list is used when there"
     " is no channel box selection", "syncTimeline")
divider(menu_channels)

menu(menu_channels, "Cut Selected", 1, "", cbc.channelbox_command_cut, "Cut selected keyframes")
menu(menu_channels, "Copy Selected", 1, "", cbc.channelbox_command_copy, "Copy selected keyframes")
menu(menu_channels, "Paste Selected", 1, "", cbc.channelbox_command_paste, "Paste selected keyframes")
menu(menu_channels, "Delete Selected", 1, "", cbc.channelbox_command_delete, "Delete selected keyframes")
divider(menu_channels)

# menu(menu_channels, "Duplicate Values", 1, "", cbc.channelbox_command_duplicateAttrValues)
# +submenu
menu(menu_channels, "Freeze", 0, "submenu", 4)
menu(menu_channels, "Translate", 0, "", cbc.channelbox_command_freezeTranslate)
menu(menu_channels, "Rotate", 0, "", cbc.channelbox_command_freezeRotate)
menu(menu_channels, "Scale", 0, "", cbc.channelbox_command_freezeScale)
menu(menu_channels, "All", 0, "optionbox", cbc.channelbox_command_freezeAll)
# -submenu
divider(menu_channels)

menu(menu_channels, "Break Connections", 1, "", cbc.channelbox_command_break)
# menu(menu_channels, "Select Connection", 1, "", cbc.channelbox_command_selectConnection)
divider(menu_channels)

menu(menu_channels, "Lock Selected", 1, "", cbc.channelbox_command_lock)
menu(menu_channels, "Unlock Selected", 1, "", cbc.channelbox_command_unlock)
menu(menu_channels, "Hide Selected", 1, "", cbc.channelbox_command_unkeyable)
menu(menu_channels, "Lock and Hide Selected", 1, "", cbc.channelbox_command_lockUnkeyable)
menu(menu_channels, "Make Selected Nonkeyable", 1, "", cbc.channelbox_command_unkeyableDisplayed)
menu(menu_channels, "Make Selected Keyable", 1, "", cbc.channelbox_command_keyable)
divider(menu_channels)

menu(menu_channels, "Add to Selected Layers", 1, "", cbc.channelbox_command_addToLayers,
     "Add selected attributes to selected Animation Layer")
menu(menu_channels, "Remove From Selected Layers", 1, "", cbc.channelbox_command_removeFromLayers,
     "Remove selected attributes from selected Animation Layer")

# --------------------------------EDIT MENU---------------------------------
menu_edit = OrderedDict()
# --------------------------------------------------------------------------
menu(menu_edit, "Graph Editor", 0, "", cbc.channelbox_command_animCurve)
menu(menu_edit, "Expressions...", 1, "", cbc.channelbox_command_expression)
menu(menu_edit, "Set Driven Key...", 1, "", cbc.channelbox_command_driven)
menu(menu_edit, "Channel Control", 0, "", cbc.channelbox_command_channelControlEditor)
menu(menu_edit, "Connection Editor", 0, "", cbc.channelbox_command_connectionEditor)
menu(menu_edit, "Attribute Editor", 0, "", cbc.channelbox_command_attributeEditor)
menu(menu_edit, "Material Attributes", 0, "", cbc.channelbox_command_materialAttributes)
divider(menu_edit)

menu(menu_edit, "Add Attribute", 0, "", cbc.channelbox_command_addAttribute)
menu(menu_edit, "Edit Attribute", 1, "", cbc.channelbox_command_renameAttribute)
menu(menu_edit, "Duplicate Attribute", 1, "", cbc.channelbox_command_duplicateAttr)
menu(menu_edit, "Delete Attributes", 1, "", cbc.channelbox_command_deleteAttributes)
divider(menu_edit)

# menu(menu_edit, "Select Node", 0, "", cbc.channelbox_command_selectNode)
# menu(menu_edit, "Delete Node", 0, "", cbc.channelbox_command_deleteNode)
# menu(menu_edit, "Delete History", 0, "", cbc.channelbox_command_deleteHistory)
# +submenu
menu(menu_edit, "Settings", 0, "submenu", 10)
# +radio
menu(menu_edit, "", 0, "radio", 2, "", "speedState")
menu(menu_edit, "Slow", 0, "", cbc.channelbox_command_setSpeed, "Channel box attributes move in increments of 0.1",
     "speedSlow")
menu(menu_edit, "Medium", 0, "", cbc.channelbox_command_setSpeed, "Channel box attributes move in increments of 1.0",
     "speedMedium")
menu(menu_edit, "Fast", 0, "", cbc.channelbox_command_setSpeed, "Channel box attributes move in increments of 10.0",
     "speedFast")
# -radio
divider(menu_edit)
menu(menu_edit, "Hyperbolic", 0, "checkbox", cbc.channelbox_command_setHyperbolic,
     "Switch between increments acting as linear (unchecked) or curve-based", "hyperbolic")
divider(menu_edit)
menu(menu_edit, "Show Namespace", 0, "checkbox", cbc.channelbox_command_setNamespace, "", "showNamespace")
divider(menu_edit)
# +radio
menu(menu_edit, "", 0, "radio", 2, "", "manipsState")
menu(menu_edit, "No Manips", 0, "", cbc.channelbox_command_setManip, "", "noManips")
menu(menu_edit, "Invisible Manips", 0, "", cbc.channelbox_command_setManip, "", "invisibleManips")
menu(menu_edit, "Standard Manips", 0, "", cbc.channelbox_command_setManip, "", "standardManips")
# -radio
divider(menu_edit)
menu(menu_edit, "Change Precision...", 0, "", cbc.channelbox_command_precision,
     "How many floating point values are displayed in the Channel Box", "changePrecision")
menu(menu_edit, "Reset to Default", 0, "", cbc.channelbox_command_reset)
# -submenu, +submenu
menu(menu_edit, "Channel Names", 0, "submenu", 3)
# +radio
menu(menu_edit, "", 0, "radio", 3, "", "namesState")
menu(menu_edit, "Nice", 0, "", cbc.channelbox_command_setChannelName, "", "nameNice")
menu(menu_edit, "Long", 0, "", cbc.channelbox_command_setChannelName, "", "nameLong")
menu(menu_edit, "Short", 0, "", cbc.channelbox_command_setChannelName, "", "nameShort")

# -------------------------------SHOW MENU----------------------------------
menu_show = OrderedDict()
# --------------------------------------------------------------------------
# +submenu
menu(menu_show, "Attributes", 0, "submenu", 8)
menu(menu_show, "Driven by Anim Curve", 0, "checkbox", cbc.channelbox_command_filter_itemCB, "", "attr_animCurve")
menu(menu_show, "Driven by Expression", 0, "checkbox", cbc.channelbox_command_filter_itemCB,
     "View->Show Results in Graph Editor must be on to see curves driven by expressions", "attr_expression")
menu(menu_show, "Driven by Driven Key", 0, "checkbox", cbc.channelbox_command_filter_itemCB, "", "attr_drivenKey")
menu(menu_show, "Scale", 0, "checkbox", cbc.channelbox_command_filter_itemCB, "", "attr_scale")
menu(menu_show, "Rotate", 0, "checkbox", cbc.channelbox_command_filter_itemCB, "", "attr_rotate")
menu(menu_show, "Translate", 0, "checkbox", cbc.channelbox_command_filter_itemCB, "", "attr_translate")
menu(menu_show, "Scale Rotate Translate", 0, "checkbox", cbc.channelbox_command_filter_itemCB, "",
     "attr_scaleRotateTranslate")
menu(menu_show, "User Defined", 0, "checkbox", cbc.channelbox_command_filter_itemCB,
     "No effect if there are no user-defined attributes present", "attr_userDefined")
# -submenu
menu(menu_show, "Isolate Selected", 0, "optionbox", cbc.channelbox_command_isolateAttr, "", "selectAttr")
menu(menu_show, "Invert Shown", 1, "checkbox", cbc.channelbox_command_filter_invertShown,
     "Toggle between isolating/hiding", "invertShown")
divider(menu_show)

menu(menu_show, "Show All", 0, "", cbc.channelbox_command_filter_filterShowAll, "Reset all attribute filters")
divider(menu_show)

menu(menu_show, "Select Filter Set", 1, "custom", cbc.channelbox_command_selectFilterSet, "", "selectFilterSet")
menu(menu_show, "Create Filter Set...", 1, "", cbc.channelbox_command_createFilterSet, "", "createFilterSet")
divider(menu_show)

menu(menu_show, "Channel Box Settings", 0, "submenu", 4)
menu(menu_show, "Label on Right-Click Menu", 0, "checkbox", cbc.channelbox_command_popupLabel,
     "Show the menu label at top of right-click menu", "popupLabel")
menu(menu_show, "Show Icons", 0, "checkbox", cbc.channelbox_command_showIcons,
     "Show the Manipulator, Speed, and Hyperbolic icons above the menu bar", "showIcons")
menu(menu_show, "Hide Unavailable Menu Items", 0, "checkbox", cbc.channelbox_command_hideUnavailable,
     "Hide unavailable menu options instead of disabling them", "hideUnavailable")
divider(menu_show)
menu(menu_show, "Delete All Stored Settings (Full Reset)", 0, "", cbc.channelbox_command_cboxReset,
     "Re-initialize this channel box at the default state")
# --------------------------------End : Menus-------------------------------
# --------------------------------------------------------------------------

# -------------------------------MENUS DICT---------------------------------
menus = OrderedDict()  # Add your custom menus here too
# --------------------------------------------------------------------------
menus["Channels"] = menu_channels
menus["Edit"] = menu_edit
menus["Objects"] = ""  # this is a custom menu and it's behaviour is defined (differently) in jtChannelBox.py
menus["Show"] = menu_show
# -----------------------------End : Menus Dict-----------------------------
# --------------------------------------------------------------------------


# -----------------------------SYMBOL COMMANDS------------------------------
symbol_commands = {}
# --------------------------------------------------------------------------
symbol_commands["pressed"] = cbc.channelbox_command_Symbol_pressed
symbol_commands["update"] = cbc.channelbox_command_Symbol_update
# ---------------------------End : Symbol Commands--------------------------
# --------------------------------------------------------------------------


# --------------------------------------------------------------------------
#                              SAVED STATES                                
#                   Variables stored by the system                         
#  [x, 0] - First element is the saved data, second element is whether or  #
#  not this state is saved/serialized persistently to disk and restored    
#                  when the script or maya is restarted                    
saved_states = {}
# --------------------------------------------------------------------------
# checkbox states
saved_states["syncGraphEditor"] = [0, 0]
saved_states["syncTimeline"] = [0, 0]
saved_states["hyperbolic"] = [0, 1]
saved_states["showNamespace"] = [1, 1]

# radio button collection states
saved_states["speedState"] = [2, 1]
saved_states["manipsState"] = [3, 1]
saved_states["namesState"] = [1, 1]

# serialized settings
saved_states["changePrecision"] = [3, 1]
saved_states["fieldWidth"] = [65, 1]
saved_states["channelWidth"] = [230, 1]
saved_states["hideUnavailable"] = [0, 1]
saved_states["showIcons"] = [1, 1]
saved_states["popupLabel"] = [1, 1]

# filter checkbox states
saved_states["attr_animCurve"] = [0, 0]
saved_states["attr_expression"] = [0, 0]
saved_states["attr_drivenKey"] = [0, 0]
saved_states["attr_scaleRotateTranslate"] = [0, 0]
saved_states["attr_userDefined"] = [0, 0]
saved_states["attr_scale"] = [0, 0]
saved_states["attr_rotate"] = [0, 0]
saved_states["attr_translate"] = [0, 0]
saved_states["invertShown"] = [0, 0]
saved_states["savedFilters"] = [OrderedDict(), 1]  # Used to store filter sets, you probably don't want to modify this
# ---------------------------End : Saved States-----------------------------
# --------------------------------------------------------------------------


# --------------------------------------------------------------------------
#                            SCRIPT JOB IDs                                
#                   Saved for later removal of script jobs                 
#       Script jobs end automatically when the parent UI is closed         
#  -1 almost always is the default value, -1 means not currently running   
jobIDs = {}  #
# --------------------------------------------------------------------------
jobIDs["syncGraphEditor"] = -1
jobIDs["syncTimeline"] = -1
# --------------------------End : Script Job IDs----------------------------
# --------------------------------------------------------------------------
