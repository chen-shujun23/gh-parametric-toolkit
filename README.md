# gh-parametric-toolkit

Studio-ready computational design tools built for **Rhino 8** using **Grasshopper** and **CPython (Python 3)**.  
This repository focuses on **modular, readable, and extensible code** that supports early-stage design exploration, rationalization, and sustainability-informed workflows in the AEC industry.

Grasshopper definitions act as **thin UI layers**, while core logic lives in reusable Python modules to support maintainability, testing, and team adoption.

---

## Compatibility

- Rhino 8
- Grasshopper
- CPython (Python 3)
- macOS / Windows

---

## Local Setup

This toolkit requires an **environment variable** pointing to the local path of the
`gh-parametric-toolkit` repository so that Grasshopper CPython components can import
the project modules.

### macOS

1. Open **Terminal**
2. Set the environment variable:

   export GH_PARAMETRIC_TOOLKIT="Users/YOURNAME/Documents/YOURFOLDER/gh-parametric-toolkit"

3. Launch Rhino from same Terminal window:

   open -a "Rhino 8"
