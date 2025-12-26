"""
Toolkit initialisation entry point.

Purpose:
- Provide a stable startup hook for the toolkit
- Keep Grasshopper files free of toolkit logic

This function can be extended later with lightweight checks
(e.g. version checks, folder checks) without changing GH files.
"""


def initialise():
    """Initialise the toolkit."""
    return "Toolkit initialised"
