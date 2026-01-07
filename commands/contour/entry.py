import adsk.core
import adsk.fusion
import os
from ...lib import fusionAddInUtils as futil
from ... import config

app = adsk.core.Application.get()
ui = app.userInterface

# Command identity
CMD_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_contour'
CMD_NAME = 'Split with Planes'
CMD_Description = 'Split bodies with parallel construction planes between two points'

IS_PROMOTED = True

# UI location
WORKSPACE_ID = 'FusionSolidEnvironment'
PANEL_ID = 'SolidScriptsAddinsPanel'
COMMAND_BESIDE_ID = 'ScriptsManagerCommand'

ICON_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', '')

# Event handlers reference
local_handlers = []


def start():
    try:
        cmd_def = ui.commandDefinitions.addButtonDefinition(CMD_ID, CMD_NAME, CMD_Description, ICON_FOLDER)
        futil.add_handler(cmd_def.commandCreated, command_created)

        workspace = ui.workspaces.itemById(WORKSPACE_ID)
        panel = workspace.toolbarPanels.itemById(PANEL_ID)
        control = panel.controls.addCommand(cmd_def, COMMAND_BESIDE_ID, False)
        control.isPromoted = IS_PROMOTED
        
        futil.log(f'{CMD_NAME} command started successfully')
    except:
        futil.handle_error('Failed to start command')


def stop():
    try:
        workspace = ui.workspaces.itemById(WORKSPACE_ID)
        panel = workspace.toolbarPanels.itemById(PANEL_ID)
        command_control = panel.controls.itemById(CMD_ID)
        command_definition = ui.commandDefinitions.itemById(CMD_ID)

        if command_control:
            command_control.deleteMe()
        if command_definition:
            command_definition.deleteMe()
        
        futil.log(f'{CMD_NAME} command stopped successfully')
    except:
        futil.handle_error('Failed to stop command')


def command_created(args: adsk.core.CommandCreatedEventArgs):
    futil.log(f'{CMD_NAME} Command Created Event')

    inputs = args.command.commandInputs

    # Body selection (multiple)
    body_select = inputs.addSelectionInput('body_select', 'Bodies', 'Select bodies to split')
    body_select.addSelectionFilter('SolidBodies')
    body_select.setSelectionLimits(1, 0)  # 1 to unlimited

    # Start point selection
    start_point = inputs.addSelectionInput('start_point', 'Start Point', 'Select start point')
    start_point.addSelectionFilter('Vertices')
    start_point.addSelectionFilter('SketchPoints')
    start_point.addSelectionFilter('ConstructionPoints')
    start_point.setSelectionLimits(1, 1)

    # End point selection
    end_point = inputs.addSelectionInput('end_point', 'End Point', 'Select end point')
    end_point.addSelectionFilter('Vertices')
    end_point.addSelectionFilter('SketchPoints')
    end_point.addSelectionFilter('ConstructionPoints')
    end_point.setSelectionLimits(1, 1)

    # Number of divisions
    inputs.addIntegerSpinnerCommandInput('divisions', 'Number of Divisions', 1, 100, 1, 5)

    # Connect event handlers
    futil.add_handler(args.command.execute, command_execute, local_handlers=local_handlers)
    futil.add_handler(args.command.inputChanged, command_input_changed, local_handlers=local_handlers)
    futil.add_handler(args.command.executePreview, command_preview, local_handlers=local_handlers)
    futil.add_handler(args.command.validateInputs, command_validate_input, local_handlers=local_handlers)
    futil.add_handler(args.command.destroy, command_destroy, local_handlers=local_handlers)


