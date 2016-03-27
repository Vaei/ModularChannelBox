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
# This license covers all scripts included with this script that are
#  prefixed with jtChannelBox
# --------------------------------------------------------------------------#
# To request a commercial license please contact me via my email address:
# jaredtaylor.99@gmail.com
# --------------------------------------------------------------------------#


"""
Interface with saved menu sets to house the jtChannelBox module
"""

import maya.cmds as cmds
import maya.mel as mel
import base64  # for encoding/decoding scene-specific data to save menu sets
from functools import partial
from collections import OrderedDict
import jtChannelBox as CBox
import jtChannelBox_Commands_System as Sc  # borrowing Undo() class to use- with Undo(0):

reload(CBox)

try:
    import cPickle as pickle
except:
    import pickle


def persistent_menu_sets():
    menus = data_load()
    persist = []

    # to add a module in a subfolder use subfoldername.modulename and ensure there is an
    #  __init__.py file present with the module
    def add(name, module):
        menus[name] = module
        persist.append(name)

        # add persistent menus here - these will be automatically added to your

    # new scenes - non-persistent menus are per-scene
    add("Modelling", "jtChannelBox_Menu_Modelling")
    add("Rigging", "jtChannelBox_Menu_Rigging")
    add("Animation", "jtChannelBox_Menu_Animation")
    add("Default", "jtChannelBox_Menu_Default")

    data_save(persist, "menuSets_persist")
    data_save(menus)


def layer_editor_reset():  # re-parent layer editor to default maya channelbox
    layout_pane = mel.eval("$tmpvar=$gChannelsLayersPane")
    layer_editor_form = mel.eval("$tmpvar=$gLayerEditorForm")

    if layer_editor_form:
        cmds.formLayout(layer_editor_form, e=1, parent=layout_pane)


def data_save(_dict, key="menuSets"):  # encode data into a string to add to fileInfo (accepts only string)
    _str = pickle.dumps(_dict)
    _encode = base64.b64encode(_str)
    cmds.fileInfo(key, _encode)


def data_load(key="menuSets"):  # decode data from fileInfo
    _data = cmds.fileInfo(key, q=1)
    if _data:
        _decoded = base64.b64decode(_data[0])
        return pickle.loads(_decoded)
    else:
        return OrderedDict()


def currentset_get():  # the menu set that is currently in use
    try:
        return cmds.fileInfo("menuSet", q=1)[0]
    except:
        return None


def currentset_set(key):
    cmds.fileInfo("menuSet", key)


def menuset_add(_box_ui, menu, *args):  # interface for adding menu sets
    print "\n"  # in case of previous warnings/errors, this will clear the script output to avoid confusion

    def button_add(_name_tf, _path_tf, _b_close, *args):
        key = cmds.textField(_name_tf, q=1, tx=1)
        path = cmds.textField(_path_tf, q=1, tx=1)
        path = path.replace("\\", ".")
        path = path.split(".py")[0]

        if key and path:
            menu_sets = data_load()
            confirm = None
            if key in menu_sets:  # if it exists, ask to overwrite
                confirm = cmds.confirmDialog(title="Confirm Overwrite",
                                             message="Menu Set \"" + key + "\" already exists. Overwrite?",
                                             button=("Overwrite", "Cancel"), icn="warning")

            if confirm is None or confirm == "Overwrite":
                menu_sets[key] = path
                data_save(menu_sets)

                cmds.textField(_name_tf, e=1, tx=None)
                cmds.textField(_path_tf, e=1, tx=None)

                if len(data_load()) == 1:
                    menuset_first_sel(_box_ui, menu)

            print "Success: Menu Set added: \"" + key + "\"\n",

            if _b_close:
                cmds.deleteUI(window)
        elif key:
            cmds.error("module field entry is invalid")
        elif path:
            cmds.error("key field entry is invalid")
        else:
            cmds.error("key and module field entries are invalid")

    def button_browse(_tf, *args):
        _f = cmds.fileDialog2(fm=1, dir=Sc.channelbox_get_path(),
                              caption="Select a .py module containing menus from the same folder or a subfolder"
                                      " (no spaces)",
                              fileFilter="*.py")
        if _f:
            _f = _f[0].replace("/", "\\")
            _f = _f.split(Sc.channelbox_get_path())[-1]

            if " " in _f:
                cmds.error("No spaces are allowed in the subfolder or module names")
            else:
                cmds.textField(_tf, e=1, text=_f)

    if cmds.window("jtChannelBox_UI_MenuAddEdit", exists=1):
        cmds.deleteUI("jtChannelBox_UI_MenuAddEdit")

    window = cmds.window("jtChannelBox_UI_MenuAddEdit", title="Add Menu Set", tlb=1, resizeToFitChildren=1, sizeable=0,
                         p=_box_ui.layout_pane)
    layout = cmds.rowColumnLayout(nc=3, p=window)

    layout_labels = cmds.rowColumnLayout(nr=2, rowOffset=[(1, "bottom", 12)], rowAlign=[(1, "left")], p=layout)
    cmds.text("Name : ", p=layout_labels)
    cmds.text("Module : ", p=layout_labels)

    layout_fields = cmds.rowColumnLayout(nr=2, rowOffset=[(1, "bottom", 3)], p=layout)
    name_tf = cmds.textField(w=130, p=layout_fields)
    layout_path = cmds.rowColumnLayout(nc=2, p=layout_fields)
    path_tf = cmds.textField(w=200, p=layout_path)
    cmds.button(l="...", w=20, h=20, c=partial(button_browse, path_tf), p=layout_path)

    layout_buttons = cmds.rowColumnLayout(nr=2, p=layout)
    cmds.button(l="Add", c=partial(button_add, name_tf, path_tf, 0), p=layout_buttons)
    cmds.button(l="Add / Close", w=80, c=partial(button_add, name_tf, path_tf, 1), p=layout_buttons)

    cmds.showWindow(window)
    cmds.window(window, e=1, wh=(1, 1), rtf=1)


