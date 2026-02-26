import maya.cmds as mc
import maya.cmds as cmds
import math

def getLongName(name):
    if mc.objExists(name):
        return mc.ls(name)[0]
    return None

def getShortName(name):
    if mc.objExists(name):
        return mc.ls(name)[0]
    return None

def createPolyImagePlane(camera, cameraShape, imagePlane):
    global planeShapeName

    planeName = getShortName(imagePlane) + "_poly"
    if imagePlane.find('->') != -1:
        planeName = getShortName(imagePlane).split('->')[-1] + "_poly"
    planeShapeName = planeName + 'Shape'
    polyPlaneName = planeName + '_polyPlane'

    # Create transform, mesh, and polyPlane nodes
    plane = mc.createNode('transform', name=planeName, parent=camera)
    planeShape = mc.createNode('mesh', name=planeShapeName, parent=plane)
    polyPlane = mc.createNode('polyPlane', name=planeShapeName)
    mc.connectAttr(polyPlane + '.output', planeShape + '.inMesh', force=True)
    mc.setAttr(polyPlane + '.subdivisionsWidth', 1)
    mc.setAttr(polyPlane + '.subdivisionsHeight', 1)
    
    # 기본 polyPlane geometry: width=1, height = (verticalFilmAperture / horizontalFilmAperture)
    mc.setAttr(polyPlane + ".width", 1)
    exprPolyHeight = '%s.height = %s.verticalFilmAperture / %s.horizontalFilmAperture;' % (polyPlane, cameraShape, cameraShape)
    mc.expression(string=exprPolyHeight, object=polyPlane, alwaysEvaluate=True, unitConversion="all")

    # 1. Expression으로 카메라 파라미터와 imagePlane.depth로부터 basePlaneScale 계산
    exprStr = ''
    exprStr += 'float $f = %s.focalLength;\n' % cameraShape
    exprStr += 'float $fbw = %s.horizontalFilmAperture;\n' % cameraShape
    exprStr += 'float $fbh = %s.verticalFilmAperture;\n' % cameraShape
    exprStr += 'float $fov = rad_to_deg(2 * atan(($fbw*25.4)/(2*$f)));\n'
    exprStr += 'float $planeScale = 2*(%s.depth)*(tand($fov/2.0));\n\n' % imagePlane
    # plane에 사용자 속성(basePlaneScale) 추가
    if not mc.attributeQuery("basePlaneScale", node=plane, exists=True):
        mc.addAttr(plane, ln="basePlaneScale", at="float", dv=1.0)
        mc.setAttr(plane + ".basePlaneScale", e=True, keyable=True)
    exprStr += 'basePlaneScale = $planeScale;\n'
    mc.expression(string=exprStr, object=plane, alwaysEvaluate=True, unitConversion="all")

    # 2. multiplyDivide 노드로 scaleX를 imagePlane.sizeX에 연결
    #    계산: scaleX = basePlaneScale * (sizeX / cameraShape.horizontalFilmAperture)
    scaleX_div = mc.shadingNode("multiplyDivide", asUtility=True, name=planeName + "_scaleX_div")
    mc.setAttr(scaleX_div + ".operation", 2)  # division
    # 기존 coverageX 대신 keyframed sizeX 사용
    mc.connectAttr(imagePlane + ".sizeX", scaleX_div + ".input1X", f=True)
    mc.connectAttr(cameraShape + ".horizontalFilmAperture", scaleX_div + ".input2X", f=True)
    
    scaleX_md = mc.shadingNode("multiplyDivide", asUtility=True, name=planeName + "_scaleX_md")
    mc.setAttr(scaleX_md + ".operation", 1)  # multiplication
    mc.connectAttr(plane + ".basePlaneScale", scaleX_md + ".input1X", f=True)
    mc.connectAttr(scaleX_div + ".outputX", scaleX_md + ".input2X", f=True)
    mc.connectAttr(scaleX_md + ".outputX", plane + ".scaleX", f=True)
    
    # 3. multiplyDivide 노드로 scaleZ를 imagePlane.sizeY에 연결
    #    계산: scaleZ = basePlaneScale * (sizeY / cameraShape.verticalFilmAperture)
    scaleY_div = mc.shadingNode("multiplyDivide", asUtility=True, name=planeName + "_scaleZ_div")
    mc.setAttr(scaleY_div + ".operation", 2)
    # 기존 coverageY 대신 keyframed sizeY 사용
    mc.connectAttr(imagePlane + ".sizeY", scaleY_div + ".input1X", f=True)
    mc.connectAttr(cameraShape + ".verticalFilmAperture", scaleY_div + ".input2X", f=True)
    
    scaleY_md = mc.shadingNode("multiplyDivide", asUtility=True, name=planeName + "_scaleZ_md")
    mc.setAttr(scaleY_md + ".operation", 1)
    mc.connectAttr(plane + ".basePlaneScale", scaleY_md + ".input1X", f=True)
    mc.connectAttr(scaleY_div + ".outputX", scaleY_md + ".input2X", f=True)
    mc.connectAttr(scaleY_md + ".outputX", plane + ".scaleZ", f=True)
    
    # 4. scaleY는 단순히 basePlaneScale에 연결 (깊이 조절용)
    mc.connectAttr(plane + ".basePlaneScale", plane + ".scaleY", f=True)

    # 5. Translation과 Rotation 표현식 (offset, depth 등)
    exprTrans = ''
    exprTrans += 'translateX = basePlaneScale * 0.5 * ((%s.offsetX/2.54)/((%s.horizontalFilmAperture/2.54)*0.5));\n' % (imagePlane, cameraShape)
    exprTrans += 'translateY = basePlaneScale * 0.5 * ((%s.offsetY/2.54)/((%s.horizontalFilmAperture/2.54)*0.5));\n' % (imagePlane, cameraShape)
    exprTrans += 'translateZ = -1 * %s.depth;\n' % imagePlane
    exprTrans += 'rotateX = 90.0;\n'
    exprTrans += 'rotateY = 0.0;\n'
    exprTrans += 'rotateZ = 0.0;\n'
    mc.expression(string=exprTrans, object=plane, alwaysEvaluate=True, unitConversion="all")
    
    return (plane, planeShape, polyPlane)

