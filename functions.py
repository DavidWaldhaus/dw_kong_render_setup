# Import third-party modules
import maya.cmds as cmds
import pymel.core as pmc
import maya.mel as mel
import tempfile
import os
import re

import subprocess

# Logger
import logging

# Render Setup
import maya.app.renderSetup.model.override as override
import maya.app.renderSetup.model.selector as selector
import maya.app.renderSetup.model.collection as collection
import maya.app.renderSetup.model.renderLayer as renderLayer
import maya.app.renderSetup.model.renderSetup as renderSetup
from maya.app.renderSetup.model.connectionOverride import MaterialOverride

logging.basicConfig()
logger = logging.getLogger('Kong Render Setup')
logger.setLevel(logging.INFO)

NAME_MATCHING = {"clr":"BaseColor", "dsp":"Height", "mtl":"Metalness", "nrm":"Normal", "opc":"Opacity", "rgh":"Roughness", "emn":"Emissive"}

def kill_existing_app(windowName):
    """Kill the app if it's running.

    Args:
        windowName (str): Window object name of the app.
    """
    if cmds.window(windowName, exists=True, q=True):
        cmds.deleteUI(windowName)

def show_help():

    help_path = "T:/david.waldhaus/documentation/fixPref/fixPref_documentation.pdf"

    subprocess.Popen(help_path, shell=True)

def is_group(node):
    try:
        children = node.getChildren()
        for child in children:
            if type(child) is not pmc.nodetypes.Transform:
                return False
        return True
    except:
        return False

def load_selected_geo():

    sel = pmc.ls(sl=1)
    if not sel:
        logger.warning("Nothing selected!")
        return

    return sel,str(sel)

def load_selected_shader(shader=None):
    """
    loads the selected shading engine
    returns str asset name, dir with plug index and variation name
    :param shader:
    :return:
    """

    valid = False
    shader = shader
    asset_name = ""
    switch_nodes = {}
    max_input = 0

    # validate that selection is only a single SG node

    if len(shader) != 1:
        pmc.warning("Please Select only 1 shader!.")
        return valid, shader, switch_nodes, max_input

    shader = shader[0]

    if not shader.type() == "shadingEngine":
        pmc.warning("Please Select a Shading Engine Only")
        return valid, shader, switch_nodes, max_input

    # selection from here on is validated
    # contains only a single shd engine

    valid = True

    # get asset name from shader naming

    asset_name = str(shader).replace("elements_", "").replace("_sg", "")

    # get switch nodes from sg
    all_nodes = pmc.listHistory(shader)
    all_switches = [x for x in all_nodes if x.type() == "aiSwitch"]

    logger.info("Unfiltered Switches : {}".format(all_switches))

    # get plug name for switches, switch is only valid if a plug is found

    switch_dir_unvalidated = {}

    for switch in all_switches:
        plug = re.findall(r".*_(clr|dsp|mtl|nrm|opc|rgh|emn)_switch.?$", str(switch))
        if len(plug) == 1:
            plug = plug[0]
            switch_dir_unvalidated[plug] = switch
        else:
            logger.info("Couldn't identify channel for {}. Skipping.".format(switch))

    logger.info("Ordered the found Switches this way : \n {}".format(switch_dir_unvalidated))

    # validate the found switches against main dict

    switch_dir_validated = {}

    for plug in NAME_MATCHING:
        if plug in switch_dir_unvalidated:
            switch_dir_validated[plug] = switch_dir_unvalidated[plug]
        else:
            switch_dir_validated[plug] = None

    logger.info("Ordered the Switches! Final List : \n {}".format(switch_dir_validated))

    switch_nodes = switch_dir_validated

    # get max input number

    max_input = 0
    skipped_slots = []

    for switch in switch_nodes:
        temp_max = 0
        for x in range(20):
            # if no switch node exists for the slot, skip it
            if switch_nodes[switch]:
                connection = switch_nodes[switch] + ".input{}".format(x)
                is_connected = pmc.connectionInfo(connection, isDestination=True)
                if not is_connected:
                    continue
                else:
                    temp_max += 1
            else:
                if not switch in skipped_slots:
                    skipped_slots.append(switch)
                continue
        if temp_max > max_input:
            max_input = temp_max

    logger.info("Determined max number of switch inputs : {}".format(max_input))
    logger.info("Skipping switch for the following slots, since no input was found : {}".format(skipped_slots))

    # build a dict with slot number and variation name

    # pick clr switch as base to determine variation names, if thats not available use next best choice

    base_switch = None

    for switch in switch_nodes:
        if switch_nodes[switch]:
            base_switch = switch_nodes[switch]
            break
        else:
            continue

    if base_switch:
        logger.info("Determined {} switch to pick variations from.".format(base_switch))
    else:
        logger.warning("Could not determine a base switch. Aborting.")
        return False

    # iterate over base switches inputs until max input is reached, and get variation name

    variations = {}

    for x in range(max_input):
        variation_name = ""
        node = pmc.listConnections(base_switch + ".input{}".format(x))[0]
        file_path = node.fileTextureName.get()
        # regex to get folder above version folder
        variation_name = re.findall(r"^(?:.*[\/\\]+)(\w+)(?:[\/\\]+)(?:v\d{3})", str(os.path.normpath(file_path)))
        if variation_name:
            if len(variation_name) == 1:
                variation_name = variation_name[0]
            else:
                logger.warning("Error fetching variation name for path : {}".format(file_path))
                return False
        else:
            logger.warning("Error fetching variation name for path : {}".format(file_path))
            return False

        variations[x] = variation_name

    return valid, shader, asset_name, variations

