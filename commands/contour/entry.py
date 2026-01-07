import adsk.core
import adsk.fusion
import os
import math
from ...lib import fusionAddInUtils as futil
from ... import config

app = adsk.core.Application.get()
ui = app.userInterface

# Command identity
CMD_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_contour'
CMD_NAME = 'Split with Planes'
CMD_Description = 'Create parallel construction planes and split bodies'

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
        futil.handle_error('Failed to start Contour command')


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
        futil.handle_error('Failed to stop Contour command')


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
        # BRepVertex or SketchPoint
        geom = entity.geometry
        if isinstance(geom, adsk.core.Point3D):
            return geom.copy()
    if hasattr(entity, 'worldGeometry'):
        # ConstructionPoint
        return entity.worldGeometry.copy()
    if isinstance(entity, adsk.fusion.BRepVertex):
        return entity.geometry.copy()
    if isinstance(entity, adsk.fusion.SketchPoint):
        return entity.geometry.copy()

    raise ValueError(f'Cannot extract point from {type(entity)}')


def get_direction_from_selection(entity) -> adsk.core.Vector3D:
    """Extract direction Vector3D from edge, face, or construction axis."""
    if isinstance(entity, adsk.fusion.BRepEdge):
        # Get edge geometry (linear edges only)
        geom = entity.geometry
        if isinstance(geom, adsk.core.Line3D):
            direction = geom.startPoint.vectorTo(geom.endPoint)
            direction.normalize()
            return direction
        elif isinstance(geom, adsk.core.InfiniteLine3D):
            return geom.direction.copy()
    elif isinstance(entity, adsk.fusion.BRepFace):
        # Get face normal at pointOnFace
        evaluator = entity.evaluator
        _, normal = evaluator.getNormalAtPoint(entity.pointOnFace)
        return normal
    elif isinstance(entity, adsk.fusion.ConstructionAxis):
        # Get construction axis direction (Origin X/Y/Z axes)
        line = entity.geometry
        return line.direction.copy()
    elif isinstance(entity, adsk.fusion.SketchLine):
        # Sketch line (including construction lines)
        geom = entity.geometry
        direction = geom.startPoint.vectorTo(geom.endPoint)
        direction.normalize()
        return direction

    raise ValueError(f'Cannot extract direction from {type(entity)}')


def calculate_extent_along_direction(bodies, base_point: adsk.core.Point3D, direction: adsk.core.Vector3D):
    """Calculate min/max extent of bodies along direction from base point."""
    min_dist = float('inf')
    max_dist = float('-inf')

    for body in bodies:
        bbox = body.boundingBox
        # Check all 8 corners of bounding box
        corners = [
            adsk.core.Point3D.create(bbox.minPoint.x, bbox.minPoint.y, bbox.minPoint.z),
            adsk.core.Point3D.create(bbox.maxPoint.x, bbox.minPoint.y, bbox.minPoint.z),
            adsk.core.Point3D.create(bbox.minPoint.x, bbox.maxPoint.y, bbox.minPoint.z),
            adsk.core.Point3D.create(bbox.maxPoint.x, bbox.maxPoint.y, bbox.minPoint.z),
            adsk.core.Point3D.create(bbox.minPoint.x, bbox.minPoint.y, bbox.maxPoint.z),
            adsk.core.Point3D.create(bbox.maxPoint.x, bbox.minPoint.y, bbox.maxPoint.z),
            adsk.core.Point3D.create(bbox.minPoint.x, bbox.maxPoint.y, bbox.maxPoint.z),
            adsk.core.Point3D.create(bbox.maxPoint.x, bbox.maxPoint.y, bbox.maxPoint.z),
        ]

        for corner in corners:
            vec = base_point.vectorTo(corner)
            dist = vec.dotProduct(direction)
            min_dist = min(min_dist, dist)
            max_dist = max(max_dist, dist)

    return min_dist, max_dist


