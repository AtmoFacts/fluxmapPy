# fluxmappy

Quality filtering and polygon analysis for spatial flux rasters (FluxMaps).

`fluxmappy` reads FluxMap GeoTIFFs together with their companion quality-flag
rasters, masks out cells that fail a quality threshold, and aggregates the
result over polygon boundaries into statistics and diurnal cycles.

---

## Requirements

- **Python 3.10–3.13** (the package declares `requires-python = ">=3.10,<3.14"`)
- **GDAL-backed geospatial libraries** — `rasterio` and `fiona`. These are the
  only awkward part of the install: they need a matching GDAL build. Installing
  them through **conda-forge is strongly recommended**; `pip` works on most
  platforms via prebuilt wheels but can fail to find a compatible GDAL.
- `numpy`, `tzdata` (installed automatically)
---

# Disclaimer 

fluxmapPy is in an early (0.6.0) phase in which behavior may still change between releases. Names and arguments are subject to change until they lock at the 1.0.0 version. Name changes from 0.6.0 to 1.0.0 could cause warnings to appear when using the package.


# Installation

No clone required. Quote the whole argument — the `#` and `@` confuse some
shells if unquoted.

```bash
python -m pip install "fluxmappy @ git+https://github.com/AtmoFacts/fluxmapPy"
```

Or Into a fresh virtual environment (recommended over installing system-wide):

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install "fluxmappy @ git+https://github.com/AtmoFacts/fluxmapPy"
```
---

## Verifying the installation

```bash
python -c "import importlib.metadata as m; print('fluxmappy', m.version('fluxmappy'))"
python -c "import fluxmappy; print(len(fluxmappy.__all__), 'public names')"
python -c "import rasterio, fiona; print('rasterio', rasterio.__version__, '| fiona', fiona.__version__)"
```

Expected output resembles:

```
fluxmappy 0.6.0
18 public names
rasterio 1.3.9 | fiona 1.9.6
```

---

## Troubleshooting

| Symptom | Cause and fix |
|---------|---------------|
| `ERROR: Repository not found` | The repository is private and Git is unauthenticated — see [Installing from a private repository](#installing-from-a-private-repository). |
| `ERROR: File "setup.py" not found` or `Neither 'setup.py' nor 'pyproject.toml' found` | The `#subdirectory=ext/fluxmapPy` fragment is missing or misspelled. It is case-sensitive: lowercase `f`, capital `P`. |
| `pip: command not found` | Use `python -m pip …` instead, or install pip (`sudo apt install python3-pip`, or use the conda route). |
| `ModuleNotFoundError: No module named 'venv'` | On Debian/Ubuntu: `sudo apt install python3-venv`. |
| `ModuleNotFoundError: No module named 'fluxmappy'` after a successful install | You are in a different interpreter than the one you installed into. Check with `python -c "import sys; print(sys.executable)"` and re-activate your environment. |
| `zsh: no matches found: fluxmappy@git+https://…` | The install argument was not quoted. Wrap the whole `"fluxmappy @ git+…"` string in double quotes. |

---