def createShader(shaderType):
    """ Create a shader of the given type"""
    shaderName = cmds.shadingNode(shaderType, asShader=True)
    sgName = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=(shaderName + "SG"))
    cmds.connectAttr(shaderName + ".outColor", sgName + ".surfaceShader")
    return (shaderName, sgName)

def build_render_setup(content=None, content_shadow=None, asset_name="default", filename_prefix="", shading_engine="", variations={}, bg_selector=""):
    """
    builds the render setup
    :param content: content of main description
    :param asset_name: name of the asset, used to build render layer naming
    :param filename_prefix:  file name prefix set in render layer
    :param shading_engine: sg for material OR
    :param variations: dict with variations & indices to build layers for switch variations
    :return:
    """

    logger.info("Building Shader with the following Parameters : \n"
                "Content : {} \n"
                "Shadow Catch Conent : {} \n"
                "Background : {} \n"
                "File Name Prefix : {} \n"
                "Asset Name : {} \n"
                "Shading Engine : {} \n"
                "Var Dict : {}".format(content, content_shadow, bg_selector, filename_prefix, asset_name, shading_engine, variations))

    # iterate over variations dict to build layers for each var

    rs = renderSetup.instance()

    for index in variations:

        # create main render layer
        layer_name = asset_name + "_" + variations[index]
        rl = rs.createRenderLayer(layer_name)

        # create render setting override for image path
        file_prefix = filename_prefix

        settings_coll = rl.renderSettingsCollectionInstance()
        attr_name = 'imageFilePrefix'
        override = settings_coll.createAbsoluteOverride('defaultRenderGlobals', attr_name)
        override.setAttrValue(file_prefix)
        override.setName(layer_name + '_' + attr_name)

        # create collection for head
        c_shadow_catcher = rl.createCollection("shadow_catcher")
        # build list from obj list
        shdw_string = build_search_string(content_shadow)
        c_shadow_catcher.getSelector().setPattern(shdw_string)
        # create shader override
        ov1 = c_shadow_catcher.createOverride('shadow_catcher', MaterialOverride.kTypeId)

        # check if shadow catcher exists, if not create a new one

        if not pmc.objExists("aiShadowMatte1SG"):
            shadow_matte_sg = createShader("aiShadowMatte")[-1]
            logger.info("No existing shadow catcher found, creating new aiShadowMatte: {}".format(shadow_matte_sg))
        else:
            shadow_matte_sg = pmc.PyNode("aiShadowMatte1SG")
            logger.info("Using existing aiShadowMatte as shadow catcher: {}".format(shadow_matte_sg))

        ov1.setSource(str(shadow_matte_sg)+".message")
   
        # set self shadows off on shapes
        """
        # shape collection gets created automatically
        c_head_shapes = c_shadow_catcher.createCollection('head_shapes')  # create sub collection
        c_head_shapes.getSelector().setPattern('*')
        c_head_shapes.getSelector().setFilterType(selector.Filters.kShapes)
        """
        attr_name = 'aiSelfShadows'

        cmds.polyCube(n='dummyObj')
        or_self_shadows = c_shadow_catcher.createAbsoluteOverride('dummyObjShape', attr_name)
        or_self_shadows.setName(c_shadow_catcher.name() + "_self_shadows_off")
        or_self_shadows.setAttrValue(0)
        cmds.delete('dummyObj')

        # create aov collection and disable all
        c_aovs = rl.createCollection('aovs_off')  # create sub collection
        c_aovs.getSelector().setPattern('*')
        c_aovs.getSelector().setFilterType(selector.Filters.kCustom)
        c_aovs.getSelector().setCustomFilterValue("aiAOV")

        attr_enabled = "enabled"
        dummy_aov = pmc.createNode( 'aiAOV' , name = 'Dummy' )
        or_enabled = c_aovs.createAbsoluteOverride(str(dummy_aov), attr_enabled)
        or_enabled.setName(c_aovs.name() + "_enabled")
        or_enabled.setAttrValue(0)
        pmc.delete(dummy_aov)

        # create bg collection
        c_bg = rl.createCollection("background")
        c_bg.getSelector().setPattern(bg_selector)

        # create empty collection for visibility
        c_visibility = rl.createCollection("visibility")
        cmds.polyCube(n='dummyObj')
        or_self_shadows = c_visibility.createAbsoluteOverride('dummyObj', "visibility")
        or_self_shadows.setName(c_visibility.name() + "_visibility_off")
        or_self_shadows.setAttrValue(0)
        cmds.delete('dummyObj')

        # create main collection for asset geo
        c_asset = rl.createCollection(asset_name)

        # add content
        """
        #selector
        sl = c_asset.getSelector()
        # static selection
        ss = sl.staticSelection
        # add items

        # create str list from items
        str_content = []

        for obj in content:
            str_content.append(str(obj))

        ss.add(str_content)
        """

        # build list from obj list

        sel_string = build_search_string(content)
        c_asset.getSelector().setPattern(sel_string)

        # create shader override
        or_material = c_asset.createOverride('asset_shader', MaterialOverride.kTypeId)
        or_material.setSource(str(shading_engine) + ".message")

        # floatConstant override for switch index
        c_float_constant = c_asset.createCollection('float_switch_select')  # create sub collection
        c_float_constant.getSelector().setPattern('*')
        c_float_constant.getSelector().setFilterType(selector.Filters.kCustom)
        c_float_constant.getSelector().setCustomFilterValue("floatConstant")

        attr_in_float = "inFloat"
        dummy_float = pmc.createNode('floatConstant', name='dummy_float')
        or_enabled = c_float_constant.createAbsoluteOverride(str(dummy_float), attr_in_float)
        or_enabled.setName(c_float_constant.name() + "_inFloat")
        or_enabled.setAttrValue(index)
        pmc.delete(dummy_float)


def build_search_string(content):
    """
    builds a search string for render layer expression from a given list of nodes
    :param content: list of nodes
    :return:
    """
    sel_string = ""

    for asset in content:
        asset = str(asset)
        if ":" in asset:
            search_string = "*:" + asset.split(":")[-1]

        else:
            search_string = "*" + asset

        if not sel_string:
            sel_string = sel_string + search_string
        else:
            sel_string = sel_string + ", " + search_string

    return sel_string