def command_execute(args: adsk.core.CommandEventArgs):
    futil.log(f'{CMD_NAME} Command Execute Event')

    inputs = args.command.commandInputs

    # Get inputs
    body_select: adsk.core.SelectionCommandInput = inputs.itemById('body_select')
    start_point_input: adsk.core.SelectionCommandInput = inputs.itemById('start_point')
    end_point_input: adsk.core.SelectionCommandInput = inputs.itemById('end_point')
    divisions_input: adsk.core.IntegerSpinnerCommandInput = inputs.itemById('divisions')

    # Collect bodies
    bodies = []
    for i in range(body_select.selectionCount):
        bodies.append(body_select.selection(i).entity)

    # Get start and end points
    start_point = get_point_from_selection(start_point_input.selection(0).entity)
    end_point = get_point_from_selection(end_point_input.selection(0).entity)

    # Get number of divisions
    divisions = divisions_input.value

    # Execute split operation
    try:
        futil.log(f'=== Starting Body Split ===')
        futil.log(f'Bodies: {len(bodies)}')
        futil.log(f'Start point: {start_point.asArray()}')
        futil.log(f'End point: {end_point.asArray()}')
        futil.log(f'Divisions: {divisions}')
        
        split_bodies_with_planes(bodies, start_point, end_point, divisions)
        
        futil.log(f'=== Body Split Completed ===')
    except Exception as e:
        error_msg = f'Error splitting bodies: {str(e)}'
        ui.messageBox(error_msg)
        futil.log(error_msg, adsk.core.LogLevels.ErrorLogLevel)
        futil.handle_error('Body Split Failed')


def get_point_from_selection(entity) -> adsk.core.Point3D:
    """Extract Point3D from various selection types."""
    if hasattr(entity, 'geometry'):
        geom = entity.geometry
        if isinstance(geom, adsk.core.Point3D):
            return geom.copy()
    if hasattr(entity, 'worldGeometry'):
        return entity.worldGeometry.copy()
    if isinstance(entity, adsk.fusion.BRepVertex):
        return entity.geometry.copy()
    if isinstance(entity, adsk.fusion.SketchPoint):
        return entity.geometry.copy()

    raise ValueError(f'Cannot extract point from {type(entity)}')


