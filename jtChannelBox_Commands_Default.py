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
import maya.mel as mel
from functools import partial
import jtChannelBox_Commands_System as sysCmd


# reload(sysCmd)

# --------------------------------------------  
# --------- CUSTOM USER MENU COMMANDS --------  
# --------------------------------------------  
# ------------- Add your own here ------------  
# --------------------------------------------  


# --------------------------------------------  
# ----------- DEFAULT MENU COMMANDS ----------  
# --------------------------------------------  
# ---------- Duplicate, don't modify ---------  
# --------------------------------------------  


# -------------- CHANNEL MENU -------------  
# -----------------------------------------  
def channelbox_command_keyItem(box, menuItem, key, *args):
    with sysCmd.Undo():
        cmds.channelBox(box.channelbox, e=1,
                        exe=("if( `getAttr -k \"#P.#A\"`||`getAttr -channelBox \"#P.#A\"` )setKeyframe \"#P.#A\";", 1))


def channelbox_command_keyAll(box, menuItem, key, *args):
    with sysCmd.Undo():
        cmds.channelBox(box.channelbox, e=1, exe=("if( `getAttr -k \"#P.#A\"` ) setKeyframe \"#P.#A\";", 0))


def channelbox_command_breakdown(box, menuItem, key, *args):
    with sysCmd.Undo():
        cmds.channelBox(box.channelbox, e=1, exe=("setKeyframe -breakdown true \"#P.#A\";", 1))


def channelbox_command_breakdownAll(box, menuItem, key, *args):
    with sysCmd.Undo():
        cmds.channelBox(box.channelbox, e=1, exe=("setKeyframe -breakdown true \"#P.#A\";", 0))


def channelbox_command_mute(box, menuItem, key, *args):
    with sysCmd.Undo():
        cmds.channelBox(box.channelbox, e=1, exe=("mute \"#P.#A\";", 1))


def channelbox_command_muteAll(box, menuItem, key, *args):
    with sysCmd.Undo():
        cmds.channelBox(box.channelbox, e=1, exe=("mute \"#P.#A\";", 0))


def channelbox_command_unmute(box, menuItem, key, *args):
    with sysCmd.Undo():
        cmds.channelBox(box.channelbox, e=1, exe=("mute -disable -force \"#P.#A\";", 1))


def channelbox_command_unmuteAll(box, menuItem, key, *args):
    with sysCmd.Undo():
        cmds.channelBox(box.channelbox, e=1, exe=("mute -disable -force \"#P.#A\";", 0))


def channelbox_command_syncGraph_scriptJob(box, *args):
    sel_attrs = channelBox_SelectedPlugs(box)
    if sel_attrs:
        cmds.selectionConnection("graphEditor1FromOutliner", e=1, clear=1)
        for attr in sel_attrs:
            cmds.selectionConnection("graphEditor1FromOutliner", e=1, select=attr)


# --
def channelbox_command_syncGraph(box, menuItem, key, *args):
    with sysCmd.Undo(0):
        state = channelBox_Checkbox_Update(box, key, menuItem)
        if not state and box.menu_jobs[key] > 0:
            # if user disabled the option, and ScriptJob is running, kill the ScriptJob
            cmds.scriptJob(k=box.menu_jobs[key])
            box.menu_jobs[key] = -1

        if state:
            mel.eval("GraphEditor;")  # open graph editor
            cmds.channelBox(box.channelbox, e=1, exe=(channelbox_command_animCurve(box, menuItem, key), 0))
            if box.menu_jobs[key] < 0:  # if ScriptJob is not running, start it
                box.menu_jobs[key] = cmds.scriptJob(
                    event=("ChannelBoxLabelSelected", partial(channelbox_command_syncGraph_scriptJob, box)),
                    parent=box.channelbox)


def channelbox_command_syncTimeline(box, menuItem, key, *args):
    with sysCmd.Undo(0):
        state = channelBox_Checkbox_Update(box, key, menuItem)
        playback_slider = mel.eval("$tmpVar=$gPlayBackSlider")  # gets timeslider name
        if state:
            cmds.timeControl(playback_slider, e=1, showKeys=box.channelbox)
            cmds.timeControl(playback_slider, e=1, showKeysCombined=1)
        else:
            cmds.timeControl(playback_slider, e=1, showKeysCombined=0)
            cmds.timeControl(playback_slider, e=1, showKeys="active")


# --
def channelbox_command_cut(box, menuItem, key, *args):
    with sysCmd.Undo():
        cmd = ""
        okay = 0

        def loop(which, _cmd, _okay):
            obj_list = cmds.channelBox(box.channelbox, q=1, mainObjectList=which[0], shapeObjectList=which[1],
                                       historyObjectList=which[2], outputObjectList=which[3])
            attr_list = cmds.channelBox(box.channelbox, q=1, selectedMainAttributes=which[0],
                                        selectedShapeAttributes=which[1], selectedHistoryAttributes=which[2],
                                        selectedOutputAttributes=which[3])

            if obj_list and attr_list:
                _cmd += "cutKey -t \":\" -f \":"
                for channel in attr_list:
                    _cmd += "\" -at \"" + channel
                for obj in obj_list:
                    _cmd += "\" " + obj
                _cmd += ";"
                _okay = 1

            return _cmd, _okay

        cmd, okay = loop([1, 0, 0, 0], cmd, okay)
        cmd, okay = loop([0, 1, 0, 0], cmd, okay)
        cmd, okay = loop([0, 0, 1, 0], cmd, okay)
        cmd, okay = loop([0, 0, 0, 1], cmd, okay)

        if okay == 1:
            print cmd
            print "// Result: " + str(mel.eval(cmd)) + " //"


