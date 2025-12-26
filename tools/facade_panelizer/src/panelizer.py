"""
Facade panelisation logic.

This module contains geometry-agnostic logic.
Grasshopper UI and wiring should live in the .gh file.
"""


def generate_panel_ids(u_count: int, v_count: int, prefix: str = "P"):
    """
    Generate panel IDs in row-major order.

    Example:
    u_count = 2, v_count = 3 →

    P-01-01, P-02-01
    P-01-02, P-02-02
    P-01-03, P-02-03
    """

    if u_count <= 0 or v_count <= 0:
        raise ValueError("U and V counts must be greater than zero.")

    panel_ids = []

    for v in range(1, v_count + 1):
        for u in range(1, u_count + 1):
            panel_ids.append(f"{prefix}-{u:02d}-{v:02d}")

    return panel_ids
