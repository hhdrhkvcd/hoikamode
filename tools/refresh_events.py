#!/usr/bin/env python3
"""Rewire the existing historical chain to country-specific daily hooks.

Dates are deterministic, and queue flags prevent duplicates while a human leaves
an event window open. Restoring the federation stops subsequent forced secessions.
"""

import json
from collections import defaultdict
from copy import deepcopy
from pathlib import Path

from clausewitz import Block, Entry, parse, read, write

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / "Balkan_Collapse"
COUNTRIES = json.loads((ROOT / "data/balkans.json").read_text("utf-8"))["countries"]


def block(text):
    return parse(text)


def replace_release_effects(b):
    for item in b.entries():
        if item.key == "release":
            item.key, item.value = f"BC_release_{item.value}", "yes"
        elif isinstance(item.value, Block):
            # release already creates an independent country; no DLC-specific autonomy change.
            if any(e.key == "set_autonomy" for e in item.value.entries()):
                b.items.remove(item)
            else:
                replace_release_effects(item.value)


def refresh():
    path = MOD / "events/serbia_collapse.txt"
    doc = read(path)
    hooks = defaultdict(list)
    for event in doc.values("country_event"):
        event_id = event.scalar("id")
        trigger = event.block("trigger")
        tag = trigger.scalar("tag")
        guard = "BC_queued_" + event_id.replace(".", "_")
        trigger.items[:] = [
            e
            for e in trigger.items
            if not (isinstance(e, Entry) and e.key == "BC_timeline_active")
        ]
        if event_id != "serbia_collapse.1":
            trigger.set("BC_timeline_active", "yes")
        event.remove("mean_time_to_happen")
        event.set("is_triggered_only", "yes")
        event.set(
            "picture",
            "GFX_BC_event_tito" if event_id.endswith(".1") else "GFX_BC_event_crisis",
        )
        option = event.block("option")
        replace_release_effects(option)
        if event_id == "serbia_collapse.1":
            event.set(
                "option",
                block(
                    "name = serbia_collapse.1.a BC_tito_succession = yes add_stability = -0.08 add_political_power = -50"
                ),
            )
        elif event_id == "serbia_collapse.12":
            event.set(
                "option",
                block(
                    "name = serbia_collapse.12.a set_country_flag = SER_fry_formed set_cosmetic_tag = BC_FRY add_stability = -0.03 add_political_power = 75"
                ),
            )
        elif event_id == "serbia_collapse.14":
            event.set(
                "option",
                block(
                    "name = serbia_collapse.14.a set_country_flag = SRP_dayton_signed BC_dayton_settlement = yes set_politics = { ruling_party = neutrality elections_allowed = no } add_stability = 0.08 add_war_support = -0.10"
                ),
            )
        elif event_id in [
            "serbia_collapse.3",
            "serbia_collapse.6",
            "serbia_collapse.11",
        ]:
            target = {
                "serbia_collapse.3": "SLV",
                "serbia_collapse.6": "CRO",
                "serbia_collapse.11": "BOS",
            }[event_id]
            if option.entries("declare_war_on"):
                option.remove("declare_war_on")
                option.items.extend(
                    block(
                        f"if = {{ limit = {{ country_exists = {target} NOT = {{ has_war_with = {target} }} {target} = {{ is_subject = no }} }} declare_war_on = {{ target = {target} type = annex_everything }} }}"
                    ).items
                )
        elif event_id in ["serbia_collapse.4", "serbia_collapse.13"]:
            target = "SLV" if event_id.endswith(".4") else "CRO"
            if option.entries("white_peace"):
                option.remove("white_peace")
                option.items.extend(
                    block(
                        f"if = {{ limit = {{ country_exists = {target} has_war_with = {target} }} white_peace = {target} }}"
                    ).items
                )
        if event_id == "serbia_collapse.2":
            option.set("set_cosmetic_tag", "BC_SERBIA")
        if event_id == "serbia_collapse.15":
            option.set("set_cosmetic_tag", "BC_SERBIA")
        conditions = deepcopy(trigger)
        conditions.items.append(Entry("NOT", block(f"has_country_flag = {guard}")))
        hook = Block(
            [
                Entry("limit", conditions),
                Entry("set_country_flag", guard),
                Entry("country_event", block(f"id = {event_id}")),
            ]
        )
        hooks[tag].append(Entry("if", hook))
    write(
        path,
        doc,
        "# Historical milestones; dates queued by on_daily_TAG, not random MTTH polling.\n",
    )
    triggers = MOD / "common/scripted_triggers/bc_scenario_triggers.txt"
    text = triggers.read_text("utf-8")
    if "BC_timeline_active" not in text:
        text += "\nBC_timeline_active = { SER = { NOT = { has_country_flag = BC_federation_restored } } }\n"
        triggers.write_text(text, encoding="utf-8")
    on_actions = Block()
    startup = block("""if = {
        limit = { NOT = { has_global_flag = BC_startup_complete } }
        set_global_flag = BC_startup_complete
        if = { limit = { date > 1995.12.13 country_exists = BOS country_exists = SRP } SER = { BC_dayton_settlement = yes } }
    }""")
    on_actions.add("on_startup", Block([Entry("effect", startup)]))
    for tag, entries in sorted(hooks.items()):
        on_actions.add(f"on_daily_{tag}", Block([Entry("effect", Block(entries))]))
    write(
        MOD / "common/on_actions/bc_timeline.txt",
        Block([Entry("on_actions", on_actions)]),
    )

    federation = """add_namespace = bc_federation
country_event = {
    id = bc_federation.1
    title = bc_federation.1.t
    desc = bc_federation.1.d
    picture = GFX_BC_event_serbia
    is_triggered_only = yes
    option = {
        name = bc_federation.1.a
        ai_chance = { factor = 70 modifier = { factor = 3 has_country_flag = BC_open_to_federation } }
        if = {
            limit = { country_exists = FROM has_war = no FROM = { has_war = no } }
            # A subject entity follows its constitutional parent only when that parent consents.
            if = {
                limit = { tag = BOS country_exists = SRP SRP = { is_subject_of = ROOT } }
                FROM = { annex_country = { target = SRP transfer_troops = yes } }
            }
            FROM = { annex_country = { target = ROOT transfer_troops = yes } }
        }
    }
    option = {
        name = bc_federation.1.b
        ai_chance = { factor = 30 }
        add_stability = 0.02
        if = { limit = { country_exists = FROM } FROM = { country_event = { id = bc_federation.2 days = 1 } } }
    }
}
country_event = {
    id = bc_federation.2
    title = bc_federation.2.t
    desc = bc_federation.2.d
    picture = GFX_BC_event_serbia
    is_triggered_only = yes
    option = { name = bc_federation.2.a add_political_power = 10 }
}
"""
    (MOD / "events/bc_federation.txt").write_text(federation, encoding="utf-8")
    decisions = [
        "BC_reunification = {",
        "    BC_proclaim_restoration = {",
        "        icon = BC_ser",
        "        cost = 50",
        "        visible = { NOT = { has_country_flag = BC_federation_restored } }",
        "        available = { BC_owns_all_yugoslavia = yes OR = { has_completed_focus = SER_balkan_campaign has_country_flag = BC_federal_negotiations } }",
        "        complete_effect = { BC_restore_federation = yes }",
        "        ai_will_do = { factor = 10 }",
        "    }",
    ]
    for tag in COUNTRIES:
        if tag == "SER":
            continue
        decisions += [
            f"    BC_invite_{tag} = {{",
            f"        icon = BC_{tag.lower()}",
            "        cost = 50",
            "        days_re_enable = 180",
            f"        visible = {{ has_country_flag = BC_federal_negotiations country_exists = {tag} {tag} = {{ is_subject = no }} }}",
            f"        available = {{ has_war = no {tag} = {{ has_war = no }} }}",
            f"        complete_effect = {{ {tag} = {{ country_event = {{ id = bc_federation.1 days = 1 }} }} }}",
            "        ai_will_do = { factor = 1 }",
            "    }",
        ]
    for tag in COUNTRIES:
        if tag == "SER":
            continue
        decisions += [
            f"    BC_campaign_{tag} = {{",
            "        icon = BC_army",
            "        cost = 50",
            f"        visible = {{ has_completed_focus = SER_balkan_campaign country_exists = {tag} {tag} = {{ is_subject = no }} NOT = {{ has_war_with = {tag} }} }}",
            "        available = { has_war = no }",
            f"        complete_effect = {{ declare_war_on = {{ target = {tag} type = annex_everything }} }}",
            "        ai_will_do = { factor = 1 }",
            "    }",
        ]
    decisions.append("}")
    directory = MOD / "common/decisions"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "bc_reunification.txt").write_text(
        "\n".join(decisions) + "\n", encoding="utf-8"
    )
    (directory / "categories").mkdir(exist_ok=True)
    (directory / "categories/bc_categories.txt").write_text(
        """BC_reunification = {
    icon = GFX_BC_goal_diplomacy
    allowed = { original_tag = SER }
    visible = { tag = SER has_country_flag = SER_first_breakup_wave }
}\n""",
        encoding="utf-8",
    )
    print(
        f"Rewired {sum(map(len, hooks.values()))} historical events and added consensual federation decisions."
    )


if __name__ == "__main__":
    refresh()