def channelbox_command_copy(box, menuItem, key, *args):
    with sysCmd.Undo():
        cmd = ""
        okay = 0

        def loop(which, _cmd, _okay):
            obj_list = cmds.channelBox(box.channelbox, q=1, mainObjectList=which[0], shapeObjectList=which[1],
                                       historyObjectList=which[2], outputObjectList=which[3])
            attr_list = cmds.channelBox(box.channelbox, q=1, selectedMainAttributes=which[0],
                                        selectedShapeAttributes=which[1], selectedHistoryAttributes=which[2],
                                        selectedOutputAttributes=which[3])

            if obj_list and attr_list:
                _cmd += "copyKey -t \":\" -f \":"
                for channel in attr_list:
                    _cmd += "\" -at \"" + channel
                for obj in obj_list:
                    _cmd += "\" " + obj
                _cmd += ";"
                _okay = 1

            return _cmd, _okay

        cmd, okay = loop([1, 0, 0, 0], cmd, okay)
        cmd, okay = loop([0, 1, 0, 0], cmd, okay)
        cmd, okay = loop([0, 0, 1, 0], cmd, okay)
        cmd, okay = loop([0, 0, 0, 1], cmd, okay)

        if okay == 1:
            print cmd
            print "// Result: " + str(mel.eval(cmd)) + " //"


def channelbox_command_paste(box, menuItem, key, *args):
    with sysCmd.Undo():
        cmd = ""
        okay = 0
        current_time = cmds.currentTime(q=1)

        def loop(which, _cmd, _okay):
            obj_list = cmds.channelBox(box.channelbox, q=1, mainObjectList=which[0], shapeObjectList=which[1],
                                      historyObjectList=which[2], outputObjectList=which[3])
            attr_list = cmds.channelBox(box.channelbox, q=1, selectedMainAttributes=which[0],
                                       selectedShapeAttributes=which[1], selectedHistoryAttributes=which[2],
                                       selectedOutputAttributes=which[3])

            if obj_list and attr_list:
                _cmd += "pasteKey -connect true -time " + str(current_time) + " "
                for channel in attr_list:
                    _cmd += "-at \"" + channel + "\" "
                for obj in obj_list:
                    _cmd += obj
                _cmd += ";"
                _okay = 1

            return _cmd, _okay

        cmd, okay = loop([1, 0, 0, 0], cmd, okay)
        cmd, okay = loop([0, 1, 0, 0], cmd, okay)
        cmd, okay = loop([0, 0, 1, 0], cmd, okay)
        cmd, okay = loop([0, 0, 0, 1], cmd, okay)

        if okay == 1:
            print cmd
            print "// Result: " + str(mel.eval(cmd)) + " //"


def channelbox_command_delete(box, menuItem, key, *args):
    with sysCmd.Undo():
        cmd = ""
        okay = 0

        def loop(which, _cmd, _okay):
            obj_list = cmds.channelBox(box.channelbox, q=1, mainObjectList=which[0], shapeObjectList=which[1],
                                       historyObjectList=which[2], outputObjectList=which[3])
            attr_list = cmds.channelBox(box.channelbox, q=1, selectedMainAttributes=which[0],
                                        selectedShapeAttributes=which[1], selectedHistoryAttributes=which[2],
                                        selectedOutputAttributes=which[3])

            if obj_list and attr_list:
                _cmd += "cutKey -cl -t \":\" -f \":"
                for channel in attr_list:
                    _cmd += "\" -at \"" + channel
                for obj in obj_list:
                    _cmd += "\" " + obj
                _cmd += ";"
                _okay = 1

            return _cmd, _okay

        cmd, okay = loop([1, 0, 0, 0], cmd, okay)
        cmd, okay = loop([0, 1, 0, 0], cmd, okay)
        cmd, okay = loop([0, 0, 1, 0], cmd, okay)
        cmd, okay = loop([0, 0, 0, 1], cmd, okay)

        if okay == 1:
            print cmd
            print "// Result: " + str(mel.eval(cmd)) + " //"


# --
def channelbox_command_duplicateAttrValues(box, menuItem, key, *args):
    mel.eval("copyAttrValues")


def channelbox_command_freezeTranslate(box, menuItem, key, *args):
    with sysCmd.Undo():
        if cmds.ls(sl=1):
            cmds.makeIdentity(t=1, r=0, s=0, n=0, a=1)


def channelbox_command_freezeRotate(box, menuItem, key, *args):
    with sysCmd.Undo():
        if cmds.ls(sl=1):
            cmds.makeIdentity(t=0, r=1, s=0, n=0, a=1)


def channelbox_command_freezeScale(box, menuItem, key, *args):
    with sysCmd.Undo():
        if cmds.ls(sl=1):
            cmds.makeIdentity(t=0, r=0, s=1, n=0, a=1)


def channelbox_command_freezeTranslateRotate(box, menuItem, key, *args):
    with sysCmd.Undo():
        if cmds.ls(sl=1):
            cmds.makeIdentity(t=1, r=1, s=0, n=0, a=1)


def channelbox_command_freezeTranslateScale(box, menuItem, key, *args):
    with sysCmd.Undo():
        if cmds.ls(sl=1):
            cmds.makeIdentity(t=1, r=0, s=1, n=0, a=1)


def channelbox_command_freezeRotateScale(box, menuItem, key, *args):
    with sysCmd.Undo():
        if cmds.ls(sl=1):
            cmds.makeIdentity(t=0, r=1, s=1, n=0, a=1)


def channelbox_command_freezeJointOrient(box, menuItem, key, *args):
    with sysCmd.Undo():
        if cmds.ls(sl=1):
            cmds.makeIdentity(t=0, r=0, s=0, n=0, jo=1, a=1)


