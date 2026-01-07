import adsk.core
import adsk.fusion
import os
from ...lib import fusionAddInUtils as futil
from ... import config

app = adsk.core.Application.get()
ui = app.userInterface

# Command identity
CMD_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_contour'
CMD_NAME = 'Contour'
CMD_Description = 'Create contour curves or split bodies with parallel planes'

IS_PROMOTED = True

# UI location
WORKSPACE_ID = 'FusionSolidEnvironment'
PANEL_ID = 'SolidScriptsAddinsPanel'
COMMAND_BESIDE_ID = 'ScriptsManagerCommand'

ICON_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', '')

# Event handlers reference
local_handlers = []

# Mode constants
MODE_CONTOUR_CURVES = 'Contour Curves'
MODE_SPLIT_BODY = 'Split Body'


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

    # Mode selection (Contour Curves or Split Body)
    mode_input = inputs.addDropDownCommandInput('mode', 'Mode', adsk.core.DropDownStyles.TextListDropDownStyle)
    mode_input.listItems.add(MODE_CONTOUR_CURVES, True)  # Default
    mode_input.listItems.add(MODE_SPLIT_BODY, False)

    # Body selection (multiple)
    body_select = inputs.addSelectionInput('body_select', 'Bodies', 'Select bodies')
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
    inputs.addIntegerSpinnerCommandInput('divisions', 'Number of Divisions', 2, 100, 1, 5)

    # Delete original bodies option (for Contour Curves mode)
    delete_bodies = inputs.addBoolValueInput('delete_bodies', 'Delete Original Bodies', True, '', False)

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
    mode_input: adsk.core.DropDownCommandInput = inputs.itemById('mode')
    body_select: adsk.core.SelectionCommandInput = inputs.itemById('body_select')
    start_point_input: adsk.core.SelectionCommandInput = inputs.itemById('start_point')
    end_point_input: adsk.core.SelectionCommandInput = inputs.itemById('end_point')
    divisions_input: adsk.core.IntegerSpinnerCommandInput = inputs.itemById('divisions')
    delete_bodies_input: adsk.core.BoolValueCommandInput = inputs.itemById('delete_bodies')

    # Get mode
    mode = mode_input.selectedItem.name

    # Collect bodies
    bodies = []
    for i in range(body_select.selectionCount):
        bodies.append(body_select.selection(i).entity)

    # Get start and end points
    start_point = get_point_from_selection(start_point_input.selection(0).entity)
    end_point = get_point_from_selection(end_point_input.selection(0).entity)

    # Get number of divisions
    divisions = divisions_input.value

    # Get delete bodies option
    delete_bodies = delete_bodies_input.value

    # Execute based on mode
    try:
        futil.log(f'=== Starting {mode} ===')
        futil.log(f'Bodies: {len(bodies)}')
        futil.log(f'Start point: {start_point.asArray()}')
        futil.log(f'End point: {end_point.asArray()}')
        futil.log(f'Divisions: {divisions}')
        futil.log(f'Delete bodies: {delete_bodies}')
        
        if mode == MODE_CONTOUR_CURVES:
            create_contour_curves(bodies, start_point, end_point, divisions, delete_bodies)
        else:
            split_bodies_with_planes(bodies, start_point, end_point, divisions)
        
        futil.log(f'=== {mode} Completed ===')
    except Exception as e:
        error_msg = f'Error: {str(e)}'
        ui.messageBox(error_msg)
        futil.log(error_msg, adsk.core.LogLevels.ErrorLogLevel)
        futil.handle_error(f'{mode} Failed')


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


