import os
import sys
import traceback


def run_tool(fn):
    """
    Standard runner for GH tools.

    Returns:
      (result, []) on success
      (None, [formatted error strings]) on failure
    """
    try:
        return fn(), []

    except Exception:
        return None, [
            "TOOL: An error occurred while running the tool.",
            traceback.format_exc()
        ]