def channelbox_command_freezeAll(box, menuItem, key, *args):
    with sysCmd.Undo():
        state = cmds.menuItem(menuItem, q=1, isOptionBox=1)

        if not state:
            if cmds.ls(sl=1):
                cmds.makeIdentity(t=1, r=1, s=1, n=0, a=1)
        else:
            channelbox_command_freezeUI()


def channelbox_command_freezeUI():
    with sysCmd.Undo(0):
        if cmds.window("freezeWindowBox", q=1, exists=1):
            cmds.deleteUI("freezeWindowBox")
        frz_window = cmds.window("freezeWindowBox", title="Freeze", rtf=1, s=0, tbm=1, tlb=1)
        layout = cmds.columnLayout(p=frz_window)
        layout_top = cmds.rowLayout(nc=4, p=layout)

        width = 25
        cmds.button(l="T", w=width, ann="Freeze Translate",
                    c=sysCmd.rpartial(channelbox_command_freezeTranslate, "", "", "Freeze Translate"), p=layout_top)
        cmds.button(l="R", w=width, ann="Freeze Rotate",
                    c=sysCmd.rpartial(channelbox_command_freezeRotate, "", "", "Freeze Rotate"), p=layout_top)
        cmds.button(l="S", w=width, ann="Freeze Scale",
                    c=sysCmd.rpartial(channelbox_command_freezeScale, "", "", "Freeze Scale"), p=layout_top)
        cmds.button(l="A", w=width, ann="Freeze All",
                    c=sysCmd.rpartial(channelbox_command_freezeAll, "", "", "Freeze All"), p=layout_top)

        layout_bot = cmds.rowLayout(nc=4, p=layout)
        cmds.button(l="TS", w=width, ann="Freeze Translate / Scale",
                    c=sysCmd.rpartial(channelbox_command_freezeTranslateScale, "", "", "Freeze Translate / Scale"),
                    p=layout_bot)
        cmds.button(l="TR", w=width, ann="Freeze Translate / Rotate",
                    c=sysCmd.rpartial(channelbox_command_freezeTranslateRotate, "", "", "Freeze Translate / Rotate"),
                    p=layout_bot)
        cmds.button(l="RS", w=width, ann="Freeze Rotate / Scale",
                    c=sysCmd.rpartial(channelbox_command_freezeRotateScale, "", "", "Freeze Rotate / Scale"),
                    p=layout_bot)
        cmds.button(l="JO", w=width, ann="Freeze Joint Orient",
                    c=sysCmd.rpartial(channelbox_command_freezeJointOrient, "", "", "Freeze Joint Orient"),
                    p=layout_bot)
        cmds.window(frz_window, e=1, wh=(1, 1), rtf=1)
        cmds.showWindow(frz_window)


# --
def channelbox_command_break(box, menuItem, key, *args):
    with sysCmd.Undo():
        for plug in channelBox_SelectedPlugs(box):
            if cmds.connectionInfo(plug, isDestination=1):
                destination = cmds.connectionInfo(plug, getExactDestination=1)

                # when delete source conn from character, must remove from character set or set becomes inconsistent
                src_conn = cmds.listConnections(destination, s=1, d=0, type="character")
                if src_conn:
                    warn_msg = "Removed \'^1s\' from character \'^2s\'."
                    cmds.warning(cmds.format(warn_msg, s=(destination, src_conn[0])))
                    cmds.character(destination, e=1, rm=src_conn[0])

                # is tracking edits?
                import maya.api.OpenMaya as om
                obj = om.MSelectionList().add(destination).getDependNode(0)
                depend_fn = om.MFnDependencyNode(obj)
                tracking_edits = depend_fn.isTrackingEdits()
                del obj
                del depend_fn

                if tracking_edits:
                    src = cmds.connectionInfo(destination, sourceFromDestination=1)
                    cmds.disconnectAttr(src, destination)
                else:
                    cmds.delete(destination, icn=1)


def channelbox_command_selectConnection(box, menuItem, key, *args):
    with sysCmd.Undo():
        for plug in channelBox_SelectedPlugs(box):
            if cmds.connectionInfo(plug, isDestination=1):
                destination = cmds.connectionInfo(plug, getExactDestination=1)
                dest_input = cmds.listConnections(destination)
                cmds.select(dest_input[0], r=1)


# --
def channelbox_command_lock(box, menuItem, key, *args):
    with sysCmd.Undo():
        for p in channelBox_SelectedPlugs(box):
            cmds.setAttr(p, lock=1)


def channelbox_command_unlock(box, menuItem, key, *args):
    with sysCmd.Undo():
        for p in channelBox_SelectedPlugs(box):
            cmds.setAttr(p, lock=0)


def channelbox_command_unkeyable(box, menuItem, key, *args):
    cmds.channelBox(box.channelbox, e=1, exe=("setAttr -keyable false -channelBox false \"#P.#A\";", 1))


def channelbox_command_lockUnkeyable(box, menuItem, key, *args):
    cmds.channelBox(box.channelbox, e=1, exe=("setAttr -lock true -keyable false -channelBox false \"#P.#A\";", 1))


def channelbox_command_unkeyableDisplayed(box, menuItem, key, *args):
    cmds.channelBox(box.channelbox, e=1, exe=("setAttr -keyable false -channelBox true \"#P.#A\";", 1))


def channelbox_command_keyable(box, menuItem, key, *args):
    cmds.channelBox(box.channelbox, e=1, exe=("setAttr -keyable true \"#P.#A\";", 1))


# --
def channelbox_command_addToLayers(box, menuItem, key, *args):
    with sysCmd.Undo():
        plugs = channelBox_SelectedPlugs(box)
        layers = mel.eval("$tmpvar=$gSelectedAnimLayers")
        channelBox_ModifyPlugsInLayers(plugs, layers, 1)