def get_axis_info(start_point: adsk.core.Point3D, end_point: adsk.core.Point3D):
    """Calculate axis alignment and return base plane info."""
    design = adsk.fusion.Design.cast(app.activeProduct)
    rootComp = design.rootComponent
    
    # Calculate direction vector
    direction = start_point.vectorTo(end_point)
    total_distance = direction.length
    direction.normalize()
    
    # Determine which axis we're aligned with
    xAxis = adsk.core.Vector3D.create(1, 0, 0)
    yAxis = adsk.core.Vector3D.create(0, 1, 0)
    zAxis = adsk.core.Vector3D.create(0, 0, 1)
    
    dotX = abs(direction.dotProduct(xAxis))
    dotY = abs(direction.dotProduct(yAxis))
    dotZ = abs(direction.dotProduct(zAxis))
    
    # Determine base plane
    basePlane = None
    axisName = None
    
    if dotX > 0.999:
        basePlane = rootComp.yZConstructionPlane
        axisName = 'X'
        start_coord = start_point.x
        end_coord = end_point.x
    elif dotY > 0.999:
        basePlane = rootComp.xZConstructionPlane
        axisName = 'Y'
        start_coord = start_point.y
        end_coord = end_point.y
    elif dotZ > 0.999:
        basePlane = rootComp.xYConstructionPlane
        axisName = 'Z'
        start_coord = start_point.z
        end_coord = end_point.z
    else:
        return None, None, None, None, None
    
    return basePlane, axisName, start_coord, end_coord, direction


def create_contour_curves(bodies, start_point: adsk.core.Point3D, end_point: adsk.core.Point3D, divisions: int, delete_bodies: bool):
    """Create contour curves - Step by step implementation."""
    design = adsk.fusion.Design.cast(app.activeProduct)
    rootComp = design.rootComponent
    activeComp = design.activeComponent
    
    futil.log(f'Active component: {activeComp.name}')
    
    # Get axis info (uses rootComp for base planes - world coordinates)
    basePlane, axisName, start_coord, end_coord, direction = get_axis_info(start_point, end_point)
    
    if not basePlane:
        msg = 'Direction must be aligned with X, Y, or Z axis.\n\nPlease select start/end points that are aligned with one of the coordinate axes.'
        ui.messageBox(msg)
        return
    
    futil.log(f'=== Step 1: Create Sketches ===')
    futil.log(f'Axis: {axisName}')
    futil.log(f'Range: {start_coord:.4f} to {end_coord:.4f}')
    futil.log(f'Divisions: {divisions} → {divisions + 1} sketches')
    
    # Calculate interval
    axis_interval = (end_coord - start_coord) / divisions
    futil.log(f'Interval: {axis_interval:.4f}')
    
    # Use rootComp for construction planes (world coordinates)
    # But create sketches in activeComp
    rootPlanes = rootComp.constructionPlanes
    sketches_created = []
    planes_created = []
    
    # Create sketch at each division point (including start and end)
    # 5 divisions = 6 sketches (positions 0, 1, 2, 3, 4, 5)
    for i in range(divisions + 1):
        plane_position = start_coord + (axis_interval * i)
        
        futil.log(f'Creating sketch {i + 1}/{divisions + 1} at {axisName}={plane_position:.4f}')
        
        try:
            # Step 1a: Create construction plane in rootComp (world coordinates)
            planeInput = rootPlanes.createInput()
            offsetValue = adsk.core.ValueInput.createByReal(plane_position)
            planeInput.setByOffset(basePlane, offsetValue)
            tempPlane = rootPlanes.add(planeInput)
            tempPlane.name = f'Contour Plane {i + 1}'
            planes_created.append(tempPlane)
            futil.log(f'  ✓ Created plane at world {axisName}={plane_position:.4f}')
            
            # Step 1b: Create sketch on this plane in activeComp
            sketch = activeComp.sketches.add(tempPlane)
            sketch.name = f'Contour {i + 1}'
            futil.log(f'  ✓ Created sketch: {sketch.name}')
            
            # Step 2: Add intersection curves to sketch
            curves_added = 0
            for body in bodies:
                try:
                    # projectCutEdges creates curves where the body intersects the sketch plane
                    result = sketch.projectCutEdges(body)
                    if result:
                        curves_added += result.count
                        futil.log(f'  ✓ projectCutEdges: {result.count} curves from body')
                except Exception as e:
                    futil.log(f'  ✗ projectCutEdges error: {str(e)}')
            
            if curves_added > 0:
                sketches_created.append(sketch)
                futil.log(f'  ✓ Total curves in sketch: {curves_added}')
            else:
                # No curves - delete empty sketch
                sketch.deleteMe()
                futil.log(f'  - No intersection, deleted empty sketch')
            
        except Exception as e:
            futil.log(f'  ✗ Error: {str(e)}')
    
    # Clean up construction planes (keep sketches)
    futil.log('Cleaning up construction planes...')
    for plane in planes_created:
        try:
            plane.deleteMe()
        except:
            pass
    
    # Delete original bodies if requested
    if delete_bodies and len(sketches_created) > 0:
        futil.log('Deleting original bodies...')
        for body in bodies:
            try:
                body.deleteMe()
            except:
                pass
    
    # Show result
    msg = f'✓ Contour curves created!\n\n'
    msg += f'• {divisions + 1} sections processed\n'
    msg += f'• {len(sketches_created)} sketches with curves\n'
    msg += f'• Construction planes cleaned up'
    if delete_bodies and len(sketches_created) > 0:
        msg += f'\n• Original bodies deleted'
    
    futil.log(msg)
    ui.messageBox(msg)