def menuset_edit(_box_ui, key, menu, *args):  # interface for editing menu sets
    print "\n"  # in case of previous warnings/errors, this will clear the script output to avoid confusion

    def button_edit(_name_tf, _path_tf, orig_key, orig_path, *args):
        _key = cmds.textField(_name_tf, q=1, tx=1)
        _path = cmds.textField(_path_tf, q=1, tx=1)
        _path = _path.replace("\\", ".")
        _path = _path.split(".py")[0]

        updatelabel = orig_key == currentset_get()  # need to update the label if it's key changes while selected

        if _key in data_load("menuSets_persist"):
            # prevent over-writing persistent menu sets (behaviour could be considered erroneous)
            cmds.error("Name is in use by a persistent menu set and can not be overwritten."),
            return

        if not updatelabel and _key in data_load().keys():
            confirm = cmds.confirmDialog(title="Confirm Overwrite",
                                         message="Menu Set \"" + _key + "\" already exists. Overwrite?",
                                         button=("Overwrite", "Cancel"), icn="warning")
            if confirm != "Overwrite":
                return

        if _key != orig_key and _path != orig_path:  # replace keys or values where they're no longer identical
            _data = data_load()
            new_data = OrderedDict([(_key, _path) if k == orig_key else (k, v) for k, v in _data.iteritems()])
            data_save(new_data)
        elif _key != orig_key:
            _data = data_load()
            new_data = OrderedDict([(_key, v) if k == orig_key else (k, v) for k, v in _data.iteritems()])
            data_save(new_data)
            _key = _key
        elif _path != orig_path:
            _data = data_load()
            new_data = OrderedDict([(k, _path) if v == orig_path else (k, v) for k, v in _data.iteritems()])
            data_save(new_data)

        if updatelabel:
            menulabel_update(_key, menu)
            currentset_set(_key)

        print "Success: Menu Set name changed from \"" + orig_key + "\" to \"" + _key + "\"\n",

    def button_delete(*args):
        confirm = cmds.confirmDialog(title="Confirm Delete?", message="Menu set \"" + key + "\" will be deleted.",
                                     icn="warning", button=["Delete", "Cancel"])
        if confirm == "Delete":
            _data = data_load()
            _data.pop(key, None)
            data_save(_data)
            if key == currentset_get():
                menuset_first_sel(_box_ui, menu)
            cmds.deleteUI("jtChannelBox_UI_MenuAddEdit")

    def button_browse(tf, *args):
        _f = cmds.fileDialog2(fm=1, dir=Sc.channelbox_get_path(),
                              caption="Select a .py module containing menus from the same folder or a"
                                      " subfolder (no spaces)", fileFilter="*.py")
        if _f:
            _f = _f[0].replace("/", "\\")
            _f = _f.split(Sc.channelbox_get_path())[-1]

            if " " in _f:
                cmds.error("No spaces are allowed in the subfolder or module names")
            else:
                cmds.textField(tf, e=1, text=_f)

    def index_check(_key, _btn_up, _btn_dn):
        _data = data_load()
        max_index = len(_data.keys()) - 1
        index = _data.keys().index(_key)
        cmds.button(_btn_up, e=1, en=index != 0)
        cmds.button(_btn_dn, e=1, en=index != max_index)

    def button_up(_key, _btn_up, _btn_dn, *args):  # get current index + item at current +1 and swap them around
        _data = data_load()
        index = _data.keys().index(_key)
        data_orig = _data.items()[index]
        data_affect = _data.items()[index - 1]

        d1 = OrderedDict(_data.items()[:index - 1])
        d1[data_orig[0]] = data_orig[1]
        d1[data_affect[0]] = data_affect[1]

        d1.update(OrderedDict(_data.items()[index + 1:]))
        data_save(d1)

        index_check(_key, _btn_up, _btn_dn)

    def button_down(_key, _btn_up, _btn_dn, *args):
        _data = data_load()
        index = _data.keys().index(_key)
        data_orig = _data.items()[index]
        data_affect = _data.items()[index + 1]

        d1 = OrderedDict(_data.items()[:index])
        d1[data_affect[0]] = data_affect[1]
        d1[data_orig[0]] = data_orig[1]

        d1.update(OrderedDict(_data.items()[index + 1:]))
        data_save(d1)

        index_check(_key, _btn_up, _btn_dn)

    if cmds.window("jtChannelBox_UI_MenuAddEdit", exists=1):
        cmds.deleteUI("jtChannelBox_UI_MenuAddEdit")

    window = cmds.window("jtChannelBox_UI_MenuAddEdit", title="Edit Menu Set", tlb=1, resizeToFitChildren=1, sizeable=0,
                         p=_box_ui.layout_pane)
    layout = cmds.rowColumnLayout(nc=3, p=window)

    data = data_load()

    layout_labels = cmds.rowColumnLayout(nr=2, rowOffset=[(1, "bottom", 12)], rowAlign=[(1, "left")], p=layout)
    cmds.text("Name : ", p=layout_labels)
    cmds.text("Module : ", p=layout_labels)

    path = data[key]  # restoring path to what the file dialog gives to avoid user confusion
    path = path.replace(".", "\\")
    path += ".py"

    b_enable = key not in data_load("menuSets_persist")  # only allow modification of most elements if not persistent

    layout_fields = cmds.rowColumnLayout(nr=2, rowOffset=[(1, "bottom", 3)], p=layout)
    name_tf = cmds.textField(w=130, en=b_enable, tx=key, p=layout_fields)
    layout_path = cmds.rowColumnLayout(nc=2, p=layout_fields)
    path_tf = cmds.textField(w=200, en=b_enable, tx=path, p=layout_path)
    cmds.button(l="...", en=b_enable, w=20, h=20, c=partial(button_browse, path_tf), p=layout_path)

    layout_buttons = cmds.rowColumnLayout(nr=2, p=layout)
    btn_up = cmds.button(l="^", annotation="Move up in menu", p=layout_buttons)
    btn_dn = cmds.button(l="v", annotation="Move down in menu", p=layout_buttons)
    cmds.button(btn_up, e=1, c=partial(button_up, key, btn_up, btn_dn))
    cmds.button(btn_dn, e=1, c=partial(button_down, key, btn_up, btn_dn))
    cmds.button(l="Edit", en=b_enable, c=partial(button_edit, name_tf, path_tf, key, data_load()[key]),
                           p=layout_buttons)
    cmds.button(l="Delete", en=b_enable, w=80, c=partial(button_delete), p=layout_buttons)

    index_check(key, btn_up, btn_dn)  # ensure the up or down buttons are in correct enable state

    if not b_enable:  # notify users that the menu set they are attempting to edit is persistent
        print "Modifications to persistent sets must be made in this file : " + __file__ + "\n"
        cmds.warning("This menu set is persistent and only the position may be modified via this menu. "
                     "Check script editor for more details.")
        # Modifications to persistent sets must be made in " + __file__)

    cmds.showWindow(window)
    cmds.window(window, e=1, wh=(1, 1), rtf=1)


