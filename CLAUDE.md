# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🎯 Current Status (Updated)

**Project State:** Ready for testing - Phased implementation approach
**Last Updated:** 2025-01-07

### Current Configuration

**Active Commands:**
- ✅ `commandDialog` - Test command (Phase 1 verification)
- ⚠️ `contour` - Main Contour feature (commented out, ready to enable)

**Disabled Commands:**
- ❌ `paletteShow` - Commented out
- ❌ `paletteSend` - Commented out

**Next Step:** Follow QUICKSTART.md for step-by-step testing

---

## Project Overview

This is a Fusion 360 Add-in built using Python and the Fusion 360 API. The add-in follows Autodesk's standard template structure for Fusion 360 add-ins with a command-based architecture.

## Development Environment

**Location:** This add-in is installed at:
```
/Users/hiroshi.kimura/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/Rhino-Contour/
```

**Testing in Fusion 360:**
1. Open Fusion 360
2. Navigate to **Utilities → Add-Ins** (or press Shift+S)
3. Select "My Add-Ins" tab
4. Find "Rhino-Contour" in the list
5. Click "Run" to test changes

**Debugging:**
- Set `DEBUG = True` in `config.py` to enable verbose logging
- Logs appear in Fusion 360's Text Command window
- Error messages are logged to Fusion 360's log file
- Python print statements appear in the IDE console

## Architecture

### Entry Point
- `Rhino-Contour.py`: Main entry point with `run()` and `stop()` functions
- `config.py`: Global configuration (company name, add-in name, palette IDs, debug flag)

### Command Structure
The add-in uses a modular command architecture where each command is a separate module:

```
commands/
├── __init__.py              # Registers all commands
├── commandDialog/           # Dialog-based command example
│   ├── entry.py            # Command implementation
│   └── resources/          # Icons (16x16, 32x32, 64x64)
├── paletteShow/            # HTML palette command
│   ├── entry.py            # Command implementation
│   └── resources/
│       ├── html/
│       │   ├── index.html
│       │   └── static/palette.js
│       └── icons/
└── paletteSend/            # Palette communication example
    └── entry.py
```

**Adding a New Command:**
1. Duplicate an existing command directory (e.g., `commandDialog/`)
2. Modify the `entry.py` file with your command logic
3. Update `CMD_ID`, `CMD_NAME`, `CMD_Description` constants
4. Import the new command in `commands/__init__.py`
5. Add it to the `commands` list

### Key Command Lifecycle
Each command module must implement:
- `start()`: Called when add-in starts - creates UI buttons and registers event handlers
- `stop()`: Called when add-in stops - cleans up UI elements and handlers
- `command_created()`: Defines the command dialog and connects event handlers
- `command_execute()`: Main command logic when user clicks OK

### Event Handler Management
**Critical:** Event handlers must be maintained in memory to prevent garbage collection.
- Use `futil.add_handler()` to register handlers (automatically tracked)
- Use `local_handlers = []` list for command-specific handlers
- Clear all handlers in `command_destroy()` with `local_handlers = []`

### Palette (HTML UI) Commands
Palette commands display HTML interfaces within Fusion 360:
- HTML files stored in `commands/[command_name]/resources/html/`
- JavaScript communicates with Python via `adsk.fusionSendData()` (JS → Python)
- Python returns data via `html_args.returnData` (Python → JS)
- Handle events in `palette_incoming()` function

### Utility Functions (`lib/fusionAddInUtils/`)
- `futil.log(message, level, force_console)`: Logging with debug mode support
- `futil.handle_error(name, show_message_box)`: Centralized error handling
- `futil.add_handler()`: Register event handlers with automatic tracking
- `futil.clear_handlers()`: Clean up all registered event handlers

## Configuration

**Company and Add-in Identity:**
Edit `config.py` to customize:
```python
COMPANY_NAME = 'ACME'  # Change to your company name
ADDIN_NAME = 'Rhino-Contour'  # Automatically set from folder name
```

**UI Placement:**
Each command specifies where its button appears:
```python
WORKSPACE_ID = 'FusionSolidEnvironment'  # The workspace
PANEL_ID = 'SolidScriptsAddinsPanel'    # The toolbar panel
COMMAND_BESIDE_ID = 'ScriptsManagerCommand'  # Position relative to this command
IS_PROMOTED = True  # Show in main toolbar vs dropdown
```

## Important Notes

- **Event Handler References:** Always maintain references to event handlers in a list to prevent garbage collection
- **Command IDs:** Must be globally unique - use `{COMPANY_NAME}_{ADDIN_NAME}_{CommandName}` pattern
- **Palette IDs:** Defined in `config.py` for reuse across commands
- **Resource Paths:** Use `os.path.join()` with `__file__` for cross-platform compatibility
- **Web Browser:** Set `useNewWebBrowser=True` for modern HTML/CSS/JS support in palettes