def copy_curve_to_output_sketch(sourceCurve, outputSketch: adsk.fusion.Sketch, sourceSketch: adsk.fusion.Sketch):
    """Copy a curve from source sketch to output sketch, preserving 3D position."""
    
    # Get the 3D geometry of the curve
    if isinstance(sourceCurve, adsk.fusion.SketchLine):
        # Get 3D points from the sketch line
        startPt3D = sourceSketch.sketchToModelSpace(sourceCurve.startSketchPoint.geometry)
        endPt3D = sourceSketch.sketchToModelSpace(sourceCurve.endSketchPoint.geometry)
        
        # Convert to output sketch space
        startPt = outputSketch.modelToSketchSpace(startPt3D)
        endPt = outputSketch.modelToSketchSpace(endPt3D)
        
        outputSketch.sketchCurves.sketchLines.addByTwoPoints(startPt, endPt)
        
    elif isinstance(sourceCurve, adsk.fusion.SketchArc):
        # Get 3D points from the arc
        startPt3D = sourceSketch.sketchToModelSpace(sourceCurve.startSketchPoint.geometry)
        endPt3D = sourceSketch.sketchToModelSpace(sourceCurve.endSketchPoint.geometry)
        
        # Get midpoint of arc in 3D
        evaluator = sourceCurve.geometry.evaluator
        _, midParam = evaluator.getParameterAtLength(0, sourceCurve.length / 2)
        _, midPt3D = evaluator.getPointAtParameter(midParam)
        
        # Convert to output sketch space
        startPt = outputSketch.modelToSketchSpace(startPt3D)
        midPt = outputSketch.modelToSketchSpace(midPt3D)
        endPt = outputSketch.modelToSketchSpace(endPt3D)
        
        outputSketch.sketchCurves.sketchArcs.addByThreePoints(startPt, midPt, endPt)
        
    elif isinstance(sourceCurve, adsk.fusion.SketchCircle):
        # Get center in 3D
        centerPt3D = sourceSketch.sketchToModelSpace(sourceCurve.centerSketchPoint.geometry)
        centerPt = outputSketch.modelToSketchSpace(centerPt3D)
        
        outputSketch.sketchCurves.sketchCircles.addByCenterRadius(centerPt, sourceCurve.radius)
        
    elif isinstance(sourceCurve, adsk.fusion.SketchEllipse):
        # Get center in 3D
        centerPt3D = sourceSketch.sketchToModelSpace(sourceCurve.centerSketchPoint.geometry)
        centerPt = outputSketch.modelToSketchSpace(centerPt3D)
        
        # Get major axis endpoint for direction
        majorAxisPt3D = adsk.core.Point3D.create(
            centerPt3D.x + sourceCurve.majorAxis.x * sourceCurve.majorRadius,
            centerPt3D.y + sourceCurve.majorAxis.y * sourceCurve.majorRadius,
            centerPt3D.z + sourceCurve.majorAxis.z * sourceCurve.majorRadius
        )
        majorAxisPt = outputSketch.modelToSketchSpace(majorAxisPt3D)
        
        outputSketch.sketchCurves.sketchEllipses.add(centerPt, majorAxisPt, sourceCurve.minorRadius)
        
    elif isinstance(sourceCurve, adsk.fusion.SketchFittedSpline):
        # Sample points along the spline and create fitted spline
        points = adsk.core.ObjectCollection.create()
        
        # Get fit points in 3D and convert
        for fitPoint in sourceCurve.fitPoints:
            pt3D = sourceSketch.sketchToModelSpace(fitPoint.geometry)
            pt = outputSketch.modelToSketchSpace(pt3D)
            points.add(pt)
        
        if points.count >= 2:
            outputSketch.sketchCurves.sketchFittedSplines.add(points)
            
    else:
        # For other curve types, sample points and create fitted spline
        try:
            geom = sourceCurve.geometry
            evaluator = geom.evaluator
            _, startParam, endParam = evaluator.getParameterExtents()
            
            # Sample points along the curve
            points = adsk.core.ObjectCollection.create()
            numSamples = 30
            
            for k in range(numSamples + 1):
                param = startParam + (endParam - startParam) * k / numSamples
                _, pt3D = evaluator.getPointAtParameter(param)
                pt3D_world = sourceSketch.sketchToModelSpace(pt3D)
                pt = outputSketch.modelToSketchSpace(pt3D_world)
                points.add(pt)
            
            if points.count >= 2:
                outputSketch.sketchCurves.sketchFittedSplines.add(points)
                
        except Exception as e:
            futil.log(f'    Could not copy curve type {type(sourceCurve)}: {str(e)}')


