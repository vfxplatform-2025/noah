import os
import alembic
import ast


def copy_props(i_props, o_props):
    '''
    Copy properties
    '''
    for index in range(i_props.getNumProperties()):
        header = i_props.getPropertyHeader(index)
        if header.isArray():
            i_prop = alembic.Abc.IArrayProperty(i_props, header.getName())
            prop_name = i_prop.getName()
            prop_meta = i_prop.getMetaData()
            o_prop = alembic.Abc.OArrayProperty(o_props, prop_name, i_prop.getDataType(), prop_meta, 0)
            o_prop.setTimeSampling(i_prop.getTimeSampling())
            for i in range(i_prop.getNumSamples()):
                o_prop.setValue(i_prop.getValue(i))
        elif header.isScalar():
            i_prop = alembic.Abc.IScalarProperty(i_props, header.getName())
            prop_name = i_prop.getName()
            prop_meta = i_prop.getMetaData()
            o_prop = alembic.Abc.OScalarProperty(o_props, prop_name, i_prop.getDataType(), prop_meta, 0)
            o_prop.setTimeSampling(i_prop.getTimeSampling())
            for i in range(i_prop.getNumSamples()):
                o_prop.setValue(i_prop.getValue(i))
        elif header.isCompound():
            i_prop = alembic.Abc.ICompoundProperty(i_props, header.getName())
            prop_name = i_prop.getName()
            prop_meta = i_prop.getMetaData()
            o_prop = alembic.Abc.OCompoundProperty(o_props, prop_name, prop_meta)
            copy_props(i_prop, o_prop)


def copy_object(i_obj, o_obj):
    '''
    Recursively copy object data
    '''
    if o_obj is None:
        return
    i_props = i_obj.getProperties()
    o_props = o_obj.getProperties()
    copy_props(i_props, o_props)
    for index in range(i_obj.getNumChildren()):
        i_child = i_obj.getChild(index)
        i_child_name = i_child.getName()
        i_child_meta = i_child.getMetaData()
        o_child = alembic.Abc.OObject(o_obj, i_child_name, i_child_meta)
        copy_object(i_child, o_child)


def copy_abc(i_path, o_path, app, description):
    '''
    Copy alembic file from i_path to o_path with metadata info.
    '''
    arc_in = alembic.Abc.IArchive(i_path)
    # 새로운 Alembic 파일 생성 시 metadata 정보(app, description)를 설정합니다.
    arc_out = alembic.Abc.CreateArchiveWithInfo(o_path, app, description)
    top_in = arc_in.getTop()
    top_out = arc_out.getTop()
    copy_object(top_in, top_out)


def read(abc_file):
    archive = alembic.Abc.IArchive(abc_file)
    return alembic.Abc.GetArchiveInfo(archive)


def run_set_alembic_metadata(item, scale):
    origin_path = item
    temp_path = item.split('.')[0]+'_meta.abc'
    print('RUN SET ALEMBIC METADATA Script <<<<<<<<<<<<<<<<<<<<<<<<<')
    copy_abc(item, temp_path, 'Maya 2024 AbcExport v1.0', '{"scale":%s}' % scale)
    os.replace(temp_path, origin_path)



