#!/usr/bin/env python3
"""Generate shared scenario plumbing from data/balkans.json (stdlib only)."""

from __future__ import annotations

import json
from pathlib import Path

from clausewitz import quote, read
from import_map import TECH, make_oob

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / "Balkan_Collapse"
DATA = json.loads((ROOT / "data/balkans.json").read_text("utf-8"))
COUNTRIES = DATA["countries"]
UNION = sorted({s for tag, c in COUNTRIES.items() if tag != "SRP" for s in c["states"]})
# Marks initialise late starts only. The running campaign is driven by on_daily events.
SER_FLAGS = {
    "1980.5.4": ["SER_tito_dead"],
    "1990.12.23": ["SER_slovenia_plebiscite"],
    "1991.5.19": ["SER_croatia_referendum"],
    "1991.6.25": ["SER_first_breakup_wave"],
    "1991.6.27": ["SER_slovenia_war_started"],
    "1991.7.7": ["SER_slovenia_war_ended"],
    "1991.8.25": ["SER_croatia_war_started"],
    "1991.9.8": ["SER_macedonia_referendum"],
    "1991.9.25": ["SER_macedonia_independent"],
    "1991.10.8": ["SER_croatia_separation_confirmed"],
    "1992.1.9": ["SER_srp_proclaimed"],
    "1992.1.15": ["SER_ec_recognition"],
    "1992.3.3": ["SER_bosnia_independent"],
    "1992.4.27": ["SER_fry_formed"],
    "1995.11.12": ["SER_croatia_war_ended"],
    "2006.6.3": ["SER_montenegro_independent"],
    "2008.2.17": ["SER_kosovo_independent"],
}


def put(relative, content):
    path = MOD / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


def leader(tag, tito=False):
    c = COUNTRIES[tag]
    name = "Josip Broz Tito" if tito else c["leader"]
    desc = "SER_TITO_DESC" if tito else f"{tag}_LEADER_DESC"
    picture = "BC_Tito" if tito else f"BC_{tag}_government"
    ideology = "stalinism" if tito else c["ideology"]
    return f"""create_country_leader = {{
    name = {quote(name)}
    desc = {desc}
    picture = "gfx/leaders/BC/{picture}.dds"
    expire = "2036.1.1.12"
    ideology = {ideology}
    traits = {{ }}
}}"""