def split_bodies_with_planes(bodies, start_point: adsk.core.Point3D, end_point: adsk.core.Point3D, divisions: int):
    """Split bodies with parallel construction planes between start and end points."""
    design = adsk.fusion.Design.cast(app.activeProduct)
    # Use active component instead of root component
    activeComp = design.activeComponent
    
    futil.log(f'Using active component: {activeComp.name}')
    
    # Calculate direction vector
    direction = start_point.vectorTo(end_point)
    total_distance = direction.length
    direction.normalize()
    
    futil.log(f'Direction: {direction.asArray()}, Total distance: {total_distance} cm')
    
    # Calculate interval
    interval = total_distance / divisions
    
    futil.log(f'Creating {divisions} construction planes at {interval} cm intervals')
    
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
        basePlane = activeComp.yZConstructionPlane
        axisName = 'X'
    elif dotY > 0.999:
        basePlane = activeComp.xZConstructionPlane
        axisName = 'Y'
    elif dotZ > 0.999:
        basePlane = activeComp.xYConstructionPlane
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
    
    planes = activeComp.constructionPlanes
    planes_created = []
    
    # Create construction planes at intermediate positions
    for i in range(1, divisions):  # divisions-1 planes (we don't need planes at start/end)
        # Calculate position along the axis
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
    
    # Now split the bodies with these planes
    futil.log(f'Starting to split {len(bodies)} bodies with {len(planes_created)} planes')
    
    splitFeatures = activeComp.features.splitBodyFeatures
    total_splits = 0
    failed_splits = 0
    
    # Split each plane with all relevant bodies
    # We split one plane at a time across all bodies
    for planeIndex, plane in enumerate(planes_created):
        futil.log(f'Splitting with plane {planeIndex + 1}/{len(planes_created)}: {plane.name}')
        
        # Get all solid bodies in the active component
        all_bodies = []
        for body in activeComp.bRepBodies:
            if body.isSolid:
                all_bodies.append(body)
        
        futil.log(f'  Found {len(all_bodies)} solid bodies in component')
        
        # Try to split each body with this plane
        for body in all_bodies:
            try:
                # Create split body input
                splitInput = splitFeatures.createInput(body, plane, True)  # True = keep both sides
                
                # Execute split
                splitFeature = splitFeatures.add(splitInput)
                
                if splitFeature:
                    total_splits += 1
                    futil.log(f'    ✓ Split body successfully')
                else:
                    futil.log(f'    - Split returned None (body may not intersect plane)')
                    failed_splits += 1
                    
            except Exception as e:
                futil.log(f'    ✗ Error: {str(e)}')
                failed_splits += 1
    
    final_body_count = 0
    for body in activeComp.bRepBodies:
        if body.isSolid:
            final_body_count += 1
    
    msg = f'✓ Created {len(planes_created)} construction planes in "{activeComp.name}"!\n✓ Successful splits: {total_splits}\n✓ Final body count: {final_body_count}'
    if failed_splits > 0:
        msg += f'\n⚠ Failed/skipped splits: {failed_splits}'
    
    futil.log(msg)
    ui.messageBox(msg)


def generate_contours_old(bodies, base_point: adsk.core.Point3D, direction: adsk.core.Vector3D, distance: float):
    """Generate contour curves by intersecting bodies with parallel planes using temporary sketches."""
    design = adsk.fusion.Design.cast(app.activeProduct)
    rootComp = design.rootComponent

    # Calculate extent
    min_dist, max_dist = calculate_extent_along_direction(bodies, base_point, direction)

    if min_dist >= max_dist:
        ui.messageBox('Could not determine body extent along direction.')
        return

    # Snap min_dist to nearest multiple of distance below or at 0
    start_offset = math.floor(min_dist / distance) * distance
    end_offset = max_dist

    # Number of planes
    num_planes = int(math.ceil((end_offset - start_offset) / distance)) + 1

    futil.log(f'Contour: min={min_dist}, max={max_dist}, start={start_offset}, num_planes={num_planes}')

    # Normalize direction vector
    direction.normalize()

    # Create output sketch on XY plane
    xyPlane = rootComp.xYConstructionPlane
    outputSketch = rootComp.sketches.add(xyPlane)
    outputSketch.name = 'Contours'

    curves_created = 0

    # Determine which axis the direction is aligned with
    xAxis = adsk.core.Vector3D.create(1, 0, 0)
    yAxis = adsk.core.Vector3D.create(0, 1, 0)
    zAxis = adsk.core.Vector3D.create(0, 0, 1)
    
    # Check alignment with each axis (allowing for negative direction)
    dotX = abs(direction.dotProduct(xAxis))
    dotY = abs(direction.dotProduct(yAxis))
    dotZ = abs(direction.dotProduct(zAxis))
    
    # Determine which plane to use for offset
    basePlane = None
    axisName = None
    
    if dotX > 0.999:
        # X-axis aligned - use YZ plane
        basePlane = rootComp.yZConstructionPlane
        axisName = 'X'
    elif dotY > 0.999:
        # Y-axis aligned - use XZ plane  
        basePlane = rootComp.xZConstructionPlane
        axisName = 'Y'
    elif dotZ > 0.999:
        # Z-axis aligned - use XY plane
        basePlane = rootComp.xYConstructionPlane
        axisName = 'Z'
    
    if basePlane:
        futil.log(f'Using {axisName}-axis aligned method')
        
        for i in range(num_planes):
            offset = start_offset + i * distance
            
            try:
                # Create construction plane at offset
                planes = rootComp.constructionPlanes
                planeInput = planes.createInput()
                offsetValue = adsk.core.ValueInput.createByReal(offset)
                planeInput.setByOffset(basePlane, offsetValue)
                tempPlane = planes.add(planeInput)
                
                # Create temporary sketch on this plane
                tempSketch = rootComp.sketches.add(tempPlane)
                
                # Intersect with bodies
                bodyCollection = adsk.core.ObjectCollection.create()
                for body in bodies:
                    bodyCollection.add(body)
                
                intersectionCurves = tempSketch.intersectWithSketchPlane(bodyCollection)
                
                if intersectionCurves and intersectionCurves.count > 0:
                    futil.log(f'  Offset {offset}: found {intersectionCurves.count} curves')
                    
                    # Copy curves to output sketch
                    for j in range(intersectionCurves.count):
                        curve = intersectionCurves.item(j)
                        copy_sketch_curve_to_sketch(curve, outputSketch, offset, direction)
                        curves_created += 1
                
                # Clean up
                tempSketch.deleteMe()
                tempPlane.deleteMe()
                
            except Exception as e:
                futil.log(f'  Error at offset {offset}: {str(e)}')
    
    else:
        # Complex case: arbitrary direction - not aligned with any axis
        futil.log(f'Direction not aligned with any axis (X:{dotX:.3f}, Y:{dotY:.3f}, Z:{dotZ:.3f})')
        msg = 'Currently, only X/Y/Z-axis aligned contours are supported.\n\nPlease select:\n- X-axis, Y-axis, or Z-axis from the Origin\n- Or a straight edge aligned with one of these axes'
        ui.messageBox(msg)
        return

    if curves_created > 0:
        msg = f'✓ Successfully created {curves_created} contour curves!'
        futil.log(msg)
        ui.messageBox(msg)
    else:
        msg = 'No intersections found. Check body positions relative to contour planes.'
        futil.log(msg)
        ui.messageBox(msg)