def imageSeq(*args):
    global planeShader
    planeShader = mc.shadingNode("surfaceShader", asShader=True, n="imagePlaneShader")
    texture = mc.shadingNode('file', asTexture=True, isColorManaged=True)
    pPlace2d = mc.shadingNode('place2dTexture', asUtility=True)
    cmds.connectAttr(pPlace2d + '.coverage', texture + '.coverage', f=True)
    cmds.connectAttr(pPlace2d + '.translateFrame', texture + '.translateFrame', f=True)
    cmds.connectAttr(pPlace2d + '.rotateFrame', texture + '.rotateFrame', f=True)
    cmds.connectAttr(pPlace2d + '.mirrorU', texture + '.mirrorU', f=True)
    cmds.connectAttr(pPlace2d + '.mirrorV', texture + '.mirrorV', f=True)
    cmds.connectAttr(pPlace2d + '.stagger', texture + '.stagger', f=True)
    cmds.connectAttr(pPlace2d + '.wrapU', texture + '.wrapU', f=True)
    cmds.connectAttr(pPlace2d + '.wrapV', texture + '.wrapV', f=True)
    cmds.connectAttr(pPlace2d + '.repeatUV', texture + '.repeatUV', f=True)
    cmds.connectAttr(pPlace2d + '.offset', texture + '.offset', f=True)
    cmds.connectAttr(pPlace2d + '.rotateUV', texture + '.rotateUV', f=True)
    cmds.connectAttr(pPlace2d + '.noiseUV', texture + '.noiseUV', f=True)
    cmds.connectAttr(pPlace2d + '.vertexUvOne', texture + '.vertexUvOne', f=True)
    cmds.connectAttr(pPlace2d + '.vertexUvTwo', texture + '.vertexUvTwo', f=True)
    cmds.connectAttr(pPlace2d + '.vertexUvThree', texture + '.vertexUvThree', f=True)
    cmds.connectAttr(pPlace2d + '.vertexCameraOne', texture + '.vertexCameraOne', f=True)
    cmds.connectAttr(pPlace2d + '.outUV', texture + '.uv')
    cmds.connectAttr(pPlace2d + '.outUvFilterSize', texture + '.uvFilterSize')
    
    cmds.setAttr(texture + '.fileTextureName', "%s" % seqPath, type="string")
    cmds.expression(n="frame_ext_expression", s=texture + ".frameExtension=frame")
    cmds.setAttr(texture + '.useFrameExtension', 1)
    
    cmds.connectAttr(texture + '.outColor', planeShader + '.outColor', f=True)

def polyImagePlane():
    camera = None
    cameraShape = None
    imagePlane = None
    global seqPath

    selCam = cmds.ls(sl=1)[0]
    camShape = cmds.listRelatives(selCam, type="shape")[0]
    tmp = cmds.listConnections(camShape, type="imagePlane", shapes=True)
    if len(tmp) > 0:
        imagePlane = tmp[0]
    else:
        return False
    conn = mc.listConnections(imagePlane, type="camera", shapes=True)
    if len(conn) > 0:
        cameraShape = getLongName(conn[0])
        camera = cmds.listRelatives(cameraShape, parent=True)[0]
        camera = getLongName(camera)
    else:
        return False
    seqPath = cmds.getAttr("%s.imageName" % imagePlane)
    plane, planeShape, polyPlane = createPolyImagePlane(camera, cameraShape, imagePlane)
    mc.select(plane, replace=True)
    imageSeq()

    cmds.select(planeShapeName)
    cmds.hyperShade(assign=planeShader)
    
    return True

