# power_fault_simulator

Lightweight power system fault simulator used for protection/distance/fault-location experiments.

Link :- https://numerical-relay-simulator-iam2icynugqfysyaovotfb.streamlit.app/

Quick start

1. Create and activate a virtual environment (recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Run the simulator UI or CLI:

```powershell
python app.py
# or
python main.py
```

Project layout highlights

- `faults/` - fault models
- `protection/` - detection, distance, fault location, measurements
- `system/` - electrical components (source, line, breaker, load, autoreclose)
- `ui/` - dashboard entrypoints
- `utils/` - shared constants

Repository conversion note

This repository has been initialized and prepared for pushing to GitHub. Use the GitHub CLI (`gh`) to create and push the remote repository, or add a remote manually.
