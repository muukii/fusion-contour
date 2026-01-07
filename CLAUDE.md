# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Contour** - Fusion 360 Add-in for creating contour curves or splitting bodies with parallel planes.

Similar to Rhino's Contour command, this add-in:
- Creates intersection curves between bodies and parallel planes
- Or splits bodies into multiple parts

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
│       ├── entry.py          # Main command implementation (~450 lines)
│       └── resources/        # Icons (16x16, 32x32, 64x64)
└── lib/
    └── fusionAddInUtils/     # Utility functions
```

### Key Functions (commands/contour/entry.py)

#### Core Functions
- `start()` / `stop()` - Add-in lifecycle
- `command_created()` - Creates UI dialog with inputs
- `command_execute()` - Routes to appropriate mode handler

#### Mode Handlers
- `create_contour_curves()` - Creates intersection curves in a sketch
- `split_bodies_with_planes()` - Splits bodies using construction planes

#### Helper Functions
- `get_point_from_selection()` - Extract Point3D from selection
- `get_axis_info()` - Determine axis alignment and base plane
- `copy_curve_to_output_sketch()` - Copy curves between sketches

### Algorithm: Contour Curves

1. Validate direction is aligned with X, Y, or Z axis
2. Create output sketch on the appropriate base plane
3. For each division point:
   a. Create temporary construction plane at offset
   b. Create temporary sketch on that plane
   c. Use `Sketch.intersectWithSketchPlane(bodies)` to get curves
   d. Copy curves to output sketch (preserving 3D positions)
   e. Delete temporary sketch and plane
4. Optionally delete original bodies

### Algorithm: Split Body

1. Validate direction is aligned with X, Y, or Z axis
2. Create construction planes at division points
3. For each plane, split all solid bodies
4. Delete construction planes

## UI Inputs

- **Mode** - "Contour Curves" or "Split Body"
- **Bodies** - Select solid bodies (1 or more)
- **Start Point** - Vertex, SketchPoint, or ConstructionPoint
- **End Point** - Vertex, SketchPoint, or ConstructionPoint
- **Number of Divisions** - Integer (2-100, default: 5)
- **Delete Original Bodies** - Boolean (Contour Curves mode only)

## Curve Type Support

The `copy_curve_to_output_sketch()` function handles:
- SketchLine
- SketchArc
- SketchCircle
- SketchEllipse
- SketchFittedSpline
- Other curves (sampled as fitted spline)

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
