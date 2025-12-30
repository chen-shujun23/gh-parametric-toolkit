import traceback
from typing import Callable, Tuple, List, Any


def run_tool(fn: Callable[[], Any], debug: bool = False) -> Tuple[Any, List[str]]:
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
