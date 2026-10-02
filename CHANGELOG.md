# Changelog

All notable changes to `fluxmappy` are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project
aims to follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.0] - 2026-10-01

### Changed

- Public wrapper functions are named after the module that defines them,
  following eddy4R convention: `wrap_diu`, `wrap_filt_qf`, `wrap_open_fm`
  and `wrap_stat`.
- Module documentation is moving from roxygen-style header blocks to
  numpydoc docstrings (`Parameters`, `Returns`, `Examples`). Per-module
  changelog blocks are retired in favour of this file and the git history.

### Removed

- The descriptive aliases kept during the rename: `geofence_diurnal_cycles`,
  `geofence_statistics`, `open_fluxmap`, `qf_filter_rasters`,
  `iter_filtered_rasters` and `qf_filtered_rasters`. Each public function now
  has exactly one canonical name.
- `calculate_polygon_diurnal_cycles`. Its implementation now lives directly
  in `wrap_diu`, which it duplicated apart from accepting `vector` only as a
  `pathlib.Path`. Call `wrap_diu` instead.

### Fixed

- `from __future__ import annotations` in `wrap_filt_qf.py` was preceded by a
  second string literal, which made `import fluxmappy` fail with a
  `SyntaxError`.

## Development history

The entries below were migrated from the per-module header blocks used before
the package adopted numpydoc docstrings. These are development dates rather
than releases; no versions were tagged during this period.

### 2026-10-01

- Removed three def_functions, that were similar to wrap_functions. `calculate_polygon_diurnal_cycles`, `load_filtered_rasters`, and `iter_polygon_statistics`. They are removed from the mkdoc as well. 
- Moved `iter_polygon_statistics` from `wrap_stat.py` into its own definition module, `def_stat_iter.py`. It is still used internally by `wrap_stat` and `def_diu_coll.py`.


### 2026-09-29

- Removed doc string documentation at start of each function. Replaced with documentation after each created function within each file. Added parameters, returns, and examples. 

### 2026-09-25

- Added usage examples and clearer purpose descriptions to function docstrings.

### 2026-09-02

- Renamed each public wrapper function to match its module name.

### 2026-08-20

- Renamed the wrapper and model modules to eddy4R terms: `wrap_diu.py`,
  `wrap_filt_qf.py`, `wrap_open_fm.py`, `wrap_stat.py`, `modl_filt.py`.

### 2026-08-19

- Renamed the definition modules to eddy4R terms: `def_diu_calc.py`,
  `def_diu_coll.py`, `def_diu_lt.py`, `def_diu_tz_vali.py`,
  `def_filt_grid_vali.py`, `def_filt_pair.py`, `def_filt_qf_mask.py`,
  `def_filt_rast_name.py`, `def_filt_rast_pair.py`, `def_open_qf_path.py`,
  `def_stat_calc.py`, `def_stat_mask.py`, `def_stat_vect.py`.

### 2026-08-15

- Broke the larger functions apart into smaller definition modules to reduce
  the amount of code in any single file.

### 2026-08-10 – 2026-08-13

- Original creation of the filtering, geofencing, statistics and
  diurnal-cycle modules.
