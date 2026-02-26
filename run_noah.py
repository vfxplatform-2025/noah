#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Noah Cache Export Tool Runner
Proper startup script for Noah tool that handles environment setup
"""

import sys
import os

def main():
    # Set NOAH_ROOT environment variable
    noah_root = '/storage/.NAS5/rocky9_core/TD/users/chulho/packages/noah/1.9.0'
    os.environ['NOAH_ROOT'] = noah_root
    
    # Add noah path to sys.path at the beginning to avoid conflicts
    if noah_root not in sys.path:
        sys.path.insert(0, noah_root)
    
    print("=" * 50)
    print("NOAH CACHE EXPORT TOOL STARTUP")
    print("=" * 50)
    print(f"NOAH_ROOT: {noah_root}")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print("=" * 50)
    
    try:
        # Import and run cacheExport
        import cacheExport
        import importlib
        importlib.reload(cacheExport)
        cacheExport.cacheExport()
        
    except ImportError as e:
        print(f"Import Error: {e}")
        print("\nThis tool requires Maya environment with PySide6.")
        print("Please run this script within Maya or with mayapy.")
        print("\nSuggested usage:")
        print("1. Open Maya")
        print("2. Run in Maya Script Editor:")
        print(f'   exec(open("{noah_root}/run_noah.py").read())')
        sys.exit(1)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()