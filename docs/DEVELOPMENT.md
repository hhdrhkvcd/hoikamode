# Development and reproducibility

Python 3.10+ is required for the tools. A normal player only needs Windows PowerShell 5.1 and the ready-to-install ZIP.

## Layout

- `Balkan_Collapse/`: game text, local artwork, flags and small map text files.
- `assets/millennium_map.zip`: **required source asset**, containing large map bitmaps/textures and unit placements once, compressed. `START_BALKAN.ps1` expands it when installing from a Git checkout.
- `assets/MAP_SOURCE.json`: original RAR hashes, payload hashes, file inventory and compatibility changes.
- `data/balkans.json`: the regional state/capital roster, dates and leader choices.
- `tools/`: strict Clausewitz parser, import/configuration tools, artwork cropping, validator and package builder.
- `tests/`: structural tests and a deliberately limited ownership/flag/event model; it is not an HOI4 emulator.
- `scripts/BalkanTools.psm1`: shared Windows path, JSON, backup and launch helpers.
- `Balkan_Collapse_1980.zip`: the repository's existing installation artifact, regenerated for this release. It contains an **already expanded** map, not another nested map ZIP.
- `.work/`, `.venv/`, `dist/`, diagnostics and raw unpacked map images are ignored. Do not add full unpacked archives or build toolchains to Git.

## Build and validate from existing source

No RAR extractor or full Millennium Dawn installation is needed:

```bash
python tools/build_mod.py
python tools/validate_mod.py --package Balkan_Collapse_1980.zip
```

Development checks, including bitmap decoding:

```bash
python -m venv .venv
# Activate .venv, or use its Python explicitly.
python -m pip install -r requirements-dev.txt
python -m pytest -q
python tools/validate_mod.py --deep-images --package Balkan_Collapse_1980.zip
```

The validator checks state/province uniqueness and coverage, province colours, strategic region assignments, compatible categories/terrain/buildings, capitals, supply/railway references, tag registration, focus dependencies and local artwork, localisation, event references, payload hashes and the package inventory. It **does not** check every engine effect, external vanilla asset or DLC dependency by running the game.

The event model checks Tito's succession, historical releases, a consistent late start, one-time queues, armies, peace/subject relationships, refusal/acceptance of unification and stopping forced secessions after restoration. It intentionally ignores economic calculations, combat and many game effects. Passing it is not proof that HOI4 loads.

`tests/Test-Installer.ps1` is a Windows-only runtime test using isolated temporary Documents directories and `-NoLaunch`. It never installs into the user's real Documents or starts HOI4. It exercises installation, backup, malformed JSON handling, rollback, vanilla mode and log collection. On this Linux development machine it is skipped; it can be run on Windows or in Windows CI. Syntax-only PowerShell parsing is separate and does run here. Lua 5.1 checks use Lupa and a synthetic bootstrap, not proprietary game files: they reproduce the early-load nil error and verify that the late override preserves base tables. These are configuration tests, not an engine launch.

## Reimport the supplied source map

Only needed when deliberately regenerating/adapting map data. **Do not mix archives from different map versions.** Keep the original two RAR files unchanged. An external RAR5-capable 7-Zip is needed for this initial extraction, not for players or ordinary builds.

1. In an ignored working folder, copy/link the volumes to standard names `millennium.part1.rar` and `millennium.part2.rar`.
2. Extract **part 1**, letting 7-Zip read part 2 automatically. The result must contain `map/` and `history/states/`.
3. Run in this order:

```bash
python tools/import_map.py --source .work/millennium
python tools/configure_scenario.py
python tools/refresh_focuses.py
python tools/refresh_events.py
python tools/update_localisation.py
python tools/prepare_artwork.py
python -m pytest -q
python tools/build_mod.py
python tools/validate_mod.py --deep-images --package Balkan_Collapse_1980.zip
```

`prepare_artwork.py` needs Pillow, the supplied DDS images and `assets/source/bc_supplied_crisis.png`. That PNG is preserved unchanged from the earlier Recovery ZIP; the removed legacy installation archive is no longer a build dependency. The script crops/re-encodes existing illustrations and draws simple cosmetic flag geometry; it does not use any image-generation service.

The importer deliberately does not copy the source country's OOB, character, ideology or technology scripts: the uploaded archives do not contain their full dependency set. The world background is simplified for vanilla HOI4. Exact global historical politics and the complete Millennium Dawn mechanics are outside this conversion.

## Manual engine test

Follow [TESTING_RU.md](TESTING_RU.md), on a fresh game and with no other mods enabled. Record the actual game version/DLC and collect fresh logs before claiming engine compatibility. The descriptor deliberately does not advertise an untested `supported_version`.

## Bootstrap compatibility

Keep the scenario overrides in `common/defines/zz_balkan_collapse.lua`, after vanilla bootstrap files. Never add `NDefines = {}` or replace a complete namespace to suppress a nil error. Use `country_exists = TAG` for country references; `exists = yes/no` is a different scoped trigger. The validator rejects the former broken syntax and the obsolete early Lua file. See [the redacted 1.19.4 diagnosis](DIAGNOSIS_1_19_RU.md).
