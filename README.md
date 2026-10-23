# Home Building Estimation Prototype

## Run on Windows PowerShell

```powershell
cd path\to\estimation_prototype
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

If PowerShell blocks activation, run this in the current terminal and activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## What it calculates
- Room floor area
- Gross and net wall area
- Tile purchase area including wastage
- Plaster area (one or both sides)
- Approximate wall paint quantity
- Indicative tile, plaster and paint costs
- Room-wise CSV export

This is a learning prototype, not a complete construction estimator. It does not calculate structural design, foundation, steel, brickwork/mortar, electrical/plumbing, approvals, taxes, or verified full-house cost. Enter consistent dimensions in metres.
