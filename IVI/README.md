# IVI static tournament dataset solution

Goal:
Use StatsBomb only once to build a local dataset with tournament competitions that have group stage and final phase.
The dashboard then reads only the local file.

## Copy files

- `build_static_tournament_data.py` -> `IVI/build_static_tournament_data.py`
- `static_tournament_store.py` -> `IVI/src/static_tournament_store.py`
- `app.py` -> `IVI/app.py`

## Build dataset once

```powershell
cd C:\Users\tezca\Football\IVI
python build_static_tournament_data.py
```

This creates:

```text
IVI\data\processed\statsbomb_tournament_goal_buildups.pkl
```

## Start dashboard

```powershell
python app.py
```

The dashboard does not call StatsBomb during normal use anymore.
