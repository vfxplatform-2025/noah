# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Noah is a Python-based VFX pipeline tool package (version 1.9.0) designed for 3D content creation workflows. It supports multiple DCC applications including Maya and Clarisse, providing unified export/import functionality for various asset types and render formats.

## Environment and Dependencies

- **Python Version**: Python 2.7.15 (legacy pipeline requirement)
- **Package Manager**: REZ package management system
- **Build System**: Uses `build.rxt` configuration file for REZ package builds
- **UI Framework**: PySide2 for Qt-based user interfaces

## Key Architecture Components

### Core Modules
- `cacheExport.py` - Main export functionality and UI controller
- `noah.py`, `noah_cl.py`, `noah_cl_dev.py` - Entry points for different configurations
- `package.py` - REZ package definition with environment setup

### Application Detection
The codebase uses environment variable `APPNAME` to detect the host application:
- `APPNAME="clarisse"` - Clarisse 3D integration
- Default (Maya) - Autodesk Maya integration

### Module Structure
- `cacheExport_module/` - Core export functionality modules
  - `cacheExport_moduleImport.py` - Application-specific imports and configuration
  - `pyside2_moduleImport.py` - PySide2 UI imports
  - `clarisse_module/` - Clarisse-specific PySide2 binaries and resources
- `script/` - Individual export scripts for different asset types
- `config/` - Configuration files including `typeConfig.ini` for asset type mappings

### Export Scripts Organization
Scripts are organized by pipeline stage and asset type:
- **Animation**: `alembicScript.py`, `atomScript.py`, `cameraScript.py`
- **Models**: `modelScript.py`, `modelEnvScript.py`, `geoCacheScript.py`
- **Simulation**: `fxScript.py`, `vdbScript.py`, `yetiCacheScript.py`
- **Rendering**: `assScript.py`, `lightRigScript.py`, `lookdevScript.py`
- **Utilities**: `utilScript.py`, `dataScript.py`, `shotgunScript.py`

### Asset Type Configuration
`config/typeConfig.ini` defines mappings between pipeline stages and export formats:
- Alembic exports for animation, simulation, and geometry
- Maya native formats for scene data
- Clarisse-specific exports for lighting and rendering
- Arnold ASS files for render data
- USD/USDA support for modern workflows

### UI Components
- `cacheExportUI.ui`, `cacheExportAsset.ui` - Qt Designer UI files
- `commentWindow.py` - Comment/annotation system
- `modal_widget.py` - Custom modal dialog components
- `cacheExport_style/qtmodern/` - Modern Qt styling framework

### Reference Management
- `referenceSettings/` - Reference and dependency management system
- `meshReplace.ui` - Mesh replacement UI
- `nodeModel.py` - Node-based data model for references

## Common Development Tasks

### Running the Application
```bash
# Standard launch
python noah.py

# Clarisse mode
APPNAME=clarisse python noah_cl.py

# Development mode
python noah_cl_dev.py
```

### Package Building
The project uses REZ package management:
```bash
# Build package (configuration in build.rxt)
rez-build

# Install package
rez-build --install
```

### Configuration Updates
- Asset type mappings: Edit `config/typeConfig.ini`
- Alembic options: Modify `config/alembicOption.ini`
- UI styling: Update files in `cacheExport_style/qtmodern/resources/`

### Deployment (배포)
When deploying Noah package to production, use copy method instead of REZ build:
```bash
# Production deployment path (배포 경로)
# IMPORTANT: Use /storage/.NAS5/core/... NOT /core/...
DEPLOY_PATH="/storage/.NAS5/core/Linux/APPZ/packages/noah/1.9.0"

# Copy all files to production (전체 파일 복사)
cp -r /storage/.NAS5/rocky9_core/TD/users/chulho/packages/noah/1.9.0/* $DEPLOY_PATH/

# Or copy specific modified files only (수정된 파일만 복사)
cp cacheExport.py $DEPLOY_PATH/
cp cacheExportUI.ui $DEPLOY_PATH/
```

**Note**: Always use the full path starting with `/storage/.NAS5/` for deployment, not the symbolic link `/core/`.

## Integration Points

### Shotgun Integration
- `script/shotgunScript.py` - Shotgun API integration for asset tracking
- `script/sg_focalLength.py` - Camera focal length data from Shotgun

### Render Farm Integration
- `script/tractorJobScript.py` - Pixar Tractor job submission
- `script/tractorCmdScript.py` - Command-line render job utilities

### USD Pipeline
- `script/usd_export.py` - USD export functionality
- `script/usd_model_pub.py` - USD model publishing
- `script/make_ani_usda.py` - Animation USD export

## File Naming Conventions

- Scripts follow `[type]Script.py` pattern (e.g., `alembicScript.py`)
- Module imports use `[name]_moduleImport.py` pattern
- UI files use `.ui` extension for Qt Designer files
- Configuration files use `.ini` format with ConfigParser

## Legacy Considerations

This is a Python 2.7 codebase with legacy VFX pipeline dependencies. When making changes:
- Maintain Python 2.7 compatibility
- Respect existing import patterns using `imp.reload()`
- Preserve REZ package structure and dependencies
- Test changes across both Maya and Clarisse environments