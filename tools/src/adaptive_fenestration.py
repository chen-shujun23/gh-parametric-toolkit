"""
Adaptive fenestration (Rhino 8 / Grasshopper CPython).

- Accepts: Panels (surfaces), IDs, Data values, Window shape
- Returns: (fenestrated_panels, fenestration_data)

Uses surface trimming instead of boolean operations.
"""

import Rhino.Geometry as rg


def normalize_data(data_values):
    """Normalize data to 0-1 range."""
    min_val = min(data_values)
    max_val = max(data_values)

    if max_val == min_val:
        return [0.5] * len(data_values)

    normalized = []
    for val in data_values:
        norm = (val - min_val) / (max_val - min_val)
        normalized.append(norm)

    return normalized


def bin_into_categories(normalized_values, num_categories=11):
    """Bin normalized values into discrete categories."""
    categories = []
    for norm in normalized_values:
        category = min(int(norm * num_categories), num_categories - 1)
        categories.append(category)
    return categories


def calculate_opening_scale(normalized_value, min_scale=0.0, max_scale=0.5, invert=True):
    """Calculate opening scale based on normalized value (0-1)."""
    if invert:
        return max_scale - (normalized_value * (max_scale - min_scale))
    else:
        return min_scale + (normalized_value * (max_scale - min_scale))


def create_fenestrated_panel(panel, opening_shape, scale_factor, panel_id):
    """
    Create fenestration by trimming surface with opening curve.

    Returns:
      fenestrated_panel : rg.Brep
      fenestration_info : dict with opening data
    """
    if scale_factor == 0:
        return panel, {
            'id': panel_id,
            'opening_area': 0.0,
            'opening_percent': 0.0
        }

    # Get panel center and frame
    u_mid = panel.Domain(0).Mid
    v_mid = panel.Domain(1).Mid

    success, frame = panel.FrameAt(u_mid, v_mid)
    if not success:
        raise RuntimeError(f"Failed to get frame for panel {panel_id}")

    # Transform opening shape to panel center with scaling
    scale_transform = rg.Transform.Scale(
        rg.Plane.WorldXY, scale_factor, scale_factor, 1.0)
    transform = rg.Transform.PlaneToPlane(rg.Plane.WorldXY, frame)

    opening_curve = opening_shape.Duplicate()
    opening_curve.Transform(scale_transform)
    opening_curve.Transform(transform)

    # Convert panel to Brep
    panel_brep = panel.ToBrep() if isinstance(panel, rg.Surface) else panel

    # Project curve onto the first face of the brep
    face = panel_brep.Faces[0]
    projected_curves = rg.Curve.ProjectToBrep(
        opening_curve, panel_brep, frame.ZAxis, 0.01)

    if projected_curves and len(projected_curves) > 0:
        # Use the face's Split method with the projected curve
        split_brep = face.Split([projected_curves[0]], 0.01)

        if split_brep and split_brep.Faces.Count > 1:
            # Multiple faces means successful split - keep largest
            faces = [split_brep.Faces[i]
                     for i in range(split_brep.Faces.Count)]
            largest_face = max(
                faces, key=lambda f: rg.AreaMassProperties.Compute(f).Area)
            result_panel = largest_face.DuplicateFace(False)
        else:
            result_panel = panel_brep
    else:
        result_panel = panel_brep

    # Calculate areas and percentages
    opening_area = rg.AreaMassProperties.Compute(opening_curve).Area
    panel_area = rg.AreaMassProperties.Compute(panel).Area
    opening_percent = (opening_area / panel_area *
                       100) if panel_area > 0 else 0.0

    fenestration_info = {
        'id': panel_id,
        'opening_area': opening_area,
        'opening_percent': opening_percent
    }

    return result_panel, fenestration_info


def adaptive_fenestration(panels, ids, data_values, opening_shape,
                          min_opening=0.0, max_opening=0.5,
                          num_categories=11, invert=True):
    """
    Create adaptive fenestration based on data-driven logic.
    """
    if len(panels) != len(data_values) or len(panels) != len(ids):
        raise ValueError(
            "Panels, IDs, and DataValues must have matching lengths")

    normalized = normalize_data(data_values)
    categories = bin_into_categories(normalized, num_categories)

    scale_factors = [calculate_opening_scale(norm, min_opening, max_opening, invert)
                     for norm in normalized]

    fenestrated_panels = []
    fenestration_data = []

    for i, (panel, panel_id, scale) in enumerate(zip(panels, ids, scale_factors)):
        fenestrated, info = create_fenestrated_panel(
            panel, opening_shape, scale, panel_id)

        info['category'] = categories[i]
        info['data_value'] = data_values[i]
        info['normalized_value'] = normalized[i]

        fenestrated_panels.append(fenestrated)
        fenestration_data.append(info)

    return fenestrated_panels, fenestration_data
