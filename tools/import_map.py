#!/usr/bin/env python3
"""Adapt the user's *unpacked* map to standalone, vanilla-HOI4 Balkan Collapse.

Usage: python tools/import_map.py --source /path/to/unpacked/archives
Requires both original RAR volumes to have been unpacked together by 7-Zip.
Does NOT import Millennium Dawn's technologies, characters, ideologies or OOBs.
The duplicate top-level states/ directory is deliberately ignored.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import zipfile
from collections import defaultdict
from copy import deepcopy
from pathlib import Path

from clausewitz import Block, Entry, quote, read, write

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / "Balkan_Collapse"
DATA = json.loads((ROOT / "data/balkans.json").read_text("utf-8"))
COUNTRIES = DATA["countries"]
UNION = sorted({i for tag, c in COUNTRIES.items() if tag != "SRP" for i in c["states"]})
CATEGORIES = {
    "tiny_island": "tiny_island",
    "small_island": "small_island",
    "wasteland": "wasteland",
    "pastoral": "pastoral",
    "enclave": "enclave",
    "village": "rural",
    "rural": "rural",
    "suburb": "town",
    "town": "town",
    "large_suburb": "large_town",
    "large_town": "large_town",
    "city": "city",
    "large_city": "large_city",
    "metropolis": "metropolis",
    "conurbation": "megalopolis",
    "megalopolis": "megalopolis",
}
BUILDINGS = {
    "infrastructure": 5,
    "industrial_complex": 20,
    "arms_factory": 20,
    "dockyard": 20,
    "air_base": 10,
    "anti_air_building": 5,
    "synthetic_refinery": 3,
    "nuclear_reactor": 1,
    "fuel_silo": 3,
    "naval_base": 10,
    "bunker": 10,
    "coastal_bunker": 10,
    "radar_station": 6,
}
TECH = """set_technology = {
    tech_support = 1
    tech_engineers = 1
    tech_recon = 1
    infantry_weapons = 1
    infantry_weapons1 = 1
    infantry_weapons2 = 1
    support_weapons = 1
    support_weapons2 = 1
    gw_artillery = 1
    motorised_infantry = 1
    basic_train = 1
    basic_machine_tools = 1
    improved_machine_tools = 1
    construction1 = 1
    construction2 = 1
    electronic_mechanical_engineering = 1
    radio = 1
}
"""
PALETTE = {
    "SER": (196, 42, 55),
    "BOS": (32, 85, 154),
    "CRO": (205, 38, 50),
    "KOS": (38, 78, 160),
    "MAC": (200, 32, 42),
    "MNT": (174, 30, 39),
    "SLV": (45, 97, 150),
    "SRP": (185, 40, 52),
    "USA": (69, 95, 130),
    "SOV": (138, 61, 63),
    "PRC": (184, 60, 51),
    "ENG": (176, 143, 136),
    "FRA": (64, 96, 165),
    "GER": (129, 133, 132),
    "ITA": (91, 137, 81),
    "ALB": (155, 40, 45),
    "BUL": (124, 158, 96),
    "ROM": (181, 149, 74),
    "GRE": (60, 130, 173),
    "HUN": (145, 94, 62),
    "TUR": (176, 77, 70),
}


def text(path):
    data = path.read_bytes()
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError:
        return data.decode("cp1252")


def localisation(path, language, values):
    lines = [f"l_{language}:"]
    lines += [f" {key}:0 {quote(value)}" for key, value in sorted(values.items())]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8-sig")


def checksum(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def filtered_buildings(source, provinces, definitions, removed):
    result = Block()
    for e in source.entries():
        key = "industrial_complex" if e.key == "civilian_factory" else e.key
        if key.isdigit() and isinstance(e.value, Block):
            p = int(key)
            if p not in provinces:
                removed["misplaced_province_buildings"] += 1
                continue
            nested = filtered_buildings(e.value, provinces, definitions, removed)
            # Naval bases must be on coastal land provinces.
            if definitions[p][5] != "true":
                nested.remove("naval_base")
            if nested.items:
                result.add(key, nested)
        elif key in BUILDINGS and isinstance(e.value, str):
            level = max(0, min(BUILDINGS[key], int(float(e.value))))
            if level:
                result.set(key, str(level))
        else:
            removed[key] += 1
    return result


def make_oob(tag, provinces, count):
    lines = [
        "# Vanilla-compatible infantry; no dependency on modern-mod equipment.",
        "division_template = {",
        '    name = "BC Infantry"',
        "    regiments = {",
    ]
    for x in range(3):
        for y in range(2):
            lines.append(f"        infantry = {{ x = {x} y = {y} }}")
    lines += ["    }", "    support = { engineer = { x = 0 y = 0 } }", "}", "units = {"]
    for i in range(count):
        lines += [
            "    division = {",
            f'        name = "{i + 1}. {tag} Infantry"',
            f"        location = {provinces[i % len(provinces)]}",
            '        division_template = "BC Infantry"',
            "        start_experience_factor = 0.2",
            "        start_equipment_factor = 0.85",
            "    }",
        ]
    lines += ["}"]
    return "\n".join(lines) + "\n"


def import_map(source: Path):
    source = source.resolve()
    if (
        not (source / "map/provinces.bmp").is_file()
        or not (source / "history/states").is_dir()
    ):
        raise SystemExit(
            "Expected map/provinces.bmp and history/states/ from BOTH RAR volumes."
        )
    definitions = {
        int(r[0]): r
        for r in csv.reader(
            text(source / "map/definition.csv").splitlines(), delimiter=";"
        )
        if r and r[0].isdigit()
    }
    states = {}
    for file in sorted((source / "history/states").glob("*.txt")):
        state = read(file, legacy=True).block("state")
        state_id = int(state.scalar("id"))
        if state_id in states:
            raise ValueError(f"Duplicate state ID {state_id}")
        states[state_id] = (file, state)
    if not set(UNION).issubset(states):
        raise ValueError(
            "The supplied map does not contain the configured Balkan states."
        )

    tags = {}
    for f in sorted((source / "history/countries").glob("*.txt")):
        match = re.match(r"([A-Z0-9]{3})\s*-\s*(.+)", f.stem)
        if match:
            tags[match[1]] = (match[2].strip(), read(f, legacy=True))
    referenced = {"SER"}
    for _, state in states.values():
        history = state.block("history")
        referenced.add(history.scalar("owner"))
        for k in ["add_core_of", "add_claim_by"]:
            referenced.update(history.values(k))
    for tag in referenced:
        if not isinstance(tag, str) or not re.fullmatch(r"[A-Z0-9]{3}", tag):
            raise ValueError(f"Invalid country tag: {tag!r}")
        tags.setdefault(tag, (tag, Block()))

    state_dir = MOD / "history/states"
    state_dir.mkdir(parents=True, exist_ok=True)
    for old in state_dir.glob("*.txt"):
        old.unlink()
    owned = defaultdict(list)
    core_states = defaultdict(list)
    removed = defaultdict(int)
    state_names = {"english": {}, "russian": {}}
    converted = {}
    for state_id, (file, original) in sorted(states.items()):
        provinces = list(map(int, original.block("provinces").atoms()))
        h = original.block("history")
        owner = h.scalar("owner")
        if owner is None:
            raise ValueError(f"State {state_id} has no owner")
        owned[owner].append(state_id)
        cores = list(dict.fromkeys(h.values("add_core_of")))
        if owner not in cores and owner != "ZZZ":
            cores.append(owner)
        for core in cores:
            core_states[core].append(state_id)
        history = Block([Entry("owner", "SER" if state_id in UNION else owner)])
        history.add("controller", "SER" if state_id in UNION else owner)
        for core in cores:
            history.add("add_core_of", core)
        if state_id in UNION and "SER" not in cores:
            history.add("add_core_of", "SER")
        for claim in dict.fromkeys(h.values("add_claim_by")):
            if claim not in cores:
                history.add("add_claim_by", claim)
        for vp in h.values("victory_points"):
            if isinstance(vp, Block):
                p, points = map(int, vp.atoms())
                if p in provinces and definitions[p][4] == "land":
                    history.add("victory_points", Block([str(p), str(max(1, points))]))
        buildings = filtered_buildings(
            h.get("buildings", Block()), set(provinces), definitions, removed
        )
        history.add("buildings", buildings)
        # State histories also initialise the 2008 quick-start without replaying old events.
        if state_id in UNION and owner != "SER":
            date = COUNTRIES[owner]["independence"]
            history.add(
                date,
                Block(
                    [
                        Entry("owner", owner),
                        Entry("controller", owner),
                        Entry("remove_core_of", "SER"),
                    ]
                ),
            )
            if state_id in [848, 849, 850]:
                # The initial SRP release is a game abstraction of the Bosnian conflict.
                history.remove(date)
                history.add(
                    "1992.1.9",
                    Block(
                        [
                            Entry("owner", "SRP"),
                            Entry("controller", "SRP"),
                            Entry("remove_core_of", "SER"),
                        ]
                    ),
                )
                if state_id == 850:
                    history.add(
                        "1995.12.14",
                        Block([Entry("owner", "BOS"), Entry("controller", "BOS")]),
                    )
            if owner == "KOS":
                history.values(date)[0].items.append(Entry("add_claim_by", "SER"))
        category = original.scalar("state_category")
        if category not in CATEGORIES:
            raise ValueError(f"Unsupported state category {category}")
        result = Block(
            [
                Entry("id", str(state_id)),
                Entry("name", quote(f"STATE_{state_id}")),
                Entry("manpower", original.get("manpower")),
                Entry("state_category", CATEGORIES[category]),
            ]
        )
        if original.get("impassable"):
            result.add("impassable", original.get("impassable"))
        resources = original.get("resources")
        if resources:
            result.add("resources", deepcopy(resources))
        result.add("history", history)
        result.add("provinces", Block([str(p) for p in provinces]))
        converted[state_id] = result
        write(
            state_dir / f"{state_id}-BC.txt",
            Block([Entry("state", result)]),
            "# Adapted from the user-provided modern map. See assets/MAP_SOURCE.json.\n",
        )
        name = re.sub(r"^\d+\s*-\s*", "", file.stem).strip()
        names = DATA["state_names"].get(str(state_id), [name, name])
        for lang, label in zip(["english", "russian"], names):
            state_names[lang][f"STATE_{state_id}"] = label

    (MOD / "common/countries").mkdir(parents=True, exist_ok=True)
    (MOD / "common/countries/BC_World.txt").write_text(
        "graphical_culture = western_european_gfx\ngraphical_culture_2d = western_european_2d\n",
        encoding="utf-8",
    )
    tags_lines, colors = [], []
    world_names = {"english": {}, "russian": {}}
    country_hist = MOD / "history/countries"
    unit_dir = MOD / "history/units"
    unit_dir.mkdir(parents=True, exist_ok=True)
    for old in country_hist.glob("*- BC World.txt"):
        old.unlink()
    for tag, (name, raw_history) in sorted(tags.items()):
        path = f"countries/{tag}.txt" if tag in COUNTRIES else "countries/BC_World.txt"
        tags_lines.append(f'{tag} = "{path}"')
        rgb = PALETTE.get(
            tag, tuple(65 + b % 135 for b in hashlib.sha256(tag.encode()).digest()[:3])
        )
        colors.append(
            f"{tag} = {{ color = rgb {{ {' '.join(map(str, rgb))} }} color_ui = rgb {{ {' '.join(map(str, rgb))} }} }}"
        )
        if tag in COUNTRIES:
            continue
        if tag == "PLD":
            name = "Poland"
        for lang, names in world_names.items():
            names[tag] = name
            names[f"{tag}_DEF"] = name
            names[f"BC_GOV_{tag}"] = (
                f"{name}: government" if lang == "english" else f"{name}: правительство"
            )
            for ideology in ["democratic", "communism", "neutrality", "fascism"]:
                names[f"{tag}_{ideology}"] = name
                names[f"{tag}_{ideology}_DEF"] = name
        candidates = owned[tag] or core_states[tag] or [1]
        preferred = raw_history.scalar("capital")
        capital = (
            int(preferred)
            if preferred and preferred.isdigit() and int(preferred) in candidates
            else candidates[0]
        )
        politics = "neutrality"
        popularity = "{ democratic = 10 fascism = 0 communism = 10 neutrality = 80 }"
        if tag in [
            "USA",
            "ENG",
            "FRA",
            "GER",
            "ITA",
            "PLD",
            "JAP",
            "CAN",
            "AST",
            "NZL",
            "GRE",
            "BUL",
            "ROM",
            "ALB",
            "HUN",
        ]:
            politics = "democratic"
            popularity = "{ democratic = 80 fascism = 0 communism = 5 neutrality = 15 }"
        if tag in ["PRC", "PRK", "CUB", "VIN", "LAO"]:
            politics = "communism"
            popularity = "{ democratic = 5 fascism = 0 communism = 80 neutrality = 15 }"
        subtype = {
            "democratic": "centrism",
            "communism": "marxism",
            "neutrality": "despotism",
        }[politics]
        lines = [
            "# Simplified background country; not imported modern-mod scripts.",
            f"capital = {capital}",
            "set_research_slots = 3",
            "set_stability = 0.6",
            "set_war_support = 0.2",
            TECH,
            f"set_politics = {{ ruling_party = {politics} elections_allowed = no }}",
            f"set_popularities = {popularity}",
            "create_country_leader = {",
            f"    name = BC_GOV_{tag}",
            '    picture = "gfx/leaders/BC/BC_government.dds"',
            f"    ideology = {subtype}",
            '    expire = "2036.1.1.12"',
            "    traits = { }",
            "}",
        ]
        if owned[tag]:
            locations = [
                int(p)
                for s in owned[tag]
                for p in converted[s].block("provinces").atoms()
                if definitions[int(p)][4] == "land"
            ]
            capital_provinces = [
                int(p)
                for p in converted[capital].block("provinces").atoms()
                if definitions[int(p)][4] == "land"
            ]
            count = max(2, min(18, len(owned[tag])))
            (unit_dir / f"BC_WORLD_{tag}.txt").write_text(
                make_oob(tag, capital_provinces + locations, count), encoding="utf-8"
            )
            lines.append(f'oob = "BC_WORLD_{tag}"')
        (country_hist / f"{tag} - BC World.txt").write_text(
            "\n".join(lines) + "\n", encoding="utf-8"
        )

    tag_dir = MOD / "common/country_tags"
    for old in tag_dir.glob("*.txt"):
        old.unlink()
    (tag_dir / "00_balkan_world.txt").write_text(
        "\n".join(tags_lines) + "\n", encoding="utf-8"
    )
    (MOD / "common/countries/colors.txt").write_text(
        "\n".join(colors) + "\n", encoding="utf-8"
    )

    map_dir = MOD / "map"
    map_dir.mkdir(parents=True, exist_ok=True)
    for f in (source / "map").glob("*"):
        if (
            f.is_file()
            and f.suffix.lower() in [".txt", ".csv", ".map"]
            and f.name != "unitstacks.txt"
        ):
            if f.name == "buildings.txt":
                lines = [
                    line
                    for line in text(f).splitlines()
                    if len(line.split(";")) > 1 and line.split(";")[1] in BUILDINGS
                ]
                (map_dir / f.name).write_text("\n".join(lines) + "\n", encoding="utf-8")
            elif f.name == "definition.csv":
                vanilla_terrain = {
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
                rows = list(csv.reader(text(f).splitlines(), delimiter=";"))
                for row in rows:
                    if len(row) > 6 and row[6] not in vanilla_terrain:
                        row[6] = {
                            "exclusion_zone": "forest",
                            "twin_peaks": "mountain",
                            "groom_lake": "desert",
                        }.get(row[6], "urban")
                        removed["custom_terrain_types"] += 1
                (map_dir / f.name).write_text(
                    "\n".join(";".join(row) for row in rows) + "\n", encoding="utf-8"
                )
            elif f.name == "ambient_object.txt":
                # The archives do not include the modern mod's 3-D landmark entities.
                ambient = read(f, legacy=True)
                ambient.items[:] = [
                    e
                    for e in ambient.entries("type")
                    if e.value.scalar("type")
                    in ["ambient_wind_entity", "ambient_water_entity"]
                ]
                write(map_dir / f.name, ambient)
            elif f.name == "cities.txt":
                cities = read(f, legacy=True)
                from clausewitz import walk

                for e in walk(cities):
                    if e.key == "mesh":
                        e.value = Block([quote("westerngfx_house_1_1")])
                write(map_dir / f.name, cities)
            else:
                (map_dir / f.name).write_text(
                    "\n".join(line.rstrip() for line in text(f).splitlines()) + "\n",
                    encoding="utf-8",
                )
    region_dir = map_dir / "strategicregions"
    region_dir.mkdir(parents=True, exist_ok=True)
    for old in region_dir.glob("*.txt"):
        old.unlink()
    region_names = {"english": {}, "russian": {}}
    region_count = 0
    for f in sorted((source / "map/strategicregions").glob("*.txt")):
        parsed = read(f, legacy=True)
        if not parsed.get("strategic_region"):
            continue  # Empty, intentionally retired regions from the source map.
        region = parsed.block("strategic_region")
        region_id = int(region.scalar("id"))
        write(region_dir / f"{region_id}-BC.txt", parsed)
        region_count += 1
        name = re.sub(r"^\d+\s*-\s*", "", f.stem).strip()
        for names in region_names.values():
            names[f"STRATEGICREGION_{region_id}"] = name
    for lang in ["english", "russian"]:
        loc_dir = MOD / "localisation" / lang
        localisation(
            loc_dir / f"bc_map_l_{lang}.yml",
            lang,
            {**state_names[lang], **region_names[lang], **world_names[lang]},
        )

    # Store big images ONCE in Git, compressed. Both installers expand this payload.
    assets = ROOT / "assets"
    assets.mkdir(exist_ok=True)
    binary_files = [
        p
        for p in (source / "map").rglob("*")
        if p.is_file()
        and (p.suffix.lower() in [".bmp", ".dds"] or p.name == "unitstacks.txt")
        and p.name != "terrain.bmp"
    ]
    binary_files.sort()
    payload = assets / "millennium_map.zip"
    with zipfile.ZipFile(
        payload, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as archive:
        for file in binary_files:
            name = file.relative_to(source).as_posix()
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 28, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(
                info,
                file.read_bytes(),
                compress_type=zipfile.ZIP_DEFLATED,
                compresslevel=9,
            )
    manifest = {
        "source": "Two user-provided RAR volumes; supplied as Millennium Dawn map/history files",
        "note": "No full upstream mod was imported. Top-level states/ duplicates history/states/ and was ignored.",
        "source_archives": {p.name: checksum(p) for p in sorted(ROOT.glob("*.rar"))},
        "payload": payload.relative_to(ROOT).as_posix(),
        "payload_sha256": checksum(payload),
        "payload_files": {
            p.relative_to(source).as_posix(): checksum(p) for p in binary_files
        },
        "states": len(states),
        "strategic_regions": region_count,
        "registered_tags": len(tags),
        "union_states": UNION,
        "removed_unsupported_buildings": dict(sorted(removed.items())),
    }
    (assets / "MAP_SOURCE.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                k: v
                for k, v in manifest.items()
                if k not in ["payload_files", "source_archives"]
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    print(f"Map payload: {payload.stat().st_size / 1024**2:.1f} MiB compressed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    import_map(parser.parse_args().source)