def channelbox_command_removeFromLayers(box, menuItem, key, *args):
    with sysCmd.Undo():
        plugs = channelBox_SelectedPlugs(box)
        layers = mel.eval("$tmpvar=$gSelectedAnimLayers")
        channelBox_ModifyPlugsInLayers(plugs, layers, 0)


# -------------- EDIT MENU -------------  
# --------------------------------------  
def channelbox_command_expression(box, menuItem, key, *args):
    with sysCmd.Undo(0):
        main_obj_list = cmds.channelBox(box.channelbox, q=1, mainObjectList=1)
        main_attr_list = cmds.channelBox(box.channelbox, q=1, selectedMainAttributes=1)

        shape_obj_list = cmds.channelBox(box.channelbox, q=1, shapeObjectList=1)
        shape_attr_list = cmds.channelBox(box.channelbox, q=1, selectedShapeAttributes=1)

        history_obj_list = cmds.channelBox(box.channelbox, q=1, historyObjectList=1)
        history_attr_list = cmds.channelBox(box.channelbox, q=1, selectedHistoryAttributes=1)

        output_obj_list = cmds.channelBox(box.channelbox, q=1, outputObjectList=1)
        output_attr_list = cmds.channelBox(box.channelbox, q=1, selectedOutputAttributes=1)

        if main_obj_list and main_attr_list:
            mel.eval("expressionEditor \"EE\" " + main_obj_list[0] + " " + main_attr_list[0] + ";")

        elif shape_obj_list and shape_attr_list:
            mel.eval("expressionEditor \"EE\" " + shape_obj_list[0] + " " + shape_attr_list[0] + ";")

        elif history_obj_list and history_attr_list:
            mel.eval("expressionEditor \"EE\" " + history_obj_list[0] + " " + history_attr_list[0] + ";")

        elif output_obj_list and output_attr_list:
            mel.eval("expressionEditor \"EE\" " + output_obj_list[0] + " " + output_attr_list[0] + ";")


def channelbox_command_driven(box, menuItem, key, *args):
    with sysCmd.Undo(0):
        main_obj_list = cmds.channelBox(box.channelbox, q=1, mainObjectList=1)
        main_attr_list = cmds.channelBox(box.channelbox, q=1, selectedMainAttributes=1)

        shape_obj_list = cmds.channelBox(box.channelbox, q=1, shapeObjectList=1)
        shape_attr_list = cmds.channelBox(box.channelbox, q=1, selectedShapeAttributes=1)

        history_obj_list = cmds.channelBox(box.channelbox, q=1, historyObjectList=1)
        history_attr_list = cmds.channelBox(box.channelbox, q=1, selectedHistoryAttributes=1)

        output_obj_list = cmds.channelBox(box.channelbox, q=1, outputObjectList=1)
        output_attr_list = cmds.channelBox(box.channelbox, q=1, selectedOutputAttributes=1)

        if main_obj_list and main_attr_list:
            mel.eval("setDrivenKeyWindow " + "\"\"" + " " + channelBox_MelArray_Conversion(main_attr_list))

        elif shape_obj_list and shape_attr_list:
            mel.eval(
                "setDrivenKeyWindow " + shape_obj_list[0] + " " + channelBox_MelArray_Conversion(shape_attr_list) + ";")

        elif history_obj_list and history_attr_list:
            mel.eval(
                "setDrivenKeyWindow " + history_obj_list[0] + " " + channelBox_MelArray_Conversion(history_attr_list) + ";")

        elif output_obj_list and output_attr_list:
            mel.eval(
                "setDrivenKeyWindow " + output_obj_list[0] + " " + channelBox_MelArray_Conversion(output_attr_list) + ";")


def channelbox_command_animCurve(box, menuItem, key, *args):
    with sysCmd.Undo(0):
        mel.eval("GraphEditor;")
        cmds.selectionConnection("graphEditor1FromOutliner", e=1, clear=1)
        # in case graph editor is open already, clear selection
        sel_attrs = channelBox_SelectedPlugs(box)
        if sel_attrs:
            for i in sel_attrs:
                cmds.evalDeferred(
                    "cmds.selectionConnection('graphEditor1FromOutliner', e = 1, select =\"" + i + "\")")
                # evalDeferred allows occurring graph editor opens, else selection occurs before element exists


def channelbox_command_channelControlEditor(box, menuItem, key, *args):
    with sysCmd.Undo(0):
        mel.eval("ChannelControlEditor")


def channelbox_command_connectionEditor(box, menuItem, key, *args):
    with sysCmd.Undo(0):
        mel.eval("ConnectionEditor")


def channelbox_command_attributeEditor(box, menuItem, key, *args):
    with sysCmd.Undo(0):
        cmds.select(cmds.channelBox(box.channelbox, q=1, historyObjectList=1),
                    cmds.channelBox(box.channelbox, q=1, outputObjectList=1), add=1)
        mel.eval("openAEWindow")


def channelbox_command_materialAttributes(box, menuItem, key, *args):
    with sysCmd.Undo(0):
        if not cmds.ls(sl=1):
            return

        shape = cmds.listRelatives(cmds.ls(sl=1)[0], shapes=1)
        shading = cmds.listConnections(shape, type="shadingEngine")
        mel.eval("showEditor " + shading[0])


# --
def channelbox_command_addAttribute(box, menuItem, key, *args):
    with sysCmd.Undo(0):
        mel.eval("AddAttribute")


def channelbox_command_renameAttribute(box, menuItem, key, *args):
    with sysCmd.Undo(0):
        mel.eval("RenameAttribute")


