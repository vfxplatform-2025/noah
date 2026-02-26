"""
PolyImagePlane

Creates a polygon plane that mimics the position of an camera image plane.

To use, simply select the camera image plane and run the script.

import polyImagePlane
polyImagePlane.main()

Or if you know the name of the camera, camera shape and image plane directly,
you can call the function directly.

import polyImagePlane
polyImagePlane.createPolyImagePlane('cameraName', 'cameraShapeName', 'imagePlaneName')
"""

import maya.cmds as cmds
import math


def getLongName(name):
    if cmds.objExists(name):
        # return cmds.ls(name, int=True)[0]
        return cmds.ls(name)[0]
    return None


def getShortName(name):
    if cmds.objExists(name):
        return cmds.ls(name)[0]
    return None


def createPolyImagePlane(camera, cameraShape, imagePlane):
    # Get Plane Names

    #global planeShapeName

    planeName = getShortName(imagePlane)+"_poly"
    if imagePlane.find('->') != -1:
        planeName = getShortName(imagePlane).split('->')[-1]
        planeName = planeName+"_poly"
    planeShapeName = planeName+'Shape'
    polyPlaneName = planeName+'_polyPlane'

    # Create Nodes
    plane = cmds.createNode('transform', name=planeName, parent=camera)
    planeShape = cmds.createNode('mesh', name=planeShapeName, parent=plane)
    polyPlane = cmds.createNode('polyPlane', name=planeShapeName)
    cmds.connectAttr(polyPlane+'.output', planeShape+'.inMesh', force=True)
    cmds.setAttr(polyPlane+'.subdivisionsWidth', 1)
    cmds.setAttr(polyPlane+'.subdivisionsHeight', 1)

    # Add expression
    exp = ''
    exp += 'float $f = %s.focalLength;\n' % cameraShape
    exp += 'float $fbw = %s.horizontalFilmAperture;\n' % cameraShape
    exp += 'float $fbh = %s.verticalFilmAperture;\n' % cameraShape
    exp += 'float $fov = rad_to_deg(2 * atan( ($fbw*25.4) / (2 * $f) ));\n'
    exp += 'float $planeScale = 2*(%s.depth)*(tand($fov/2.0));\n\n' % imagePlane
    exp += '%s.width = 1.0;\n' % polyPlane
    exp += '%s.height = $fbh/$fbw;\n\n' % polyPlane
    exp += 'translateX = $planeScale*0.5*((%s.offsetX/2.54)/(($fbw/2.54)*0.5));\n' % imagePlane
    exp += 'translateY = $planeScale*0.5*((%s.offsetY/2.54)/(($fbw/2.54)*0.5));\n' % imagePlane
    exp += 'translateZ = -1*%s.depth;\n' % imagePlane
    exp += 'rotateX = 90.0;\n'
    exp += 'rotateY = rotateZ = 0.0;\n\n'
    exp += 'scaleX = scaleY = scaleZ = $planeScale;\n\n'
    expressionName = cmds.expression(string=exp, object=plane, alwaysEvaluate=True, unitConversion='all')

    #return (plane, planeShape, polyPlane)
    return (plane, expressionName)

def polyImagePlane(camList):
    
    camera = None
    cameraShape = None
    imagePlane = None
    #global seqPath

    #selCam = cmds.ls(sl = 1)[0]
    selCam = camList[0]
    camShape = cmds.listRelatives(selCam,type="shape")[0]
    tmp = cmds.listConnections(camShape, type = "imagePlane", shapes=True)
    if len(tmp) > 0:
        imagePlane = tmp[0]
    else:
        return False
    conn = cmds.listConnections(imagePlane, type="camera", shapes=True)
    if len(conn) > 0:
        cameraShape = getLongName(conn[0])
        camera = cmds.listRelatives(cameraShape, parent=True)[0]
        camera = getLongName(camera)
    else:
        return False
    #seqPath = cmds.getAttr("%s.imageName"%imagePlane)
    #plane, planeShape, polyPlane = createPolyImagePlane(camera, cameraShape, imagePlane)
    plane, expressionName = createPolyImagePlane(camera, cameraShape, imagePlane)
    #cmds.select(plane, replace=True)
    #imageSeq()
    
    #cmds.select(planeShapeName)
    #cmds.hyperShade(assign=planeShader)
    
    #return True
    return plane, expressionName

