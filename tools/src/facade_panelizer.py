"""
Minimal facade panelizer (Rhino 8 / Grasshopper CPython).

- Accepts: Surface / BrepFace / Brep (single face used)
- Returns: (panels, ids)
"""

import Rhino.Geometry as rg


def generate_panel_ids(u_count: int, v_count: int, prefix: str = "P"):
    if u_count <= 0 or v_count <= 0:
        raise ValueError("U and V counts must be > 0.")

    ids = []
    for v in range(1, v_count + 1):
        for u in range(1, u_count + 1):
            ids.append(f"{prefix}-{u:02d}-{v:02d}")
    return ids


def panelize_surface(surface_input, u_count: int, v_count: int, prefix: str = "P"):
    """
    Panelize a surface into a u_count x v_count grid by sampling UV corners.

    Returns:
      panels : list[rg.Surface]
      ids    : list[str]
    """
    if surface_input is None:
        raise ValueError(
            "Surface input is None. Connect a Surface (or single-face Brep).")

    if u_count <= 0 or v_count <= 0:
        raise ValueError("U and V counts must be > 0.")

    # Coerce to a Surface (GH users may plug in Breps/faces)
    if isinstance(surface_input, rg.Surface):
        srf = surface_input
    elif isinstance(surface_input, rg.BrepFace):
        srf = surface_input.UnderlyingSurface()
    elif isinstance(surface_input, rg.Brep):
        if surface_input.Faces.Count == 0:
            raise ValueError("Brep has no faces.")
        srf = surface_input.Faces[0].UnderlyingSurface()
    else:
        raise TypeError(
            f"Unsupported type for surface_input: {type(surface_input)}")

    # Get the valid U and V ranges of the surface
    u_dom = srf.Domain(0)   # U direction domain
    v_dom = srf.Domain(1)   # V direction domain

    # Compute evenly spaced parameter values across the domains
    u_params = [
        u_dom.ParameterAt(i / float(u_count))
        for i in range(u_count + 1)
    ]
    v_params = [
        v_dom.ParameterAt(j / float(v_count))
        for j in range(v_count + 1)
    ]

    panels = []
    ids = generate_panel_ids(u_count, v_count, prefix)

    # Build one panel surface per UV cell (row-major order)
    for j in range(v_count):        # V cells (rows)
        for i in range(u_count):    # U cells (columns)
            u0, u1 = u_params[i], u_params[i + 1]
            v0, v1 = v_params[j], v_params[j + 1]

            # Corner points on the original surface
            p00 = srf.PointAt(u0, v0)
            p10 = srf.PointAt(u1, v0)
            p11 = srf.PointAt(u1, v1)
            p01 = srf.PointAt(u0, v1)

            # Create a 4-corner NURBS patch for this panel
            patch = rg.NurbsSurface.CreateFromCorners(p00, p10, p11, p01)
            if patch is None:
                raise RuntimeError(
                    f"Failed to create panel at (u={i+1}, v={j+1}).")

            panels.append(patch)

    return panels, ids
