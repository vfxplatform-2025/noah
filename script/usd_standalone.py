#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
USD Standalone Export Script for Tractor Farm
This script runs in Maya standalone mode for farm USD exports
"""

import os
import sys
import argparse
from maya import standalone, cmds
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import usdScript

def main():
    """Main function for USD standalone export"""
    # Parse arguments
    parser = argparse.ArgumentParser(description='USD Export in Maya Standalone')
    parser.add_argument('--scene', required=True, help='Maya scene file path')
    parser.add_argument('--object', required=True, help='Object to export')
    parser.add_argument('--output', required=True, help='Output USD file path')
    parser.add_argument('--start', type=int, required=True, help='Start frame')
    parser.add_argument('--end', type=int, required=True, help='End frame')
    parser.add_argument('--step', type=int, default=1, help='Frame step')
    parser.add_argument('--defaultPrim', required=True, help='Default primitive name')
    
    args = parser.parse_args()
    
    try:
        # Initialize Maya standalone
        print("Initializing Maya standalone...")
        standalone.initialize()
        
        # Load USD plugin
        print("Loading Maya USD plugin...")
        cmds.loadPlugin('mayaUsdPlugin.so')
        
        # Open scene file
        print("Opening scene: {}".format(args.scene))
        cmds.file(args.scene, force=True, open=True)
        
        # Select object for export
        print("Selecting object: {}".format(args.object))
        object_fullpath = cmds.ls(args.object, l=1)[0]
        cmds.select(object_fullpath, r=True)
        
        # Use common USD options function from usdScript
        usdOptions = usdScript.get_usd_export_options(
            start_frame=args.start,
            end_frame=args.end,
            step=args.step,
            default_prim=args.defaultPrim,
            euler_filter=False  # Updated to match new options (eulerFilter=0)
        )
        
        # Export USD
        print("Exporting USD to: {}".format(args.output))
        print("Frame range: {} - {} (step: {})".format(args.start, args.end, args.step))
        print("USD Options: {}".format(usdOptions))
        
        cmds.file(args.output, 
                  force=True, 
                  options=usdOptions,
                  typ='USD Export', 
                  pr=True, 
                  es=True)
        
        # Clear selection
        cmds.select(cl=1)
        
        print("USD Export completed successfully!")
        
    except Exception as e:
        print("ERROR in USD standalone export: {}".format(str(e)))
        sys.exit(1)
        
    finally:
        # Uninitialize Maya
        try:
            standalone.uninitialize()
            os._exit(0)
        except:
            os._exit(1)

if __name__ == "__main__":
    main()