def menuset_sel(box_ui, key, m_item, menu, *args):
    state = cmds.menuItem(m_item, q=1, isOptionBox=1)
    if state:  # option box used, edit menu set
        menuset_edit(box_ui, key, menu)
    else:  # changing menu set
        data = data_load()
        channelbox_make(box_ui, data[key])
        menulabel_update(key, menu)
        currentset_set(key)


def menuset_first_sel(box_ui, menu):  # change current menu set to the first available
    data = data_load()
    key = None
    if data:
        key = data.keys()[0]
        currentset_set(key)
        channelbox_make(box_ui, data[key])
    else:
        channelbox_make(box_ui)

    menulabel_update(key, menu)


def menulabel_update(key, menu):  # change menu label when changing sets
    data = data_load()
    menu_label = ("Menu Set : " + key)[:34] if data else "Menu Set : None"
    # max character limit before falling off screen is 34
    cmds.menu(menu, e=1, label=menu_label)


def channelbox_make(box_ui, _menu="jtChannelBox_Menu_Modelling"):
    data = data_load()
    exists = 0
    if box_ui.box is not None:
        del box_ui.box
    else:
        key = currentset_get()
        _menu = _menu if not key else data[key]
    if box_ui.menu_layout is not None:
        exists = 1

    # find the key pertaining to this menu to set as current
    value = [key for key, value in data.iteritems() if value == _menu][0] if data else "None"
    currentset_set(value)
    # cbox.ChannelBox parameters : (layout to parent channel box to, name of file containing menus to use,
    # what to name the file created to store persistent states, True/False/1/0 whether to save states or not)
    box_ui.box = CBox.ChannelBox(box_ui.layout_cbox, _menu, "jtChannelBox_State_Custom", 1)
    cmds.formLayout(box_ui.layout_cbox, e=1,
                    attachForm=[(box_ui.box.layout, "left", 1), (box_ui.box.layout, "right", 1),
                                (box_ui.box.layout, "bottom", 3), (box_ui.box.layout, "top", 0)])

    if exists:
        cmds.formLayout(box_ui.layout_cbox, e=1,
                        attachForm=[(box_ui.menu_layout, "bottom", 10), (box_ui.menu_layout, "right", 0),
                                    (box_ui.menu_layout, "left", 0)],
                        attachControl=(box_ui.box.layout, "bottom", 10, box_ui.menu_layout))


