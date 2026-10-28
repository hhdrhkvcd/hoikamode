#!/usr/bin/env python3
"""Offline structural validation, NOT an HOI4 engine/Windows launch test."""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import re
import zipfile
from collections import Counter
from io import BytesIO
from pathlib import Path, PurePosixPath

from clausewitz import Block, read, unquote, walk

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / "Balkan_Collapse"
DATE = re.compile(r"^\d{4}\.\d{1,2}\.\d{1,2}(?:\.\d{1,2})?$")
TERRAINS = {
    "unknown",
    "plains",
    "forest",
    "hills",
    "mountain",
    "desert",
    "urban",
    "jungle",
    "marsh",
    "ocean",
    "lakes",
}
CATEGORIES = {
    "wasteland",
    "pastoral",
    "rural",
    "town",
    "large_town",
    "city",
    "large_city",
    "metropolis",
    "megalopolis",
    "small_island",
    "tiny_island",
    "enclave",
}
BUILDINGS = {
    "infrastructure",
    "industrial_complex",
    "arms_factory",
    "dockyard",
    "air_base",
    "anti_air_building",
    "synthetic_refinery",
    "nuclear_reactor",
    "fuel_silo",
    "naval_base",
    "bunker",
    "coastal_bunker",
    "radar_station",
}


class ValidationError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ValidationError(message)


def validate_sprite_namespace(doc, origin="<interface>"):
    """Do not shadow native UI widgets with a different sprite implementation."""
    prefixes = ("GFX_BC_", "GFX_decision_BC_", "GFX_idea_BC_")
    for group in doc.values("spriteTypes"):
        for entry in group.entries():
            if isinstance(entry.value, Block):
                name = entry.value.scalar("name")
                require(
                    name and name.startswith(prefixes),
                    f"{origin}: unsafe interface sprite {name}; use the BC namespace, "
                    "never replace vanilla UI sprites",
                )


def validate_country_existence_triggers(doc, tags, origin="<script>"):
    for entry in walk(doc):
        if entry.key == "exists":
            require(
                isinstance(entry.value, str) and unquote(entry.value) in {"yes", "no"},
                f"{origin}: exists expects yes/no; use country_exists for a country tag",
            )
        elif entry.key == "country_exists":
            require(
                isinstance(entry.value, str)
                and unquote(entry.value)
                in set(tags) | {"ROOT", "FROM", "PREV", "THIS", "OVERLORD"},
                f"{origin}: unknown country_exists target {entry.value}",
            )


def load_localisation():
    result = {}
    for lang in ["english", "russian"]:
        values = {}
        for f in sorted((MOD / "localisation" / lang).glob("*.yml")):
            require(
                f.read_bytes().startswith(b"\xef\xbb\xbf"),
                f"{f}: missing localisation UTF-8 BOM",
            )
            lines = f.read_text("utf-8-sig").splitlines()
            require(lines[0] == f"l_{lang}:", f"{f}: wrong language header")
            for n, line in enumerate(lines[1:], 2):
                if not line.strip() or line.lstrip().startswith("#"):
                    continue
                match = re.fullmatch(r'\s+([\w.]+):\d*\s+(".*")\s*', line)
                require(match is not None, f"{f}:{n}: malformed localisation")
                key = match[1]
                require(key not in values, f"{lang}: duplicate localisation key {key}")
                values[key] = ast.literal_eval(match[2])
        result[lang] = values
    return result


def initial_state_history(state, date):
    result = {"owner": None, "controller": None, "cores": set(), "claims": set()}

    def apply(block):
        for e in block.entries():
            if e.key in ["owner", "controller"]:
                result[e.key] = unquote(e.value)
            elif e.key == "add_core_of":
                result["cores"].add(e.value)
            elif e.key == "remove_core_of":
                result["cores"].discard(e.value)
            elif e.key == "add_claim_by":
                result["claims"].add(e.value)

    history = state.block("history")
    apply(history)
    key = lambda d: tuple(map(int, d.split(".")[:3]))
    for entry in sorted(
        [e for e in history.entries() if DATE.fullmatch(e.key)],
        key=lambda e: key(e.key),
    ):
        if key(entry.key) <= key(date):
            apply(entry.value)
    return result


