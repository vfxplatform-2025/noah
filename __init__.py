import os, sys


rootDir = os.path.abspath(__file__ + "/../")
sys.path.append(rootDir)
sys.path.append("/core/TD/pipeline/usd_script")

APPNAME = os.getenv('APPNAME')