class ChannelBoxUI(object):
    def __init__(self):
        def menu_builder(_menu, *args):
            cmds.menu(_menu, e=1, deleteAllItems=1)

            if len(data_load().keys()) == 0:
                persistent_menu_sets()

            menu_sets = data_load()

            for label, path in menu_sets.iteritems():
                m_item = cmds.menuItem(label=label, p=_menu)
                cmds.menuItem(m_item, e=1, c=partial(menuset_sel, self, label, m_item, _menu))
                m_ob = cmds.menuItem(optionBox=1, p=_menu)
                cmds.menuItem(m_ob, e=1, c=partial(menuset_sel, self, label, m_ob, _menu))
            if cmds.menu(_menu, q=1, numberOfItems=1) >= 1:
                cmds.menuItem(divider=1, p=_menu)
            cmds.menuItem(label="Add Menu Set...", c=partial(menuset_add, self, _menu), p=_menu)

        with Sc.Undo(0):  # prevent UI generation being placed in undo queue
            if cmds.dockControl("jtChannelBox_UI_Dock", exists=1):
                layer_editor_reset()
                cmds.deleteUI("jtChannelBox_UI_Dock")
            if cmds.window("jtChannelBox_UI_Window",exists=1):
                # in case of errors the window can remain while the dock doesn't
                layer_editor_reset()
                cmds.deleteUI("jtChannelBox_UI_Window")

            self.window = cmds.window("jtChannelBox_UI_Window", title="Channel Box", w=100, retain=0)

            # layouts
            self.layout_pane = cmds.paneLayout(configuration="horizontal2", paneSize=(1, 100, 75), p=self.window)
            self.layout_cbox = cmds.formLayout(p=self.layout_pane)
            self.layout_layers = cmds.formLayout(p=self.layout_pane)

            persistent_menu_sets()

            # make channel box
            self.box = None
            self.menu_layout = None
            channelbox_make(self)
            currentset = currentset_get()

            self.menu_layout = cmds.menuBarLayout(p=self.layout_cbox)
            menu = cmds.menu(p=self.menu_layout)
            cmds.menu(menu, e=1, pmc=partial(menu_builder, menu))

            menulabel_update(currentset, menu)

            cmds.formLayout(self.layout_cbox, e=1,
                            attachForm=[(self.menu_layout, "bottom", 10), (self.menu_layout, "left", 0),
                                        (self.menu_layout, "right", 0)],
                            attachControl=[(self.box.layout, "bottom", 10, self.menu_layout)])

            # take layer editor from default maya channelbox
            layereditor_form = mel.eval("$tmpvar=$gLayerEditorForm")
            if layereditor_form:
                cmds.formLayout(layereditor_form, e=1, parent=self.layout_layers)
                cmds.formLayout(self.layout_layers, e=1, attachForm=[
                    (layereditor_form, "top", 0),
                    (layereditor_form, "left", 0),
                    (layereditor_form, "bottom", 0),
                    (layereditor_form, "right", 0)
                ])

            # dock control
            cmds.dockControl("jtChannelBox_UI_Dock", l="Channel Box", width=220, sl="vertical", area="right",
                             content=self.window, retain=0, allowedArea=["right", "left"],
                             cc=layer_editor_reset)  # Make window dockable
            cmds.evalDeferred(lambda *args: cmds.dockControl("jtChannelBox_UI_Dock", e=1, r=1))  # Window to front