def split_bodies_with_planes(bodies, start_point: adsk.core.Point3D, end_point: adsk.core.Point3D, divisions: int):
    """Split bodies with parallel construction planes between start and end points."""
    design = adsk.fusion.Design.cast(app.activeProduct)
    rootComp = design.rootComponent
    
    # Calculate direction vector
    direction = start_point.vectorTo(end_point)
    total_distance = direction.length
    direction.normalize()
    
    futil.log(f'Direction: {direction.asArray()}, Total distance: {total_distance} cm')
    
    # Determine which axis we're aligned with
    xAxis = adsk.core.Vector3D.create(1, 0, 0)
    yAxis = adsk.core.Vector3D.create(0, 1, 0)
    zAxis = adsk.core.Vector3D.create(0, 0, 1)
    
    dotX = abs(direction.dotProduct(xAxis))
    dotY = abs(direction.dotProduct(yAxis))
    dotZ = abs(direction.dotProduct(zAxis))
    
    # Determine base plane (use rootComponent for correct world coordinates)
    basePlane = None
    axisName = None
    
    if dotX > 0.999:
        basePlane = rootComp.yZConstructionPlane
        axisName = 'X'
    elif dotY > 0.999:
        basePlane = rootComp.xZConstructionPlane
        axisName = 'Y'
    elif dotZ > 0.999:
        basePlane = rootComp.xYConstructionPlane
        axisName = 'Z'
    
    if not basePlane:
        msg = f'Direction must be aligned with X, Y, or Z axis.\n\nCurrent direction: ({direction.x:.3f}, {direction.y:.3f}, {direction.z:.3f})\n\nPlease select start/end points that are aligned with one of the coordinate axes.'
        ui.messageBox(msg)
        return
    
    futil.log(f'Using {axisName}-axis alignment')
    
    # Get the coordinate values along the axis from start and end points
    if axisName == 'X':
        start_coord = start_point.x
        end_coord = end_point.x
    elif axisName == 'Y':
        start_coord = start_point.y
        end_coord = end_point.y
    else:  # Z
        start_coord = start_point.z
        end_coord = end_point.z
    
    futil.log(f'Axis range: {start_coord} to {end_coord}')
    
    # Calculate interval along the axis
    axis_interval = (end_coord - start_coord) / divisions
    
    # Create planes in rootComponent (top level) for correct world coordinates
    planes = rootComp.constructionPlanes
    planes_created = []
    
    futil.log(f'Creating {divisions - 1} construction planes')
    
    # Create construction planes at intermediate positions
    for i in range(1, divisions):
        plane_position = start_coord + (axis_interval * i)
        
        try:
            planeInput = planes.createInput()
            offsetValue = adsk.core.ValueInput.createByReal(plane_position)
            planeInput.setByOffset(basePlane, offsetValue)
            plane = planes.add(planeInput)
            plane.name = f'Split Plane {i}'
            planes_created.append(plane)
            futil.log(f'Created plane {i} at position {plane_position} ({axisName}-axis)')
        except Exception as e:
            futil.log(f'Error creating plane {i}: {str(e)}')
    
    # Split the bodies with these planes
    futil.log(f'Starting to split {len(bodies)} bodies with {len(planes_created)} planes')
    
    # Get the parent component of the first body for split operations
    firstBody = bodies[0]
    parentComp = firstBody.parentComponent
    futil.log(f'Bodies are in component: {parentComp.name}')
    
    splitFeatures = parentComp.features.splitBodyFeatures
    total_splits = 0
    
    # Split each plane with all relevant bodies
    for planeIndex, plane in enumerate(planes_created):
        futil.log(f'Splitting with plane {planeIndex + 1}/{len(planes_created)}: {plane.name}')
        
        # Get current solid bodies in the parent component
        current_bodies = []
        for body in parentComp.bRepBodies:
            if body.isSolid:
                current_bodies.append(body)
        
        futil.log(f'  Found {len(current_bodies)} solid bodies')
        
        # Try to split each body with this plane
        for body in current_bodies:
            try:
                splitInput = splitFeatures.createInput(body, plane, True)
                splitFeature = splitFeatures.add(splitInput)
                
                if splitFeature:
                    total_splits += 1
                    futil.log(f'    ✓ Split body successfully')
                    
            except Exception as e:
                futil.log(f'    - Skipped (no intersection)')
    
    # Count final bodies
    final_body_count = 0
    for body in parentComp.bRepBodies:
        if body.isSolid:
            final_body_count += 1
    
    # Delete construction planes after split
    futil.log(f'Cleaning up {len(planes_created)} construction planes...')
    for plane in planes_created:
        try:
            plane.deleteMe()
        except:
            pass
    
    msg = f'✓ Successfully split bodies!\n\n• {divisions} divisions → {final_body_count} bodies\n• {total_splits} split operations completed\n\n(Construction planes cleaned up)'
    
    futil.log(msg)
    ui.messageBox(msg)


def command_preview(args: adsk.core.CommandEventArgs):
    pass


def command_input_changed(args: adsk.core.InputChangedEventArgs):
    pass


def command_validate_input(args: adsk.core.ValidateInputsEventArgs):
    inputs = args.inputs

    body_select: adsk.core.SelectionCommandInput = inputs.itemById('body_select')
    start_point: adsk.core.SelectionCommandInput = inputs.itemById('start_point')
    end_point: adsk.core.SelectionCommandInput = inputs.itemById('end_point')
    divisions: adsk.core.IntegerSpinnerCommandInput = inputs.itemById('divisions')

    # Validate all inputs are provided
    if (body_select.selectionCount >= 1 and
        start_point.selectionCount == 1 and
        end_point.selectionCount == 1 and
        divisions.value >= 1):
        args.areInputsValid = True
    else:
        args.areInputsValid = False


def command_destroy(args: adsk.core.CommandEventArgs):
    global local_handlers
    local_handlers = []