def channelbox_command_duplicateAttr(box, menuItem, key, *args):
    mel.eval("duplicateAttr")


def channelbox_command_deleteAttributes(box, menuItem, key, *args):
    cmds.channelBox(box.channelbox, e=1, exe=("catch (`deleteAttr -attribute \"#A\" \"#P\"`);", 1))


# --
def channelbox_command_selectNode(box, menuItem, key, *args):
    cmds.select(cmds.channelBox(box.channelbox, q=1, historyObjectList=1),
                cmds.channelBox(box.channelbox, q=1, outputObjectList=1), r=1)


def channelbox_command_deleteNode(box, menuItem, key, *args):
    cmds.delete(cmds.channelBox(box.channelbox, q=1, historyObjectList=1),
                cmds.channelBox(box.channelbox, q=1, outputObjectList=1))


def channelbox_command_deleteHistory(box, menuItem, key, *args):
    mel.eval("DeleteHistory")


# --
def channelbox_command_setSpeed(box, menuItem, key, *args):
    # Sets the incremental size for attributes when modifying with middle mouse,
    #  eg 'medium' appends +1/-1, 'fast' is +10/-10
    with sysCmd.Undo(0):
        state = 1 if key == "speedSlow" else 2 if key == "speedMedium" else 3

        if state == 1:
            cmds.channelBox(box.channelbox, e=1, speed=0.1)
        elif state == 2:
            cmds.channelBox(box.channelbox, e=1, speed=1)
        else:
            cmds.channelBox(box.channelbox, e=1, speed=10)

        box.saved_states["speedState"][0] = state
        if box.saved_states["showIcons"][0]:
            channelbox_command_Symbol_update(box, "speedState")

        sysCmd.channelbox_save_state(box)


def channelbox_command_setHyperbolic(box, menuItem, key, *args):
    # Sets whether increments interpolate linearly or using a curve
    with sysCmd.Undo(0):
        state = channelBox_Checkbox_Update(box, key, menuItem)
        cmds.channelBox(box.channelbox, e=1, hyperbolic=state)
        box.saved_states["hyperbolic"][0] = state
        if box.saved_states["showIcons"][0]:
            channelbox_command_Symbol_update(box, "hyperbolic")

        sysCmd.channelbox_save_state(box)


def channelbox_command_setNamespace(box, menuItem, key, *args):
    # Sets whether to display namespaces in the editor
    with sysCmd.Undo(0):
        state = channelBox_Checkbox_Update(box, key, menuItem)
        cmds.channelBox(box.channelbox, e=1, showNamespace=state)
        sysCmd.channelbox_save_state(box)


def channelbox_command_setManip(box, menuItem, key, *args):
    # Set manipulator display/update type based on selected attr in channel box
    with sysCmd.Undo(0):
        state = 1 if key == "noManips" else 2 if key == "invisibleManips" else 3

        if state == 1:
            cmds.channelBox(box.channelbox, e=1, useManips="none")
        elif state == 2:
            cmds.channelBox(box.channelbox, e=1, useManips="invisible")
        else:
            cmds.channelBox(box.channelbox, e=1, useManips="standard")

        box.saved_states["manipsState"][0] = state
        if box.saved_states["showIcons"][0]:
            channelbox_command_Symbol_update(box, "manipsState")

        sysCmd.channelbox_save_state(box)


def channelbox_command_precision(box, menuItem, key, *args):
    # floating point value displayed in channel box, eg. value of 5 will
    #  display 5 decimal places
    with sysCmd.Undo(0):
        old_precision = box.saved_states[key][0]
        new_precision = mel.eval("precisionPrompt (\"\", " + str(old_precision) + ", 15);")

        if new_precision > 0:  # Change widths of the fields depending on the precision
            if new_precision <= 3:
                new_width = 65
            elif new_precision <= 6:
                new_width = 95
            elif new_precision <= 9:
                new_width = 115
            elif new_precision <= 12:
                new_width = 130
            else:
                new_width = 155

            cmds.channelBox(box.channelbox, e=1, pre=new_precision, fieldWidth=new_width)
            box.saved_states[key][0] = new_precision
            box.saved_states["fieldWidth"][0] = new_width

        sysCmd.channelbox_save_state(box)


def channelbox_command_reset(box, menuItem, key, *args):
    # resets values in the edit menu to default and forced re-initialization of the default states
    with sysCmd.Undo(0):
        default_states = box.menu_default_states

        for k, v in default_states.iteritems():  # compare keys containing a default state with items that exist in
                                                #  the edit menu or others specified and restore them
            if k in box.menus["Edit"] or "fieldWidth" or "channelWidth" and v[1] == 1:
                box.saved_states[k] = v

        sysCmd.channelbox_save_state(box)  # write our changes to file
        box.re_init(box)  # re-initialize to update our changes in the display


def channelbox_command_setChannelName(box, menuItem, key, *args):
    # set display type for the names in the channel box and adjust the width of the columns displaying the label
    with sysCmd.Undo(0):
        state = 1 if key == "nameNice" else 2 if key == "nameLong" else 3

        if state == 1:
            width = 180
            cmds.channelBox(box.channelbox, e=1, lw=width, ln=1, nn=1)
        elif state == 2:
            width = 180
            cmds.channelBox(box.channelbox, e=1, lw=width, ln=1, nn=0)
        else:
            width = 140
            cmds.channelBox(box.channelbox, e=1, lw=width, ln=0, nn=0)

        box.saved_states["namesState"][0] = state
        box.saved_states["channelWidth"][0] = width

        sysCmd.channelbox_save_state(box)


# -----------------------------------------  