def source_data():
    config = json.loads((ROOT / "data/balkans.json").read_text("utf-8"))
    parsed = {}
    for folder in ["common", "history", "events", "interface"]:
        for f in (MOD / folder).rglob("*"):
            if f.is_file() and f.suffix in [".txt", ".gfx", ".mod"]:
                require(
                    not f.read_bytes().startswith(b"\xef\xbb\xbf"),
                    f"{f}: unexpected game-script BOM",
                )
                parsed[f.relative_to(MOD).as_posix()] = read(f)
    states = {}
    for name, doc in parsed.items():
        if name.startswith("history/states/"):
            state = doc.block("state")
            state_id = int(state.scalar("id"))
            require(state_id not in states, f"Duplicate state ID {state_id}")
            states[state_id] = state
    definitions = {}
    for row in csv.reader(
        (MOD / "map/definition.csv").read_text("utf-8").splitlines(), delimiter=";"
    ):
        if not row:
            continue
        require(len(row) >= 8, f"Bad province definition: {row}")
        i = int(row[0])
        require(i not in definitions, f"Duplicate province ID {i}")
        require(row[6] in TERRAINS, f"Unsupported custom terrain: {row}")
        definitions[i] = row
    return config, parsed, states, definitions


def validate_source(*, deep_images=False):
    config, parsed, states, definitions = source_data()
    loc = load_localisation()
    tags_doc = parsed["common/country_tags/00_balkan_world.txt"]
    tags = {e.key: unquote(e.value) for e in tags_doc.entries()}
    require(len(tags) == len(tags_doc.entries()), "Duplicate country registration")
    for name, doc in parsed.items():
        validate_country_existence_triggers(doc, tags, name)
    for tag, path in tags.items():
        require(re.fullmatch(r"[A-Z0-9]{3}", tag), f"Invalid country tag {tag}")
        require(
            (MOD / "common" / path).is_file(),
            f"{tag}: country definition {path} missing",
        )
    require(
        len(states) == 1493 and set(states) == set(range(1, 1494)),
        "Incomplete map state set",
    )
    province_states = {}
    for i, s in states.items():
        require(s.scalar("state_category") in CATEGORIES, f"{i}: incompatible category")
        provinces = list(map(int, s.block("provinces").atoms()))
        require(provinces, f"{i}: empty state")
        for p in provinces:
            require(p in definitions, f"{i}: undefined province {p}")
            require(
                definitions[p][4] in ["land", "lake"], f"{i}: sea province {p} in state"
            )
            require(p not in province_states, f"{p}: assigned to two states")
            province_states[p] = i
        h = s.block("history")
        require(h.scalar("owner") in tags, f"{i}: unregistered owner")
        for key in ["add_core_of", "add_claim_by"]:
            for tag in h.values(key):
                require(tag in tags, f"{i}: unregistered {key} {tag}")
        for vp in h.values("victory_points"):
            p, value = map(int, vp.atoms())
            require(
                p in provinces and definitions[p][4] == "land" and value > 0,
                f"{i}: invalid victory point {p}",
            )
        for e in h.get("buildings", Block()).entries():
            if e.key.isdigit():
                p = int(e.key)
                require(p in provinces, f"{i}: building in foreign province {p}")
                require(
                    {x.key for x in e.value.entries()}.issubset(BUILDINGS),
                    f"{i}: unsupported province building",
                )
                if e.value.get("naval_base"):
                    require(definitions[p][5] == "true", f"{i}: inland naval base {p}")
            else:
                require(e.key in BUILDINGS, f"{i}: unsupported building {e.key}")
                require(
                    e.key != "infrastructure" or int(e.value) <= 5,
                    f"{i}: infrastructure above vanilla cap",
                )
        for lang in loc:
            require(s.scalar("name") in loc[lang], f"{lang}: missing state name {i}")
    land = {p for p, row in definitions.items() if p and row[4] == "land"}
    require(
        land.issubset(province_states),
        f"Unassigned land: {sorted(land - province_states.keys())}",
    )
    require(
        len({tuple(r[1:4]) for r in definitions.values()}) == len(definitions),
        "Duplicate province RGB colour",
    )

    regions, region_provinces = {}, {}
    for f in (MOD / "map/strategicregions").glob("*.txt"):
        r = read(f).block("strategic_region")
        i = int(r.scalar("id"))
        require(i not in regions, f"Duplicate strategic region {i}")
        regions[i] = r
        for p in map(int, r.block("provinces").atoms()):
            require(
                p in definitions and p not in region_provinces,
                f"{p}: missing/duplicate strategic assignment",
            )
            region_provinces[p] = i
    require(len(regions) == 224, "Wrong strategic region count")
    require(
        set(region_provinces) == set(definitions) - {0},
        "Unassigned strategic provinces",
    )
    for i, s in states.items():
        require(
            len(
                {
                    region_provinces[int(p)]
                    for p in s.block("provinces").atoms()
                    if int(p) in land
                }
            )
            == 1,
            f"{i}: crosses air regions",
        )
    for n, line in enumerate((MOD / "map/railways.txt").read_text().splitlines(), 1):
        if line.strip():
            level, count, *route = map(int, line.split())
            require(
                1 <= level <= 5 and count == len(route) and set(route).issubset(land),
                f"Invalid railway line {n}",
            )
    for line in (MOD / "map/supply_nodes.txt").read_text().splitlines():
        if line.strip():
            level, p = map(int, line.split())
            require(level > 0 and p in land, f"Invalid supply node {p}")
    for n, line in enumerate((MOD / "map/buildings.txt").read_text().splitlines(), 1):
        row = line.split(";")
        i, p = int(row[0]), int(row[-1])
        require(i in states and row[1] in BUILDINGS, f"Invalid map building line {n}")
        require(
            not p or province_states.get(p) == i, f"Misplaced map building line {n}"
        )

    histories = {}
    for name, doc in parsed.items():
        if name.startswith("history/countries/"):
            tag = Path(name).name[:3]
            require(
                tag not in histories and tag in tags,
                f"Duplicate/unregistered country history {tag}",
            )
            require(
                int(doc.scalar("capital")) in states, f"{tag}: invalid capital state"
            )
            histories[tag] = doc
            for e in walk(doc):
                if e.key == "oob":
                    require(
                        f"history/units/{unquote(e.value)}.txt" in parsed,
                        f"{tag}: missing OOB {e.value}",
                    )
                if e.key == "picture":
                    require(
                        (MOD / unquote(e.value)).is_file(),
                        f"{tag}: missing leader portrait {e.value}",
                    )
    require(set(histories) == set(tags), "A registered country lacks a history file")
    for date in ["1980.5.1", "2008.2.18"]:
        effective = {i: initial_state_history(s, date) for i, s in states.items()}
        active = {s["owner"] for s in effective.values()}
        for tag in active:
            capital = int(histories[tag].scalar("capital"))
            require(
                effective[capital]["owner"] == tag, f"{date} {tag}: capital not owned"
            )
    for tag, c in config["countries"].items():
        require(
            int(histories[tag].scalar("capital")) == c["capital"],
            f"{tag}: stale capital",
        )
        for state in c["states"]:
            require(state in states, f"{tag}: missing region state {state}")

    sprites = {}
    for name, doc in parsed.items():
        if name.startswith("interface/"):
            validate_sprite_namespace(doc, name)
            for group in doc.values("spriteTypes"):
                for sprite in group.values("spriteType"):
                    key = sprite.scalar("name")
                    require(key not in sprites, f"Duplicate local sprite {key}")
                    tex = sprite.scalar("texturefile")
                    require((MOD / tex).is_file(), f"{key}: missing texture {tex}")
                    sprites[key] = tex
    focus_ids, counts, focus_trees = {}, Counter(), []
    for name, doc in parsed.items():
        if name.startswith("common/national_focus/"):
            tree = doc.block("focus_tree")
            focus_trees.append(tree)
            tree_id = tree.scalar("id")
            coords = set()
            for f in tree.values("focus"):
                key = f.scalar("id")
                require(key not in focus_ids, f"Duplicate focus ID {key}")
                focus_ids[key] = f
                counts[tree_id] += 1
                coord = (f.scalar("x"), f.scalar("y"))
                require(coord not in coords, f"{tree_id}: overlapping focus at {coord}")
                coords.add(coord)
                require(f.scalar("icon") in sprites, f"{key}: unresolved focus icon")
                for lang in loc:
                    require(
                        key in loc[lang] and key + "_desc" in loc[lang],
                        f"{lang}: missing focus text {key}",
                    )
            for f in tree.values("focus"):
                for parent in f.values("prerequisite") + f.values("mutually_exclusive"):
                    for e in parent.entries("focus"):
                        require(
                            e.value in {x.scalar("id") for x in tree.values("focus")},
                            f"{f.scalar('id')}: foreign/missing focus dependency {e.value}",
                        )
    require(len(focus_ids) == 415, "Expected 400 national + 15 generic focuses")
    require(
        sorted(counts.values()) == [15] + [50] * 8,
        f"Wrong national focus counts: {counts}",
    )
    require(
        sum(t.scalar("default") == "yes" for t in focus_trees) == 1,
        "Expected one generic default tree",
    )

    def visit(key, stack, seen):
        require(key not in stack, f"Focus prerequisite cycle at {key}")
        if key in seen:
            return
        stack.add(key)
        for p in focus_ids[key].values("prerequisite"):
            for e in p.entries("focus"):
                visit(e.value, stack, seen)
        stack.remove(key)
        seen.add(key)

    seen = set()
    for key in focus_ids:
        visit(key, set(), seen)

    bookmarks = (
        parsed["common/bookmarks/balkan_collapse_1980.txt"]
        .block("bookmarks")
        .values("bookmark")
    )
    require(
        [b.scalar("date") for b in bookmarks] == ["1980.5.1.12", "2008.2.18.12"],
        "Old or wrong scenario dates",
    )
    for b in bookmarks:
        require(b.scalar("picture") in sprites, "Missing bookmark artwork")
        for lang in loc:
            require(
                b.scalar("name") in loc[lang] and b.scalar("desc") in loc[lang],
                "Untranslated bookmark",
            )
        for e in b.entries():
            if e.key in tags:
                for f in e.value.block("focuses").atoms():
                    require(f in focus_ids, f"Bookmark points to missing focus {f}")
    require(
        not (MOD / "common/defines.lua").exists(),
        "Do not shadow vanilla common/defines.lua",
    )
    define_files = sorted((MOD / "common/defines").glob("*.lua"))
    require(
        [p.name for p in define_files] == ["zz_balkan_collapse.lua"],
        "Load the Balkan override after vanilla defines; remove obsolete 00_balkan_collapse.lua",
    )
    defines = define_files[0].read_text("utf-8")
    require(
        'NDefines.NGame.START_DATE = "1980.5.1.12"' in defines,
        "Start date override is ineffective",
    )
    require(
        not re.search(
            r"^\s*(?:NDefines(?:\.[A-Za-z_]\w*)?|NGame|NDiplomacy)\s*=",
            defines,
            re.MULTILINE,
        ),
        "Never create or replace a whole defines table; preserve vanilla initialization",
    )
    inner = read(MOD / "descriptor.mod")
    outer = read(ROOT / "Balkan_Collapse.mod")
    for descriptor in [inner, outer]:
        require(
            not {"common", "common/defines"}.intersection(
                unquote(value) for value in descriptor.values("replace_path")
            ),
            "The descriptor must preserve the vanilla defines bootstrap",
        )
    require(outer.scalar("path") == "mod/Balkan_Collapse", "Wrong launcher path")
    require(
        inner.scalar("version") == outer.scalar("version") == config["version"],
        "Version mismatch",
    )
    required_replace = {
        "history/states",
        "history/countries",
        "common/bookmarks",
        "events",
        "map/strategicregions",
        "common/national_focus",
    }
    require(
        required_replace.issubset({unquote(v) for v in inner.values("replace_path")}),
        "Missing total-map replace_path",
    )

    events = {}
    for name, doc in parsed.items():
        if name.startswith("events/"):
            for event in doc.values("country_event"):
                key = event.scalar("id")
                require(key not in events, f"Duplicate event {key}")
                events[key] = event
                require(
                    event.scalar("is_triggered_only") == "yes",
                    f"{key}: random event polling still enabled",
                )
                require(
                    event.scalar("picture") in sprites, f"{key}: missing event picture"
                )
                for lang in loc:
                    for field in ["title", "desc"]:
                        require(
                            event.scalar(field) in loc[lang],
                            f"{key}: missing {lang} event {field}",
                        )
                    for option in event.values("option"):
                        require(
                            option.scalar("name") in loc[lang],
                            f"{key}: missing {lang} option text",
                        )
    require(len(events) == 23, "Historical event chain is incomplete")
    for name, doc in parsed.items():
        for e in walk(doc):
            if e.key == "country_event" and isinstance(e.value, Block):
                require(
                    e.value.scalar("id") in events, f"{name}: undefined event reference"
                )
            if e.key in ["add_state_claim", "transfer_state"]:
                require(
                    int(e.value) in states, f"{name}: invalid state effect {e.value}"
                )
    hooks = parsed["common/on_actions/bc_timeline.txt"].block("on_actions")
    require(
        not hooks.get("on_daily"),
        "Global on_daily would repeat events once per country",
    )
    require(
        all(
            k in ["on_startup", "on_daily_SER", "on_daily_SRP", "on_daily_MAC"]
            for k in [e.key for e in hooks.entries()]
        ),
        "Unexpected timeline hooks",
    )
    queues = [e for e in walk(hooks) if e.key == "country_event"]
    require(len(queues) == 21, "Every historical event must have a daily queue")

    payload = ROOT / "assets/millennium_map.zip"
    info = json.loads((ROOT / "assets/MAP_SOURCE.json").read_text("utf-8"))
    require(
        hashlib.sha256(payload.read_bytes()).hexdigest() == info["payload_sha256"],
        "Map payload hash mismatch",
    )
    with zipfile.ZipFile(payload) as z:
        require(z.testzip() is None, "Damaged map ZIP member")
        require(
            set(z.namelist()) == set(info["payload_files"]),
            "Map payload manifest mismatch",
        )
        for member in z.infolist():
            path = PurePosixPath(member.filename)
            require(
                not path.is_absolute()
                and ".." not in path.parts
                and path.parts[0] == "map",
                "Unsafe map ZIP path",
            )
            require(
                hashlib.sha256(z.read(member)).hexdigest()
                == info["payload_files"][member.filename],
                f"Map member hash mismatch: {member.filename}",
            )
        if deep_images:
            from PIL import Image

            im = Image.open(BytesIO(z.read("map/provinces.bmp")))
            require(
                im.mode == "RGB" and im.size == (5632, 2048),
                "Wrong province BMP format",
            )
            colors = {tuple(map(int, r[1:4])): p for p, r in definitions.items()}
            used = {c for _, c in im.getcolors(im.width * im.height)}
            require(
                used == set(colors) - {(0, 0, 0)},
                "Province bitmap colours do not match definition.csv",
            )
            for name in [
                "heightmap.bmp",
                "rivers.bmp",
                "terrain_morecities.bmp",
                "cities.bmp",
            ]:
                image = Image.open(BytesIO(z.read("map/" + name)))
                require(
                    image.size == im.size and image.mode in ["P", "L"],
                    f"{name}: bad indexed bitmap format",
                )
    if deep_images:
        from PIL import Image

        for tex in set(sprites.values()):
            with Image.open(MOD / tex) as image:
                image.load()
        for tag in list(config["countries"]) + [
            "BC_YUGOSLAVIA",
            "BC_SERBIA",
            "BC_FRY",
            "BC_RESTORED_YUGOSLAVIA",
        ]:
            for folder, size in [
                ("", (82, 52)),
                ("medium", (41, 26)),
                ("small", (10, 7)),
            ]:
                with Image.open(MOD / "gfx/flags" / folder / f"{tag}.tga") as image:
                    require(image.size == size, f"{tag}: invalid {folder} flag size")
    return {
        "game_script_files": len(parsed),
        "states": len(states),
        "land_provinces": len(land),
        "strategic_regions": len(regions),
        "country_tags": len(tags),
        "national_focuses": 400,
        "generic_focuses": 15,
        "events": len(events),
        "bookmarks": [b.scalar("date") for b in bookmarks],
        "deep_images": deep_images,
        "engine_launch_tested": False,
    }