def copy_sketch_curve_to_sketch(sourceCurve, targetSketch: adsk.fusion.Sketch, offset: float, direction: adsk.core.Vector3D):
    """Copy a sketch curve from one sketch to another, projecting to target sketch plane."""
    curves = targetSketch.sketchCurves
    
    try:
        # Get the 3D geometry of the source curve
        geom = sourceCurve.geometry
        
        if isinstance(sourceCurve, adsk.fusion.SketchLine):
            # Line
            start = targetSketch.modelToSketchSpace(sourceCurve.startSketchPoint.geometry)
            end = targetSketch.modelToSketchSpace(sourceCurve.endSketchPoint.geometry)
            curves.sketchLines.addByTwoPoints(start, end)
            
        elif isinstance(sourceCurve, adsk.fusion.SketchArc):
            # Arc - use three points
            start = targetSketch.modelToSketchSpace(sourceCurve.startSketchPoint.geometry)
            end = targetSketch.modelToSketchSpace(sourceCurve.endSketchPoint.geometry)
            # Get midpoint of arc
            _, midPoint3D = sourceCurve.geometry.evaluator.getPointAtParameter(0.5)
            mid = targetSketch.modelToSketchSpace(midPoint3D)
            curves.sketchArcs.addByThreePoints(start, mid, end)
            
        elif isinstance(sourceCurve, adsk.fusion.SketchCircle):
            # Circle
            center = targetSketch.modelToSketchSpace(sourceCurve.centerSketchPoint.geometry)
            curves.sketchCircles.addByCenterRadius(center, sourceCurve.radius)
            
        elif isinstance(sourceCurve, adsk.fusion.SketchEllipse):
            # Ellipse
            center = targetSketch.modelToSketchSpace(sourceCurve.centerSketchPoint.geometry)
            majorAxis = sourceCurve.majorAxis
            curves.sketchEllipses.add(center, majorAxis, sourceCurve.majorRadius, sourceCurve.minorRadius)
            
        elif isinstance(sourceCurve, adsk.fusion.SketchFittedSpline):
            # Fitted spline - get fit points
            fitPoints = adsk.core.ObjectCollection.create()
            for point in sourceCurve.fitPoints:
                fitPoints.add(targetSketch.modelToSketchSpace(point.geometry))
            curves.sketchFittedSplines.add(fitPoints)
            
        elif isinstance(sourceCurve, adsk.fusion.SketchFixedSpline):
            # Fixed spline - use the NURBS geometry
            nurbs = sourceCurve.geometry
            curves.sketchFixedSplines.add(nurbs)
            
        else:
            # For other curve types, try to get geometry and add as fixed spline
            if hasattr(geom, 'asNurbsCurve'):
                nurbs = geom.asNurbsCurve()
                curves.sketchFixedSplines.add(nurbs)
            else:
                futil.log(f'Unsupported sketch curve type: {type(sourceCurve)}')
                
    except Exception as e:
        futil.log(f'Error copying curve to sketch: {type(sourceCurve)} - {str(e)}')


def command_preview(args: adsk.core.CommandEventArgs):
    futil.log(f'{CMD_NAME} Command Preview Event')


def command_input_changed(args: adsk.core.InputChangedEventArgs):
    changed_input = args.input
    futil.log(f'{CMD_NAME} Input Changed Event fired from a change to {changed_input.id}')


def command_validate_input(args: adsk.core.ValidateInputsEventArgs):
    futil.log(f'{CMD_NAME} Validate Input Event')

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
    futil.log(f'{CMD_NAME} Command Destroy Event')
    global local_handlers
    local_handlers = []