# --------------- SHOW MENU ---------------  
# -----------------------------------------  
def channelbox_command_popupLabel(box, menuItem, key, *args):
    state = channelBox_Checkbox_Update(box, key, menuItem)
    box.saved_states["popupLabel"][0] = state
    sysCmd.channelbox_save_state(box)


def channelbox_command_hideUnavailable(box, menuItem, key, *args):
    state = channelBox_Checkbox_Update(box, key, menuItem)
    box.saved_states["hideUnavailable"][0] = state
    sysCmd.channelbox_save_state(box)


def channelbox_command_showIcons(box, menuItem, key, *args):
    state = channelBox_Checkbox_Update(box, key, menuItem)
    box.saved_states["showIcons"][0] = state
    sysCmd.channelbox_save_state(box)
    box.re_init(box)


def channelbox_command_cboxReset(box, menuItem, key, *args):
    with sysCmd.Undo(0):
        confirm = cmds.confirmDialog(t="Reset to Default",
                                     m="Delete all saved data and modified settings associated with this Channel Box?",
                                     icon="critical", button=["Reset", "Cancel"])

        if confirm == "Reset":

            default_states = box.menu_default_states

            for k, v in default_states.iteritems():
                # compare keys containing a default state with items that exist in the edit menu or others
                # specified and restore them
                box.saved_states[k] = v

            sysCmd.channelbox_pickle_delete_state(box)
            # box.re_init(box)  # re-initialize to update our changes in the display
            cmds.warning("Please close the ChannelBox UI and re-open it for changes to take effect")


def channelbox_command_selectFilterSet(box, menuItem, key, *args):
    with sysCmd.Undo(0):
        state = cmds.menuItem(menuItem, q=1, isOptionBox=1)
        f_set_name = cmds.menuItem(menuItem, q=1, label=1)

        if not state:  # didn't press the option box
            channelbox_command_resetFilters(box)  # resetting filters before applying a new one cleans everything up
            if f_set_name in box.saved_states["savedFilters"][0]:
                saved = box.saved_states["savedFilters"][0][f_set_name][
                        :-2]  # [-1] is invertShown boolean and -2 is the type string, exclude from loop
                box.saved_states["invertShown"][0] = box.saved_states["savedFilters"][0][f_set_name][
                    -1]  # restoring invert state saved with the filter
                # Specific Attribute Filters
                if box.saved_states["savedFilters"][0][f_set_name][-2] == "type=attr":
                    # dict in ["savedFilters"] contains only enabled attributes, so set to 1 always
                    box.filter_attrs = {k: 1 for k in saved}
                    channelBox_filterAttrs(box)  # attributes restored to box.filter_attrs, now apply the filter
                # Pre-defined Filters
                else:
                    for f in saved:
                        box.filter_items.append(f)
                        box.saved_states[f][0] = 1  # set each of the checkbox attributes to 1 to update UI
                    channelBox_Filter_Items(box)
            else:
                cmds.error(
                    "Filter set doesn't exist, potential mismatch between data file and current menu state."
                    " Was something deleted from the drive?")
        else:
            del_conf = cmds.confirmDialog(t="Delete?", icn="warning", message="Delete filter set \"" + f_set_name +
                                                                              "\"?", button=["Delete", "Cancel"])
            if del_conf == "Delete":
                box.saved_states["savedFilters"][0].pop(f_set_name, None)


def channelbox_command_createFilterSet(box, menuItem, key, *args):
    with sysCmd.Undo(0):
        attrs = len(box.filter_attrs) >= 1
        fset = []

        if attrs:  # checking if we're dealing with specific attributes or pre-defined items
            for f in box.filter_attrs:  # add the key values in filter_attrs to fset
                fset.append(f)
            fset.append("type=attr")  # append the type to the end of the list, later becomes [-2]
        else:
            for f in box.filter_items:
                fset.append(f)
            fset.append("type=item")

        if fset:
            name_prompt = cmds.promptDialog(t="Save Filter Set", button=["Save", "Cancel"])
            # ask user to enter the set name
        else:
            return

        fset.append(
            box.saved_states["invertShown"][0])  # append the invertShown state to become [-1] pushing fset to [-2]

        if name_prompt == "Save":
            name = cmds.promptDialog(q=1, tx=1)
            confirm = 0
            if name in box.saved_states["savedFilters"][0]:  # check if exists, ask to confirm overwrite
                confirm = cmds.confirmDialog(t="Confirm Overwrite", icn="warning",
                                             message="Filter set \"" + name + "\" already exists. Overwrite?",
                                             button=["Overwrite", "Cancel"])
            if confirm and confirm == "Overwrite" or not confirm:
                box.saved_states["savedFilters"][0][name] = fset
        else:
            return

        sysCmd.channelbox_save_state(box)


def channelBox_filterAttrs(box):
    with sysCmd.Undo(0):
        names = []
        for key, value in box.filter_attrs.iteritems():
            if value:
                names.append(key)

        box.filter = cmds.itemFilterAttr(byNameString=names, negate=box.saved_states["invertShown"][0])
        cmds.channelBox(box.channelbox, e=1, attrFilter=box.filter, update=1)