def validate_package(path):
    with zipfile.ZipFile(path) as z:
        require(z.testzip() is None, "Broken install ZIP")
        names = set(z.namelist())
        for name in names:
            p = PurePosixPath(name)
            require(
                not p.is_absolute() and ".." not in p.parts,
                f"Unsafe package path {name}",
            )
            require(
                not any(
                    x in p.parts for x in [".git", ".venv", ".work", "__pycache__"]
                ),
                "Development files leaked into package",
            )
        for file in [
            "START_BALKAN.bat",
            "START_VANILLA.bat",
            "COLLECT_BALKAN_LOGS.bat",
            "RESTORE_PREVIOUS_MODS.bat",
            "scripts/BalkanTools.psm1",
            "Balkan_Collapse.mod",
            "Balkan_Collapse/descriptor.mod",
            "Balkan_Collapse/map/provinces.bmp",
            "Balkan_Collapse/map/definition.csv",
        ]:
            require(file in names, f"Missing packaged file {file}")
        require(
            z.read("Balkan_Collapse/descriptor.mod")
            == (MOD / "descriptor.mod").read_bytes(),
            "Stale packaged descriptor",
        )
        require(
            len(
                [
                    n
                    for n in names
                    if n.startswith("Balkan_Collapse/history/states/")
                    and n.endswith(".txt")
                ]
            )
            == 1493,
            "Incomplete packaged states",
        )
        require(
            "assets/millennium_map.zip" not in names,
            "Distribution contains a redundant nested map archive",
        )
        info = json.loads((ROOT / "assets/MAP_SOURCE.json").read_text("utf-8"))
        for name, sha in info["payload_files"].items():
            require(
                hashlib.sha256(z.read("Balkan_Collapse/" + name)).hexdigest() == sha,
                f"Packaged map is stale: {name}",
            )
        for file in MOD.rglob("*"):
            if file.is_file() and "__pycache__" not in file.parts:
                name = "Balkan_Collapse/" + file.relative_to(MOD).as_posix()
                require(
                    name in names and z.read(name) == file.read_bytes(),
                    f"Packaged source is stale: {name}",
                )
        support = list(ROOT.glob("*.bat")) + list(ROOT.glob("*.ps1"))
        support += [
            p
            for folder in ["scripts", "docs"]
            for p in (ROOT / folder).rglob("*")
            if p.is_file()
        ]
        support += [
            ROOT / p
            for p in [
                "README.md",
                "NOTICE.md",
                "assets/MAP_SOURCE.json",
                "assets/ARTWORK_SOURCE.json",
            ]
        ]
        for file in support:
            name = file.relative_to(ROOT).as_posix()
            require(
                name in names and z.read(name) == file.read_bytes(),
                f"Packaged installer/document is stale: {name}",
            )
    return {
        "package": str(path),
        "files": len(names),
        "bytes": Path(path).stat().st_size,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--deep-images",
        action="store_true",
        help="Also decode map/portrait/flag textures (requires Pillow).",
    )
    parser.add_argument(
        "--package", type=Path, help="Also check a completed installation ZIP."
    )
    args = parser.parse_args()
    report = validate_source(deep_images=args.deep_images)
    if args.package:
        report.update(validate_package(args.package))
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
