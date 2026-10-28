#!/usr/bin/env python3
"""Keep the 8 x 50 existing focuses; give rewards real effects and local artwork.

The file IDs/localisation remain stable for translation. This operation is idempotent.
"""

import json
from pathlib import Path

from clausewitz import parse, read, write

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / "Balkan_Collapse"
DATA = json.loads((ROOT / "data/balkans.json").read_text("utf-8"))
COUNTRIES = DATA["countries"]


def block(text):
    return parse(text)


def factory(kind):
    return f"capital_scope = {{ add_extra_state_shared_building_slots = 1 add_building_construction = {{ type = {kind} level = 1 instant_build = yes }} }}"


def refresh():
    for file in sorted((MOD / "common/national_focus").glob("*.txt")):
        if file.name == "bc_generic_focus.txt":
            continue
        doc = read(file)
        tree = doc.block("focus_tree")
        tag = tree.scalar("id")[:3]
        focuses = tree.values("focus")
        if len(focuses) != 50:
            raise ValueError(f"{tag}: expected 50 focuses, found {len(focuses)}")
        for f in focuses:
            name = f.scalar("id")
            suffix = name[4:]
            icon = "government"
            reward = "add_political_power = 35 add_stability = 0.02"
            if any(
                k in suffix
                for k in [
                    "economy",
                    "industry",
                    "industrial",
                    "research",
                    "transport",
                    "trade",
                ]
            ):
                icon = "economy"
                reward = "add_political_power = 35"
                if "research" in suffix or suffix.endswith(
                    ("economy_09", "economy_expansion_09")
                ):
                    icon = "research"
                    reward += " add_tech_bonus = { name = BC_research_bonus bonus = 0.5 uses = 1 category = industry }"
                elif suffix == "transport" or "regional_trade" in suffix:
                    icon = "transport"
                    reward += " capital_scope = { if = { limit = { infrastructure < 5 } add_building_construction = { type = infrastructure level = 1 instant_build = yes } } }"
                elif suffix.endswith(("_01", "_04", "_08", "_12")) or suffix in [
                    "industry",
                    "industrial_revival",
                ]:
                    reward += " " + factory("industrial_complex")
                elif suffix.endswith(("_06", "_10", "_14")):
                    reward += " " + factory("arms_factory")
                else:
                    reward += " add_stability = 0.02"
            if any(k in suffix for k in ["army", "defence", "security", "rearmament"]):
                icon = "army"
                reward = "army_experience = 15 add_manpower = 4000"
                if suffix.endswith(("_03", "_07", "_11")) or suffix in [
                    "army",
                    "rearmament",
                ]:
                    reward += " " + factory("arms_factory")
                elif suffix.endswith(("_05", "_09", "_13")):
                    reward += f" add_equipment_to_stockpile = {{ type = infantry_equipment_1 amount = 1500 producer = {tag} }}"
                else:
                    reward += " add_war_support = 0.02"
            if any(
                k in suffix
                for k in ["diplomacy", "conference", "federal", "council", "peacefully"]
            ):
                icon = "diplomacy"
                reward = "add_political_power = 40 add_stability = 0.02"
                if tag != "SER":
                    reward += " add_opinion_modifier = { target = SER modifier = BC_regional_cooperation }"
                    if suffix.endswith("_13"):
                        reward += " set_country_flag = BC_open_to_federation"
            if suffix in [
                "independence",
                "proclamation",
                "sovereignty",
                "yugoslav_legacy",
            ]:
                icon = tag.lower()
            if suffix == "tito_aftermath":
                icon = "tito"
            if any(k in suffix for k in ["claim", "campaign", "serbian_program"]):
                icon = "reconstruction" if "campaign" in suffix else tag.lower()
            f.set("icon", f"GFX_BC_goal_{icon}")
            f.set("completion_reward", block(reward))
            f.set("ai_will_do", block("factor = 1"))
            if tag == "SER":
                special = {
                    "SER_balkan_conference": "add_political_power = 60 add_stability = 0.03",
                    "SER_serbian_program": "add_war_support = 0.08 add_political_power = 50",
                    "SER_federal_treaty": "set_rule = { can_create_factions = yes } if = { limit = { is_in_faction = no } create_faction = BC_BALKAN_FEDERATION } add_political_power = 50",
                    "SER_reunify_peacefully": "set_country_flag = BC_federal_negotiations\n"
                    + "\n".join(
                        f"if = {{ limit = {{ country_exists = {t} NOT = {{ has_war_with = {t} }} {t} = {{ is_subject = no has_war = no }} }} {t} = {{ country_event = {{ id = bc_federation.1 days = 1 }} }} }}"
                        for t in COUNTRIES
                        if t != "SER"
                    ),
                    "SER_balkan_campaign": "\n".join(
                        f"if = {{ limit = {{ country_exists = {t} NOT = {{ has_war_with = {t} }} {t} = {{ is_subject = no }} }} create_wargoal = {{ type = annex_everything target = {t} }} }}"
                        for t in COUNTRIES
                        if t != "SER"
                    )
                    + "\nadd_war_support = 0.05",
                    "SER_restore_cores": "BC_restore_federation = yes",
                    "SER_economy_expansion_10": factory("industrial_complex")
                    + " remove_ideas = BC_debt_crisis add_ideas = BC_reconstruction_program",
                    "SER_army_expansion_10": "remove_ideas = BC_fragmented_command army_experience = 25 add_manpower = 10000",
                }
                claims = {
                    "SER_claim_kosovo": COUNTRIES["KOS"]["states"],
                    "SER_claim_montenegro": COUNTRIES["MNT"]["states"],
                    "SER_claim_bosnia": COUNTRIES["BOS"]["states"],
                    "SER_claim_croatia_slovenia": COUNTRIES["CRO"]["states"]
                    + COUNTRIES["SLV"]["states"],
                }
                if name in claims:
                    special[name] = (
                        "\n".join(f"add_state_claim = {s}" for s in claims[name])
                        + "\nadd_political_power = 25"
                    )
                if name in special:
                    f.set("completion_reward", block(special[name]))
                if name in ["SER_balkan_conference", "SER_serbian_program"]:
                    f.set(
                        "available",
                        block(
                            "has_country_flag = SER_first_breakup_wave NOT = { has_country_flag = BC_federation_restored }"
                        ),
                    )
                if name == "SER_restore_cores":
                    f.set(
                        "available",
                        block(
                            "BC_owns_all_yugoslavia = yes NOT = { has_country_flag = BC_federation_restored }"
                        ),
                    )
                if name == "SER_reunify_peacefully":
                    f.set("available", block("has_war = no"))
                if name == "SER_federal_treaty":
                    f.set(
                        "available",
                        block("OR = { is_in_faction = no is_faction_leader = yes }"),
                    )
                if name.startswith("SER_army_expansion_"):
                    f.set("x", "15")
                    f.set("y", str(2 + int(name.rsplit("_", 1)[1])))
                if name == "SER_army_expansion_01":
                    # Army modernisation must not be locked behind already winning reunification.
                    f.set("prerequisite", block("focus = SER_modern_army"))
                if name in ["SER_claim_montenegro", "SER_claim_bosnia"]:
                    f.set("x", "9" if name.endswith("montenegro") else "12")
                if name == "SER_claim_croatia_slovenia":
                    f.remove("prerequisite")
                    for required in [
                        "SER_claim_kosovo",
                        "SER_claim_montenegro",
                        "SER_claim_bosnia",
                    ]:
                        f.add("prerequisite", block(f"focus = {required}"))
                if name in [
                    "SER_claim_croatia_slovenia",
                    "SER_rearmament",
                    "SER_balkan_campaign",
                    "SER_restore_cores",
                ]:
                    f.set("x", "9")
            f.set("cancel_if_invalid", "no")
        write(
            file,
            doc,
            "# Eight national trees retain 50 focuses each; photographs are reused, not AI-generated.\n",
        )

    generic = [
        "focus_tree = {",
        "    id = BC_generic_tree",
        "    default = yes",
        "    country = { factor = 1 }",
    ]
    branches = [
        ("civic", "government", "add_political_power = 70 add_stability = 0.05"),
        ("industry", "economy", factory("industrial_complex")),
        ("defence", "army", "army_experience = 15 " + factory("arms_factory")),
    ]
    for x, (branch, icon, reward) in enumerate(branches):
        for n in range(1, 6):
            name = f"BC_generic_{branch}_{n}"
            generic += [
                "    focus = {",
                f"        id = {name}",
                f"        icon = GFX_BC_goal_{icon}",
                f"        x = {2 + x * 3}",
                f"        y = {n - 1}",
                "        cost = 5",
            ]
            if n > 1:
                generic.append(
                    f"        prerequisite = {{ focus = BC_generic_{branch}_{n - 1} }}"
                )
            generic += [
                f"        completion_reward = {{ {reward} }}",
                "        ai_will_do = { factor = 1 }",
                "    }",
            ]
    generic.append("}")
    (MOD / "common/national_focus/bc_generic_focus.txt").write_text(
        "\n".join(generic) + "\n", encoding="utf-8"
    )
    print(
        "Updated 400 national focuses and added a small generic tree for background countries."
    )


if __name__ == "__main__":
    refresh()
