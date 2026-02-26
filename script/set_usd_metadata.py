#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
import json
from pxr import Usd, Sdf

def run_set_usd_metadata(usd_path, scale, prefix):
    if not os.path.isfile(usd_path):
        raise FileNotFoundError(usd_path)

    # Stage 열기
    stage = Usd.Stage.Open(usd_path)
    layer = stage.GetRootLayer()  # Sdf.Layer 객체

    # 원하는 내용을 doc 필드에 JSON 문자열로 설정
    layer.documentation = json.dumps({prefix: scale})

    # 저장
    layer.Save()
    print(f"[OK] {usd_path} → doc = {layer.documentation}")

# usd_path = '/show/ORV/seq/TST/TST_0100/ani/wip/usd/TST_0100_ani_v02_w02/twoWayTunnel1/twoWayTunnel1.usda'
# scale = 0.2
# prefix = 'twoWayTunnel1'