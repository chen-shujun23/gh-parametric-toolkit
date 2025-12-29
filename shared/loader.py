import traceback


def run_tool(fn, debug=False):
    """
    Standard runner for GH tools.

    Returns:
      (result, []) on success
      (None, [formatted error strings]) on failure
    """
    try:
        return fn(), []

    except Exception as e:
        msg = f"TOOL ERROR: {e}\n\n"

        if debug:
            return None, [msg, traceback.format_exc()]
        else:
            return None, [msg]
