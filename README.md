# Contour - Fusion 360 Add-in

<img width="1512" height="948" alt="image" src="https://github.com/user-attachments/assets/34928a65-305c-40cc-af79-ab572ff4dac1" />

<img width="1512" height="948" alt="image" src="https://github.com/user-attachments/assets/c05d844e-d074-4756-85f3-838dda1e8e7b" />

<img width="797" height="649" alt="image" src="https://github.com/user-attachments/assets/59dbabb3-79c6-4a33-aa46-330d7b59bc44" />


A Fusion 360 add-in for creating contour curves or splitting bodies with parallel planes. Similar to Rhino's Contour command.

## Features

### Mode 1: Contour Curves (Default)
- Creates intersection curves between bodies and parallel planes
- All curves are collected into a single sketch
- Optionally delete original bodies after creating curves
- Perfect for creating cross-section profiles

### Mode 2: Split Body
- Splits bodies into multiple parts using parallel planes
- Construction planes are automatically cleaned up after splitting

## Usage

### 1. Start the Add-in
- Open Fusion 360
- Press `Shift+S` → Select "Rhino-Contour" → Click **Run**

### 2. Execute the Command
- Click the **"Contour"** button in the toolbar

### 3. Set Parameters

| Parameter | Description |
|-----------|-------------|
| **Mode** | Choose "Contour Curves" or "Split Body" |
| **Bodies** | Select bodies (multiple selection allowed) |
| **Start Point** | Starting point (vertex, sketch point, or construction point) |
| **End Point** | Ending point (vertex, sketch point, or construction point) |
| **Number of Divisions** | Number of sections (default: 5) |
| **Delete Original Bodies** | (Contour Curves mode only) Remove bodies after creating curves |

### 4. Execute
- Click **OK**
- Contour curves will be created in a new sketch named "Contours"
- Or bodies will be split into the specified number of parts

## Example

### Create 5 Contour Sections
1. Create a complex 3D shape
2. Mode: Contour Curves
3. Bodies: Select the shape
4. Start Point: Select a vertex on the bottom
5. End Point: Select a vertex on the top (directly above)
6. Number of Divisions: 5
7. Delete Original Bodies: Checked
8. Click OK → 6 cross-section curves created (5 divisions = 6 sections)

```
Original Body:          Result (6 sections):
    ___                     ___  ← Section 6
   /   \                   /   \
  |     |                 |     | ← Section 5
  |     |        →        |     | ← Section 4
  |     |                 |     | ← Section 3
  |     |                 |     | ← Section 2
  \_____/                 \_____/ ← Section 1
```

## Limitations

- Direction must be parallel to X, Y, or Z axis
- Arbitrary (angled) directions are not currently supported

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

### No Curves Created
- Verify start/end points are aligned with X/Y/Z axis
- Check if bodies intersect with the planes at the specified positions

## License

Based on Autodesk Fusion 360 Add-in Template
