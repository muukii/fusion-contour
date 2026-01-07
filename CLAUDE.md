# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Split with Planes** - Fusion 360 Add-in for splitting bodies with parallel construction planes.

This add-in allows users to:
- Select bodies to split
- Choose start and end points to define the split direction
- Specify number of divisions
- Automatically create construction planes and split the bodies

## Development Environment

**Location:**
```
/Users/hiroshi.kimura/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/Rhino-Contour/
```

**Testing:**
1. Open Fusion 360
2. Navigate to **Utilities → Add-Ins** (or press Shift+S)
3. Select "My Add-Ins" tab
4. Find "Rhino-Contour" and click "Run"

**Debugging:**
- Set `DEBUG = True` in `config.py` for verbose logging
- Logs appear in Fusion 360's Text Command window

## Architecture

### File Structure
```
Rhino-Contour/
├── Rhino-Contour.py          # Entry point (run/stop)
├── config.py                  # Global configuration
├── commands/
│   ├── __init__.py           # Command registration
│   └── contour/
│       ├── __init__.py
│       ├── entry.py          # Main command implementation
│       └── resources/        # Icons (16x16, 32x32, 64x64)
└── lib/
    └── fusionAddInUtils/     # Utility functions
```

### Key Functions (commands/contour/entry.py)

- `start()` / `stop()` - Add-in lifecycle
- `command_created()` - Creates UI dialog with inputs
- `command_execute()` - Main execution logic
- `split_bodies_with_planes()` - Core splitting algorithm
- `get_point_from_selection()` - Extract Point3D from selection

### Splitting Algorithm

1. Calculate direction from start to end point
2. Verify direction aligns with X, Y, or Z axis
3. Create construction planes at equal intervals
4. Split bodies using SplitBodyFeature
5. Clean up construction planes

## UI Inputs

- **Bodies** - Select solid bodies to split (1 or more)
- **Start Point** - Vertex, SketchPoint, or ConstructionPoint
- **End Point** - Vertex, SketchPoint, or ConstructionPoint
- **Number of Divisions** - Integer (1-100, default: 5)

## Limitations

- Direction must align with X, Y, or Z axis
- Start/End points must be on axis-aligned line

## Configuration

Edit `config.py`:
```python
DEBUG = True          # Enable verbose logging
COMPANY_NAME = 'ACME' # Used in command IDs
```

## Event Handler Management

**Critical:** Event handlers must be maintained in `local_handlers` list to prevent garbage collection.

```python
local_handlers = []

# In command_created:
futil.add_handler(args.command.execute, command_execute, local_handlers=local_handlers)

# In command_destroy:
local_handlers = []
```
