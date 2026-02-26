# -*- coding:utf-8 -*-

import sys
sys.path.append("/core/TD/m83sg/handler")
from m83sg import sg_connect
from pprint import pprint

def getShotInfo(projV, seqV, shotV):
    sgl = sg_connect()
    sg = sgl.script_auth(script_name='noha', api_key='w7ahp&fjulyfpsronbgxKmefl')

    filters = [
        ['code', 'is', shotV],
        ['project.Project.name', 'is', projV]
    ]

    fields = ['assets']

    shotInfo = sg.find_one('Shot', filters, fields)
    #pprint(shotV)

    return shotInfo
