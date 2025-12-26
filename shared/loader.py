import os
import sys
import traceback


def ensure_repo_on_syspath() -> str:
    """
    Ensures the repo root is on sys.path using GH_PARAMETRIC_TOOLKIT.
    Returns the repo path.
    """
    repo = os.getenv("GH_PARAMETRIC_TOOLKIT")
    if not repo:
        raise Exception(
            "Toolkit path not set.\n\n"
            "In Terminal, run:\n"
            '  export GH_PARAMETRIC_TOOLKIT="/path/to/gh-parametric-toolkit"\n'
            '  open -a "Rhino 8"\n\n'
            "Keep Terminal open while Rhino is running."
        )

    if repo not in sys.path:
        sys.path.insert(0, repo)

    return repo


def run_tool(fn):
    """
    Standard runner for GH tools.
    Returns:
      (result, []) on success
      (None, [traceback]) on failure
    """
    try:
        return fn(), []
    except Exception:
        return None, [traceback.format_exc()]
