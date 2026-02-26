import os
import importlib

__all__ = []

ABCIMPORTOPT = ["alembic", "gpu", "proxy", "import"]
APPNAME = os.getenv('APPNAME')

import maya.cmds as cmds
__all__.append('cmds')

import maya.mel as mel
__all__.append('mel')

import maya.OpenMayaUI as mui
__all__.append('mui')

from script import atomScript
importlib.reload(atomScript)
__all__.append('atomScript')

from script import geoCacheScript
importlib.reload(geoCacheScript)
__all__.append('geoCacheScript')

from script import yetiCacheScript
importlib.reload(yetiCacheScript)
__all__.append('yetiCacheScript')

from script import alembicScript
importlib.reload(alembicScript)
__all__.append('alembicScript')

from script import usdScript
importlib.reload(usdScript)
__all__.append('usdScript')

from script import assScript
importlib.reload(assScript)
__all__.append('assScript')

from script import cameraScript
importlib.reload(cameraScript)
__all__.append('cameraScript')

from script import dummyScript
importlib.reload(dummyScript)
__all__.append('dummyScript')

from script import mayaScript
importlib.reload(mayaScript)
__all__.append('mayaScript')

from script import mayaHairScript
importlib.reload(mayaHairScript)
__all__.append('mayaHairScript')

from script import renderLayerScript
importlib.reload(renderLayerScript)
__all__.append('renderLayerScript')

from script import rigScript
importlib.reload(rigScript)
__all__.append('rigScript')

from script import modelScript
importlib.reload(modelScript)
__all__.append('modelScript')

from script import frameRangeScript
importlib.reload(frameRangeScript)
__all__.append('frameRangeScript')

from script import resolutionScript
importlib.reload(resolutionScript)
__all__.append('resolutionScript')

from script import modelEnvScript
importlib.reload(modelEnvScript)
__all__.append('modelEnvScript')

from script import vrayProxyScript
importlib.reload(vrayProxyScript)
__all__.append('vrayProxyScript')

from script import lookdevScript
importlib.reload(lookdevScript)
__all__.append('lookdevScript')

from script import fxScript
importlib.reload(fxScript)
__all__.append('fxScript')

from script import tractorJobScript
importlib.reload(tractorJobScript)
__all__.append('tractorJobScript')

from script import shotgunScript
importlib.reload(shotgunScript)
__all__.append('shotgunScript')

from script import utilScript
importlib.reload(utilScript)
__all__.append('utilScript')

from script import dataScript
importlib.reload(dataScript)
__all__.append('dataScript')

import referenceSettings.referenceSettings as referenceSettings
print(f"DEBUG: referenceSettings module imported from: {referenceSettings.__file__}")
importlib.reload(referenceSettings)
__all__.append('referenceSettings')

from script import takeScript
importlib.reload(takeScript)
__all__.append('takeScript')

from script import convert_byte_to_string
importlib.reload(convert_byte_to_string)
__all__.append('convert_byte_to_string')

import asstesExport
importlib.reload(asstesExport)
__all__.append('asstesExport')

import commentWindow
importlib.reload(commentWindow)
__all__.append('commentWindow')

from script import instanceScript
importlib.reload(instanceScript)
__all__.append('instanceScript')

print('__all__ >>>>>>>>>>>> ',__all__)