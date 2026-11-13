# HEY AI

HEY AI is a small Windows desktop application with a futuristic floating orb.
The initial version provides an always-on-top orb and an expandable status
panel. Voice recognition and AI integration are not included yet.

## Requirements

- Windows 10 or later
- Python 3.10 or later

## Run on Windows

From PowerShell in the project directory:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
python -m hey_ai
```

Click the orb to expand the panel. Drag the orb or panel to reposition it, and
select the minus button to collapse it back to the orb. The application stays
above other windows.

## Run tests

```powershell
python -m unittest discover -s tests -v
```
