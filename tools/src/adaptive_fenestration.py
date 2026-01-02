"""
Adaptive fenestration (Rhino 8 / Grasshopper CPython).

- Accepts: Panels, IDs, Data values (any metric), Window shape
- Returns: (fenestrated_panels, fenestration_data)

Generic tool: Data values can be irradiance, temperature, view analysis, 
occupancy, wind pressure, or any other scalar metric.
"""

import Rhino.Geometry as rg


def normalize_data(data_values):
    """
    Normalize data to 0-1 range and bin into user-specified categories.

    Returns:
      normalized : list[float] (0.0 to 1.0)
      categories : list[int] (0 to num_categories-1)
    """
    min_val = min(data_values)
    max_val = max(data_values)

    if max_val == min_val:
        return [0.5] * len(data_values), [5] * len(data_values)

    normalized = []

    for val in data_values:
        # Normalize to 0-1
        norm = (val - min_val) / (max_val - min_val)
        normalized.append(norm)

    return normalized


def bin_into_categories(normalized_values, num_categories=11):
    """
    Bin normalized values into discrete categories.

    Returns:
      categories : list[int] (0 to num_categories-1)
    """
    categories = []
    for norm in normalized_values:
        category = min(int(norm * num_categories), num_categories - 1)
        categories.append(category)
    return categories


def calculate_opening_scale(normalized_value, min_scale=0.0, max_scale=0.5, invert=True):
    """
    Calculate opening scale based on normalized value (0-1).

    Args:
      normalized_value: 0.0 to 1.0
      min_scale: Minimum opening size (0.0 = solid panel)
      max_scale: Maximum opening size (0.5 = 50% of panel)
      invert: If True, high value = small opening. If False, high value = large opening.

    Returns scale factor (min_scale to max_scale)
    """
    if invert:
        # High data value = small opening (e.g., high irradiance = small window)
        return max_scale - (normalized_value * (max_scale - min_scale))
    else:
        # High data value = large opening (e.g., high view quality = large window)
        return min_scale + (normalized_value * (max_scale - min_scale))


def create_fenestrated_panel(panel, opening_shape, scale_factor, panel_id):
    """
    Create fenestration by scaling and positioning an opening shape at panel center.

    Returns:
      fenestrated_panel : rg.Brep or rg.Surface
      fenestration_info : dict with opening data
    """
    if scale_factor == 0:
        # Solid panel (no opening)
        panel_area = rg.AreaMassProperties.Compute(panel).Area
        return panel, {
            'id': panel_id,
            'opening_scale': 0.0,
            'opening_area': 0.0,
            'opening_percent': 0.0,
            'panel_area': panel_area
        }

    # Get panel center and frame
    u_mid = panel.Domain(0).Mid
    v_mid = panel.Domain(1).Mid
    center = panel.PointAt(u_mid, v_mid)

    success, frame = panel.FrameAt(u_mid, v_mid)
    if not success:
        raise RuntimeError(f"Failed to get frame for panel {panel_id}")

    # Transform opening shape to panel center with scaling
    transform = rg.Transform.PlaneToPlane(rg.Plane.WorldXY, frame)
    scale_transform = rg.Transform.Scale(
        rg.Plane.WorldXY, scale_factor, scale_factor, 1.0)

    opening_curve = opening_shape.Duplicate()
    opening_curve.Transform(scale_transform)
    opening_curve.Transform(transform)

    # Create Brep from panel
    panel_brep = panel.ToBrep() if isinstance(panel, rg.Surface) else panel

    # Extrude opening curve to create cutting volume
    extrusion_vector = frame.ZAxis * 1.0
    opening_surface = rg.Surface.CreateExtrusion(
        opening_curve, extrusion_vector)

    if opening_surface:
        opening_brep = opening_surface.ToBrep()
        # Boolean difference
        fenestrated = rg.Brep.CreateBooleanDifference(
            [panel_brep], [opening_brep], 0.01)

        if fenestrated and len(fenestrated) > 0:
            result_panel = fenestrated[0]
        else:
            # Boolean failed, return original panel
            result_panel = panel_brep
    else:
        result_panel = panel_brep

    # Calculate areas and percentages
    opening_area = rg.AreaMassProperties.Compute(
        opening_curve).Area if scale_factor > 0 else 0.0
    panel_area = rg.AreaMassProperties.Compute(panel).Area
    opening_percent = (opening_area / panel_area *
                       100) if panel_area > 0 else 0.0

    fenestration_info = {
        'id': panel_id,
        'opening_scale': scale_factor,
        'opening_area': opening_area,
        'opening_percent': opening_percent,
        'panel_area': panel_area
    }

    return result_panel, fenestration_info


def adaptive_fenestration(panels, ids, data_values, opening_shape,
                          min_opening=0.0, max_opening=0.5,
                          num_categories=11, invert=True):
    """
    Create adaptive fenestration based on data-driven logic.

    Args:
      panels: List of panel surfaces
      ids: List of panel identifiers
      data_values: List of scalar values (irradiance, temperature, view, etc.)
      opening_shape: Closed planar curve defining opening geometry
      min_opening: Minimum opening size (0.0 to 1.0)
      max_opening: Maximum opening size (0.0 to 1.0)
      num_categories: Number of discrete size categories
      invert: If True, high data = small opening. If False, high data = large opening.

    Returns:
      fenestrated_panels : list[rg.Brep]
      fenestration_data : list[dict]
      categories : list[int]
      scale_factors : list[float]
    """
    if len(panels) != len(data_values):
        raise ValueError("Number of panels must match number of data values")

    if len(panels) != len(ids):
        raise ValueError("Number of panels must match number of IDs")

    # Normalize data
    normalized = normalize_data(data_values)

    # Bin into categories
    categories = bin_into_categories(normalized, num_categories)

    # Calculate scale factors
    scale_factors = []
    for norm in normalized:
        scale = calculate_opening_scale(norm, min_opening, max_opening, invert)
        scale_factors.append(scale)

    # Create fenestrated panels
    fenestrated_panels = []
    fenestration_data = []

    for i, (panel, panel_id, scale) in enumerate(zip(panels, ids, scale_factors)):
        fenestrated, info = create_fenestrated_panel(
            panel, opening_shape, scale, panel_id)

        # Add category to info
        info['category'] = categories[i]
        info['data_value'] = data_values[i]
        info['normalized_value'] = normalized[i]

        fenestrated_panels.append(fenestrated)
        fenestration_data.append(info)

    return fenestrated_panels, fenestration_data, categories, scale_factors