def generate():
    replacements = [
        "common/bookmarks",
        "common/country_tags",
        "common/characters",
        "common/national_focus",
        "common/on_actions",
        "common/decisions",
        "history/countries",
        "history/states",
        "history/units",
        "history/general",
        "map/strategicregions",
        "map/supplyareas",
        "events",
    ]
    descriptor = f"""name="Балканы 1980: распад и воссоединение"
version="{DATA["version"]}"
picture="thumbnail.png"
tags={{ "Alternative History" "Events" "Gameplay" "National Focuses" }}
"""
    descriptor += "".join(f'replace_path="{p}"\n' for p in replacements)
    # No unverified supported_version and no dependency on the full Millennium Dawn mod.
    (MOD / "descriptor.mod").write_text(descriptor, encoding="utf-8")
    (ROOT / "Balkan_Collapse.mod").write_text(
        descriptor + 'path="mod/Balkan_Collapse"\n', encoding="utf-8"
    )
    # Vanilla creates NDefines in its 00_* files. An earlier-sorting override
    # aborts Lua initialization and leaves unrelated engine defines unset.
    (MOD / "common/defines/00_balkan_collapse.lua").unlink(missing_ok=True)
    put(
        "common/defines/zz_balkan_collapse.lua",
        """-- Load after vanilla 00_* defines. Never create or replace NDefines tables.
NDefines.NGame.START_DATE = "1980.5.1.12"
NDefines.NGame.END_DATE = "2036.1.1.1"
NDefines.NDiplomacy.TENSION_TIME_SCALE_START_DATE = "1980.5.1.12"
""",
    )
    put(
        "common/characters/00_bc_characters.txt",
        "# Leaders are defined explicitly in country histories. Vanilla 1936 characters are not loaded.",
    )
    put(
        "history/general/00_bc_scenario.txt",
        "# No vanilla 1936 wars, factions or dated global setup on the modern map.",
    )
    put(
        "map/supplyareas/00_bc_unused.txt",
        "# Legacy pre-NSB supply areas are intentionally not used.",
    )
    for tag in COUNTRIES:
        put(
            f"common/countries/{tag}.txt",
            """graphical_culture = eastern_european_gfx
graphical_culture_2d = eastern_european_2d""",
        )
    old = MOD / "common/countries/Republika_Srpska.txt"
    if old.exists():
        old.unlink()

    # Existing files retain their readable names, but all capitals now refer to this map.
    for tag, c in COUNTRIES.items():
        filename = next((MOD / "history/countries").glob(f"{tag} - *.txt"))
        party = c["ruling_party"]
        head = [
            f"capital = {c['capital']}",
            "set_research_slots = 3",
            "set_stability = 0.55",
            "set_war_support = 0.25",
            "set_convoys = 20",
            TECH,
        ]
        if tag == "SER":
            head += [
                "set_politics = { ruling_party = communism elections_allowed = no }",
                "set_popularities = { democratic = 7 fascism = 3 communism = 78 neutrality = 12 }",
                "set_country_flag = SER_tito_alive",
                "add_ideas = { BC_debt_crisis BC_fragmented_command }",
                "set_cosmetic_tag = BC_YUGOSLAVIA",
                leader(tag, tito=True),
                'oob = "BC_SER_1980"',
                "set_country_flag = BC_army_initialized",
            ]
            for date, flags in SER_FLAGS.items():
                contents = [f"set_country_flag = {flag}" for flag in flags]
                if date == "1980.5.4":
                    contents += ["BC_tito_succession = yes"]
                if date == "1991.6.25":
                    contents += ['oob = "BC_SER_2008"', "set_cosmetic_tag = BC_SERBIA"]
                if date == "1992.4.27":
                    contents += ["set_cosmetic_tag = BC_FRY"]
                if date == "2006.6.3":
                    contents += ["set_cosmetic_tag = BC_SERBIA"]
                head.append(f"{date} = {{\n    " + "\n    ".join(contents) + "\n}")
        else:
            neutral = party == "neutrality"
            popularities = (
                "{ democratic = 25 fascism = 5 communism = 5 neutrality = 65 }"
                if neutral
                else "{ democratic = 65 fascism = 5 communism = 10 neutrality = 20 }"
            )
            head += [
                f"set_politics = {{ ruling_party = {party} elections_allowed = no }}",
                f"set_popularities = {popularities}",
                leader(tag),
            ]
            contents = [
                "set_country_flag = BALKANS_INDEPENDENT",
                "set_country_flag = BC_army_initialized",
                f'oob = "BC_{tag}"',
            ]
            if tag == "SRP":
                contents += ["set_country_flag = SRP_proclaimed"]
            head.append(
                f"{c['independence']} = {{\n    " + "\n    ".join(contents) + "\n}"
            )
            if tag == "SRP":
                head += [
                    "1992.2.28 = { set_country_flag = SRP_constitution }",
                    "1992.4.6 = { set_country_flag = SRP_bosnia_war_started }",
                    "1995.12.14 = { set_country_flag = SRP_dayton_signed }",
                ]
            if tag == "MAC":
                head.append("1991.11.17 = { set_country_flag = MAC_constitution }")
        filename.write_text("\n\n".join(head) + "\n", encoding="utf-8")

    # OOB locations are land provinces that actually belong to the configured country.
    for tag, c in COUNTRIES.items():
        state_ids = c["states"] if tag != "BOS" else [104, 851, 850]
        locations = []
        for s in [c["capital"]] + [i for i in state_ids if i != c["capital"]]:
            state = read(MOD / f"history/states/{s}-BC.txt").block("state")
            vps = [
                int(v.atoms()[0])
                for v in state.block("history").values("victory_points")
            ]
            locations.extend(vps or map(int, state.block("provinces").atoms()))
        put(
            f"history/units/BC_{tag if tag != 'SER' else 'SER_2008'}.txt",
            make_oob(tag, locations, c["divisions"]),
        )
    federation_locations = [11586, 3617, 3882, 11581, 9627, 11899, 9809, 11887]
    put("history/units/BC_SER_1980.txt", make_oob("JNA", federation_locations, 18))

    # Shared, guarded effects used by both historical events and the quick start.
    effects = []
    effects.append(
        "BC_tito_succession = {\n"
        "    kill_country_leader = yes\n"
        "    clr_country_flag = SER_tito_alive\n"
        "    set_country_flag = SER_tito_dead\n"
        f"    {leader('SER')}\n"
        "    set_politics = { ruling_party = democratic elections_allowed = no }\n"
        "    set_popularities = { democratic = 55 fascism = 5 communism = 25 neutrality = 15 }\n}"
    )
    for tag, c in COUNTRIES.items():
        if tag == "SER":
            continue
        ids = c.get("release_states", c["states"])
        effects.append(f"""BC_initialize_{tag}_army = {{
    if = {{
        limit = {{ NOT = {{ has_country_flag = BC_army_initialized }} }}
        set_country_flag = BC_army_initialized
        load_oob = "BC_{tag}"
        add_equipment_to_stockpile = {{ type = infantry_equipment_1 amount = 1500 producer = {tag} }}
    }}
}}""")
        lines = [
            f"BC_release_{tag} = {{",
            "    if = {",
            f"        limit = {{ NOT = {{ country_exists = {tag} }} }}",
            f"        release = {tag}",
            "    }",
            f"    if = {{ limit = {{ country_exists = {tag} }}",
            f"        {tag} = {{",
            "            set_country_flag = BALKANS_INDEPENDENT",
            f"            BC_initialize_{tag}_army = yes",
            "        }",
            "    }",
        ]
        for s in ids:
            lines.append(f"    {s} = {{ remove_core_of = SER }}")
        lines.append("}")
        effects.append("\n".join(lines))
    effects.append(
        "BC_restore_federation = {\n"
        "    set_country_flag = BC_federation_restored\n"
        "    set_cosmetic_tag = BC_RESTORED_YUGOSLAVIA\n"
        "    remove_ideas = BC_debt_crisis\n"
        "    add_stability = 0.1\n"
        "    add_political_power = 100\n"
        + "".join(f"    {s} = {{ add_core_of = SER }}\n" for s in UNION)
        + "}"
    )
    effects.append(
        "BC_dayton_settlement = {\n"
        "    if = { limit = { country_exists = BOS country_exists = SRP }\n"
        "        if = { limit = { SRP = { has_war_with = BOS } } SRP = { white_peace = BOS } }\n"
        "        if = { limit = { 850 = { is_owned_by = SRP } } BOS = { transfer_state = 850 } }\n"
        "        if = { limit = { SRP = { is_subject = no } } BOS = { puppet = SRP } }\n"
        "        SRP = { set_politics = { ruling_party = neutrality elections_allowed = no } }\n"
        "    }\n}"
    )
    put("common/scripted_effects/bc_scenario_effects.txt", "\n\n".join(effects))
    trigger = (
        "BC_owns_all_yugoslavia = {\n"
        + "".join(f"    owns_state = {s}\n    controls_state = {s}\n" for s in UNION)
        + "}"
    )
    put("common/scripted_triggers/bc_scenario_triggers.txt", trigger)
    put(
        "common/ideas/bc_ideas.txt",
        """ideas = {
    country = {
        BC_debt_crisis = {
            picture = BC_debt_crisis
            allowed = { original_tag = SER }
            removal_cost = -1
            modifier = { stability_factor = -0.1 consumer_goods_factor = 0.08 production_speed_buildings_factor = -0.05 }
        }
        BC_fragmented_command = {
            picture = BC_fragmented_command
            allowed = { original_tag = SER }
            removal_cost = -1
            modifier = { army_org_factor = -0.08 }
        }
        BC_reconstruction_program = {
            picture = BC_reconstruction_program
            allowed = { always = yes }
            removal_cost = -1
            modifier = { production_speed_buildings_factor = 0.05 }
        }
    }
}""",
    )
    put(
        "common/opinion_modifiers/bc_opinions.txt",
        """opinion_modifiers = {
    BC_regional_cooperation = { value = 25 }
}""",
    )

    bookmarks = []
    for date, name, desc, picture, ideology in [
        (
            "1980.5.1.12",
            "SERBIA_1980_NAME",
            "SERBIA_1980_DESC",
            "GFX_BC_BOOKMARK_1980",
            "communism",
        ),
        (
            "2008.2.18.12",
            "BC_2008_NAME",
            "BC_2008_DESC",
            "GFX_BC_BOOKMARK_SERBIA",
            "democratic",
        ),
    ]:
        lines = [
            "bookmark = {",
            f"    name = {name}",
            f"    desc = {desc}",
            f"    date = {date}",
            f"    picture = {picture}",
            "    default = yes" if date.startswith("1980") else "    default = no",
            '    default_country = "SER"',
            f"    SER = {{ history = {'SER_BOOKMARK_1980_HISTORY' if date.startswith('1980') else 'BC_SER_BOOKMARK_2008_HISTORY'} ideology = {ideology} focuses = {{ SER_tito_aftermath }} }}",
        ]
        if date.startswith("2008"):
            for tag, c in COUNTRIES.items():
                if tag != "SER":
                    focus = (
                        "SRP_proclamation" if tag == "SRP" else f"{tag}_independence"
                    )
                    lines.append(
                        f"    {tag} = {{ history = BC_{tag}_BOOKMARK_HISTORY ideology = {c['ruling_party']} focuses = {{ {focus} }} }}"
                    )
        lines += ["    effect = { randomize_weather = 19800501 }", "}"]
        bookmarks.append("\n".join(lines))
    put(
        "common/bookmarks/balkan_collapse_1980.txt",
        "bookmarks = {\n" + "\n".join(bookmarks) + "\n}",
    )


if __name__ == "__main__":
    generate()
    print(
        "Generated scenario descriptors, two bookmarks, eight country histories and army setup."
    )