def split_bodies_with_planes(bodies, start_point: adsk.core.Point3D, end_point: adsk.core.Point3D, divisions: int):
    """Split bodies with parallel construction planes between start and end points."""
    design = adsk.fusion.Design.cast(app.activeProduct)
    rootComp = design.rootComponent
    
    # Get axis info
    basePlane, axisName, start_coord, end_coord, direction = get_axis_info(start_point, end_point)
    
    if not basePlane:
        msg = 'Direction must be aligned with X, Y, or Z axis.\n\nPlease select start/end points that are aligned with one of the coordinate axes.'
        ui.messageBox(msg)
        return
    
    futil.log(f'Using {axisName}-axis alignment')
    futil.log(f'Axis range: {start_coord} to {end_coord}')
    
    # Calculate interval
    axis_interval = (end_coord - start_coord) / divisions
    
    # Create planes in rootComponent
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
    changed_input = args.input
    inputs = args.inputs
    
    # Update UI based on mode selection
    if changed_input.id == 'mode':
        mode_input: adsk.core.DropDownCommandInput = inputs.itemById('mode')
        delete_bodies_input: adsk.core.BoolValueCommandInput = inputs.itemById('delete_bodies')
        
        # Show/hide delete bodies option based on mode
        if mode_input.selectedItem.name == MODE_CONTOUR_CURVES:
            delete_bodies_input.isVisible = True
        else:
            delete_bodies_input.isVisible = False


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
        divisions.value >= 2):
        args.areInputsValid = True
    else:
        args.areInputsValid = False


def command_destroy(args: adsk.core.CommandEventArgs):
    global local_handlers
    local_handlers = []