def channelbox_command_isolateAttr(box, menuItem, key, *args):
    with sysCmd.Undo(0):
        state = cmds.menuItem(menuItem, q=1, isOptionBox=1)

        if state:  # clicked menuItem rather than option box
            if cmds.window("selectAttrWin", exists=1):
                cmds.deleteUI("selectAttrWin")

            window = cmds.window("selectAttrWin", title="Select Attributes", mxb=1, mnb=1, s=1)
            layout = cmds.formLayout(p=window)

            def state(_key):  # restore checkbox values
                if _key in box.filter_attrs and box.filter_attrs[_key] == 1:
                    return 1
                else:
                    return 0

            def cb_cmd(_key, cb, *args):
                # checkbox command, sets value for each _key, calls resetfilters to clear previous, then updates
                box.filter_attrs[_key] = cmds.checkBox(cb, q=1, v=1)
                channelbox_command_resetFilters(box)
                channelBox_filterAttrs(box)

            # primary interface
            clayout = cmds.columnLayout(p=layout)
            r1 = cmds.rowLayout(nc=4, cw4=(70, 30, 30, 30), p=clayout)
            cmds.text(l="", p=r1)
            cmds.text(l="X", p=r1)
            cmds.text(l="Y", p=r1)
            cmds.text(l="Z", p=r1)

            r2 = cmds.rowLayout(nc=4, cw4=(70, 30, 30, 30), p=clayout)
            cmds.text(l="Translate", p=r2)
            _tx = cmds.checkBox(l="", v=state("translateX"), p=r2)
            _ty = cmds.checkBox(l="", v=state("translateY"), p=r2)
            _tz = cmds.checkBox(l="", v=state("translateZ"), p=r2)

            cmds.checkBox(_tx, e=1, cc=partial(cb_cmd, "translateX", _tx))
            cmds.checkBox(_ty, e=1, cc=partial(cb_cmd, "translateY", _ty))
            cmds.checkBox(_tz, e=1, cc=partial(cb_cmd, "translateZ", _tz))

            r3 = cmds.rowLayout(nc=4, cw4=(70, 30, 30, 30), p=clayout)
            cmds.text(l="Rotate", p=r3)
            _rx = cmds.checkBox(l="", v=state("rotateX"), p=r3)
            _ry = cmds.checkBox(l="", v=state("rotateY"), p=r3)
            _rz = cmds.checkBox(l="", v=state("rotateZ"), p=r3)

            cmds.checkBox(_rx, e=1, cc=partial(cb_cmd, "rotateX", _rx))
            cmds.checkBox(_ry, e=1, cc=partial(cb_cmd, "rotateY", _ry))
            cmds.checkBox(_rz, e=1, cc=partial(cb_cmd, "rotateZ", _rz))

            r4 = cmds.rowLayout(nc=4, cw4=(70, 30, 30, 30), p=clayout)
            cmds.text(l="Scale", p=r4)
            _sx = cmds.checkBox(l="", v=state("scaleX"), p=r4)
            _sy = cmds.checkBox(l="", v=state("scaleY"), p=r4)
            _sz = cmds.checkBox(l="", v=state("scaleZ"), p=r4)

            cmds.checkBox(_sx, e=1, cc=partial(cb_cmd, "scaleX", _sx))
            cmds.checkBox(_sy, e=1, cc=partial(cb_cmd, "scaleY", _sy))
            cmds.checkBox(_sz, e=1, cc=partial(cb_cmd, "scaleZ", _sz))

            # other attributes

            slayout = cmds.scrollLayout(childResizable=1, p=clayout)  # extra attribs placed in scroll layout
            skip = ["translateX", "translateY", "translateZ", "rotateX", "rotateY", "rotateZ", "scaleX", "scaleY",
                    "scaleZ"]
            objects = cmds.channelBox(box.channelbox, q=1, mainObjectList=1)

            if objects:
                for obj in objects:
                    attrs = []
                    attrs_cb = cmds.listAttr(obj, cb=1)
                    attrs_k = cmds.listAttr(obj, k=1, v=1)  # list all obj attribs to loop over
                    if attrs_cb and len(attrs_cb) >= 1:
                        attrs += attrs_cb
                    if attrs_k and len(attrs_k) >= 1:
                        attrs += attrs_k
                    for attr in attrs:
                        if attr not in skip:
                            name = obj + "." + attr
                            leafs = cmds.listAttr(name, leaf=1)
                            attr = leafs[0]
                            nice_name = cmds.attributeQuery(attr, niceName=1, node=obj)
                            if nice_name:
                                _cb = cmds.checkBox(l=nice_name, v=state(attr), p=slayout)
                                cmds.checkBox(_cb, e=1, cc=partial(cb_cmd, attr, _cb))

            cmds.showWindow()
        else:  # option box
            box.filter_attrs = {}
            plugs = channelBox_SelectedPlugs(box)  # which attributes are selected in channel box
            if not plugs:
                cmds.warning("No attributes selected")
                return
            for plug in plugs:
                name = cmds.attributeName(plug, long=1)  # we are given shortened attributes, this grabs the long name
                box.filter_attrs[name] = 1
            channelbox_command_resetFilters(box)
            channelBox_filterAttrs(box)


def channelbox_command_filter_invertShown(box, menuItem, key, *args):
    with sysCmd.Undo(0):
        if len(box.filter_attrs) >= 1:
            channelBox_filterAttrs(box)
        elif len(box.filter_items) >= 1:
            channelBox_Filter_Items(box)


def channelbox_command_filter_itemCB(box, menuItem, key, *args):
    with sysCmd.Undo(0):
        state = channelBox_Checkbox_Update(box, key, menuItem)
        if state:
            box.filter_items.append(key)
        else:
            box.filter_items.remove(key)

        channelBox_Filter_Items(box)


def channelbox_command_resetFilters(box):
    with sysCmd.Undo(0):
        print box.filter_items
        for key in box.filter_items:
            box.saved_states[key][0] = 0

        box.filter_items = []


def channelbox_command_filter_filterShowAll(box, menuItem, key, *args):
    with sysCmd.Undo(0):
        channelbox_command_resetFilters(box)
        box.saved_states["invertShown"][0] = 0
        box.filter_attrs = {}

        cmds.channelBox(box.channelbox, e=1, attrFilter=0, update=1)

        channelBox_Filter_Items(box)


