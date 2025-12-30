"""
Tower Twister for Rhino 8 / Grasshopper CPython

Takes a single closed curve and creates twisted tower surfaces by copying,
rotating, and lofting between floors.
"""

from typing import Tuple, List
import Rhino.Geometry as rg


def twist_tower(
    base_curve: rg.Curve,
    floor_count: int,
    floor_height: float,
    rotation_per_floor: int,
    axis_point: rg.Point3d = None
) -> Tuple[List[rg.Surface], List[rg.Curve]]:
    """
    Create twisted tower surfaces from a single closed base curve.

    Args:
        base_curve: Closed curve (polyline, circle, rectangle, etc.)
        floor_count: Number of floors to generate
        floor_height: Vertical distance between floors (meters)
        rotation_per_floor: Rotation increment in degrees per floor (integer)
        axis_point: Center point for rotation (defaults to curve centroid)

    Returns:
        (surfaces, floor_curves)
    """

    if base_curve is None:
        raise ValueError("No base curve provided.")

    if not base_curve.IsClosed:
        raise ValueError(
            "Base curve must be closed. "
            "Use closed polylines, circles, rectangles, or polygons."
        )

    if floor_count < 2:
        raise ValueError("Floor count must be at least 2.")

    if floor_height <= 0:
        raise ValueError("Floor height must be > 0.")

    if axis_point is None:
        bbox = base_curve.GetBoundingBox(True)
        axis_point = bbox.Center

    floor_curves = []

    for i in range(floor_count):
        z_offset = i * floor_height
        rotation_degrees = i * rotation_per_floor

        transform = rg.Transform.Identity
        transform *= rg.Transform.Translation(0, 0, z_offset)

        if rotation_degrees != 0:
            angle_rad = rotation_degrees * (3.14159265359 / 180.0)
            axis_elevated = rg.Point3d(axis_point.X, axis_point.Y, z_offset)
            transform *= rg.Transform.Rotation(
                angle_rad,
                rg.Vector3d.ZAxis,
                axis_elevated
            )

        new_curve = base_curve.DuplicateCurve()
        new_curve.Transform(transform)
        floor_curves.append(new_curve)

    surfaces = []
    for i in range(floor_count - 1):
        loft_breps = rg.Brep.CreateFromLoft(
            [floor_curves[i], floor_curves[i + 1]],
            rg.Point3d.Unset,
            rg.Point3d.Unset,
            rg.LoftType.Normal,
            False
        )

        if not loft_breps or len(loft_breps) == 0:
            raise RuntimeError(f"Loft failed between floors {i+1} and {i+2}.")

        brep = loft_breps[0]
        for face in brep.Faces:
            surfaces.append(face.UnderlyingSurface())

    return surfaces, floor_curves
