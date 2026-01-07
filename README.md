# Split with Planes - Fusion 360 Add-in

A Fusion 360 add-in for splitting bodies with parallel construction planes. Divides bodies into equal segments between two points.

## Features

- Split multiple bodies at once
- Define direction and distance using start/end points
- Set number of divisions (1-100)
- Automatic creation and cleanup of construction planes

## Usage

### 1. Start the Add-in
- Open Fusion 360
- Press `Shift+S` → Select "Rhino-Contour" → Click **Run**

### 2. Execute the Command
- Click the **"Split with Planes"** button in the toolbar

### 3. Set Parameters

| Parameter | Description |
|-----------|-------------|
| **Bodies** | Select bodies to split (multiple selection allowed) |
| **Start Point** | Starting point (vertex, sketch point, or construction point) |
| **End Point** | Ending point (vertex, sketch point, or construction point) |
| **Number of Divisions** | Number of divisions (default: 5) |

### 4. Execute
- Click **OK**
- Bodies will be split into the specified number of parts

## Example

### Split a Cube into 5 Parts
1. Create a cube
2. Bodies: Select the cube
3. Start Point: Select a vertex on the bottom face
4. End Point: Select a vertex on the top face (directly above)
5. Number of Divisions: 5
6. Click OK → Cube is split into 5 bodies

```
Before:           After:
┌─────────┐      ┌─────────┐
│         │      ├─────────┤
│         │  →   ├─────────┤
│         │      ├─────────┤
│         │      ├─────────┤
└─────────┘      └─────────┘
```

## Limitations

- Direction must be parallel to X, Y, or Z axis
- Arbitrary (angled) directions are not currently supported

## Installation Location

```
/Users/hiroshi.kimura/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/Rhino-Contour/
```

## File Structure

```
Rhino-Contour/
├── Rhino-Contour.py      # Entry point
├── config.py             # Configuration (DEBUG=True/False)
├── commands/
│   └── contour/
│       └── entry.py      # Main implementation
└── lib/
    └── fusionAddInUtils/ # Utilities
```

## Troubleshooting

### Button Not Appearing
- Restart the add-in: Stop → Run

### Errors Occurring
- Check logs in Text Commands window
- Set `DEBUG = True` in `config.py`

### Bodies Not Splitting
- Verify start/end points are aligned with X/Y/Z axis
- Check if bodies intersect with the planes

## License

Based on Autodesk Fusion 360 Add-in Template