def channelBox_Filter_Items(box):
    with sysCmd.Undo(0):
        filters = []
        names = []

        for f in box.filter_items:
            if f == "attr_userDefined":
                user_cb = cmds.listAttr(ud=1, cb=1)
                user_kv = cmds.listAttr(ud=1, k=1, v=1)
                if user_cb:
                    names += user_cb
                if user_kv:
                    names += user_kv
            elif f == "attr_translate":
                names.append("translateX")
                names.append("translateY")
                names.append("translateZ")
            elif f == "attr_rotate":
                names.append("rotateX")
                names.append("rotateY")
                names.append("rotateZ")
            elif f == "attr_scale":
                names.append("scaleX")
                names.append("scaleY")
                names.append("scaleZ")
            else:
                filters.append(f.split("_")[-1])

        if len(filters) == 0 and len(names) == 0:
            cmds.channelBox(box.channelbox, e=1, update=1)
            return

        _f = []  # create the actual filters
        if "animCurve" in filters:
            _f.append(cmds.itemFilterAttr(hasCurve=1))
        if "expression" in filters:
            _f.append(cmds.itemFilterAttr(hasExpression=1))
        if "drivenKey" in filters:
            _f.append(cmds.itemFilterAttr(hasDrivenKey=1))
        if "scaleRotateTranslate" in filters:
            _f.append(cmds.itemFilterAttr(scaleRotateTranslate=1))
        if names:
            _f.append(cmds.itemFilterAttr(byNameString=names))

        destination = _f[0]
        odd = len(_f) % 2  # determines odd/even number
        loops = len(_f) / 2 + (1 if odd else 0)

        for i in range(loops):  # create union filters
            index_1 = i * 2
            index_2 = i * 2 + 1
            use_last = odd and i + 1 == loops
            destination = cmds.itemFilterAttr(union=(_f[index_1], _f[index_2] if not use_last else destination))

        box.filter = destination
        cmds.itemFilterAttr(box.filter, e=1, negate=box.saved_states["invertShown"][0])
        cmds.channelBox(box.channelbox, e=1, attrFilter=box.filter, update=1)

        for f in _f:
            cmds.delete(f)


# -----------------------------------------  


# -------------- SYMBOL COMMANDS -------------  
# --------------------------------------------  
def channelbox_command_Symbol_update(box, key, *args):
    with sysCmd.Undo(0):
        if key == "manipsState":
            if box.saved_states[key][0] == 1:
                image = "channelBoxNoManips.png"
            elif box.saved_states[key][0] == 2:
                image = "channelBoxInvisibleManips.png"
            else:
                image = "channelBoxUseManips.png"
        elif key == "speedState":
            if box.saved_states[key][0] == 1:
                image = "channelBoxSlow.png"
            elif box.saved_states[key][0] == 2:
                image = "channelBoxMedium.png"
            else:
                image = "channelBoxFast.png"
        else:
            if box.saved_states[key][0] == 1:
                image = "channelBoxHyperbolicOn.png"
            else:
                image = "channelBoxHyperbolicOff.png"

        cmds.symbolButton(box.symbols[key], e=1, image=image)


def channelbox_command_Symbol_pressed(box, key, *args):
    if key == "manipsState" or key == "speedState":
        if box.saved_states[key][0] < 3:
            box.saved_states[key][0] += 1
        else:
            box.saved_states[key][0] = 1
    elif key == "hyperbolic":
        box.saved_states[key][0] = 1 if box.saved_states[key][0] == 0 else 0

    sysCmd.channelbox_save_state(box)
    channelbox_command_Symbol_update(box, key)


# -----------------------------------------  

# -------------- HELPER COMMANDS -------------  
# --------------------------------------------  
def channelBox_Checkbox_Update(box, key, menuItem):
    box.saved_states[key][0] = cmds.menuItem(menuItem, q=1, checkBox=1)
    return box.saved_states[key][0]


def channelBox_MelArray_Conversion(mel_array):
    string = str(mel_array)
    string = string.replace("[", "{")
    string = string.replace("]", "}")
    string = string.replace("'", "\"")
    string = string.replace("{u", "{")
    string = string.replace(", u", ", ")

    return string


def channelBox_ModifyPlugsInLayers(plugs, layers, operation):
    if not plugs:
        cmds.error("No channel attributes selected.")
    if not layers:
        cmds.error("No layer is selected.  Please select a layer.")

    for layer in layers:
        if not cmds.objectType(layer, isType="animLayer"):
            continue
        for plug in plugs:
            if operation:
                mel.eval("evalEcho( \"animLayer -edit -attribute " + plug + " " + layer + "\");")
            else:
                mel.eval("evalEcho( \"animLayer -edit -removeAttribute " + plug + " " + layer + "\");")


def channelBox_SelectedPlugs(box):
    result = []

    def loop(which, _result):
        obj_list = cmds.channelBox(box.channelbox, q=1, mainObjectList=which[0], shapeObjectList=which[1],
                                   historyObjectList=which[2], outputObjectList=which[3])
        attr_list = cmds.channelBox(box.channelbox, q=1, selectedMainAttributes=which[0],
                                    selectedShapeAttributes=which[1], selectedHistoryAttributes=which[2],
                                    selectedOutputAttributes=which[3])

        if obj_list and attr_list:
            for obj in obj_list:
                for attr in attr_list:
                    _result.append(obj + "." + attr)

        return _result

    result = loop([1, 0, 0, 0], result)
    result = loop([0, 1, 0, 0], result)
    result = loop([0, 0, 1, 0], result)
    result = loop([0, 0, 0, 1], result)

    return result
    # -----------------------------------------  
