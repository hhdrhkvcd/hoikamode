"""A deliberately limited state/flag test model, not an HOI4 interpreter.

Exercises only the ownership, queue, leader and consent logic used by this mod.
It cannot prove that the game recognises an effect or that the game will launch.
"""

import re
from collections import Counter, defaultdict
from datetime import date, timedelta

from clausewitz import Block, Entry, unquote
from validate_mod import DATE, initial_state_history, source_data


class Model:
    def __init__(self, start="1980.5.1", *, auto_resolve=True):
        self.config, self.parsed, raw_states, self.definitions = source_data()
        self.date = self.to_date(start)
        self.states = {
            i: initial_state_history(s, start) for i, s in raw_states.items()
        }
        self.countries = defaultdict(
            lambda: {
                "flags": set(),
                "leaders": {},
                "party": None,
                "cosmetic": None,
                "subject_of": None,
                "oob": None,
            }
        )
        self.global_flags = set()
        self.wars = set()
        self.loaded_armies = Counter()
        self.fired = Counter()
        self.pending = []
        self.delayed = []
        self.auto_resolve = auto_resolve
        self.effects = {}
        self.triggers = {}
        self.events = {}
        for path, doc in self.parsed.items():
            if path.startswith("common/scripted_effects/"):
                self.effects.update({e.key: e.value for e in doc.entries()})
            if path.startswith("common/scripted_triggers/"):
                self.triggers.update({e.key: e.value for e in doc.entries()})
            if path.startswith("events/"):
                self.events.update(
                    {e.scalar("id"): e for e in doc.values("country_event")}
                )
        # All state histories are evaluated before country setup in this test model.
        for path, doc in sorted(self.parsed.items()):
            if path.startswith("history/countries/"):
                tag = path.split("/")[-1][:3]
                self.exec(
                    Block(
                        [
                            e
                            for e in doc.items
                            if not isinstance(e, Entry) or not DATE.fullmatch(e.key)
                        ]
                    ),
                    tag,
                    tag,
                )
                dated = [e for e in doc.entries() if DATE.fullmatch(e.key)]
                for entry in sorted(dated, key=lambda e: self.to_date(e.key)):
                    if self.to_date(entry.key) <= self.date:
                        self.exec(entry.value, tag, tag)
        self.hooks = self.parsed["common/on_actions/bc_timeline.txt"].block(
            "on_actions"
        )
        self.exec(self.hooks.block("on_startup").block("effect"), None, None)

    @staticmethod
    def to_date(value):
        return date(*map(int, value.split(".")[:3]))

    def exists(self, tag):
        return any(s["owner"] == tag for s in self.states.values())

    def resolve(self, tag, root, from_tag):
        return {"ROOT": root, "FROM": from_tag}.get(tag, unquote(tag))

    def eval(self, block, scope, root, from_tag=None, *, any_=False):
        answers = []
        for e in block.entries():
            key, value = e.key, e.value
            if key == "AND":
                answer = self.eval(value, scope, root, from_tag)
            elif key == "OR":
                answer = self.eval(value, scope, root, from_tag, any_=True)
            elif key == "NOT":
                answer = not self.eval(value, scope, root, from_tag)
            elif key in self.triggers:
                answer = self.eval(self.triggers[key], scope, root, from_tag) == (
                    value == "yes"
                )
            elif isinstance(value, Block) and (
                key in self.countries
                or key in ["SER", "BOS", "SRP", "MAC", "ROOT", "FROM"]
                or key.isdigit()
            ):
                target = (
                    int(key) if key.isdigit() else self.resolve(key, root, from_tag)
                )
                answer = self.eval(value, target, root, from_tag)
            elif key == "date":
                other = self.to_date(unquote(value))
                answer = {
                    ">": self.date > other,
                    "<": self.date < other,
                    "=": self.date == other,
                    ">=": self.date >= other,
                    "<=": self.date <= other,
                }[e.op]
            elif key in ["tag", "original_tag"]:
                answer = scope == self.resolve(value, root, from_tag)
            elif key == "country_exists":
                answer = self.exists(self.resolve(value, root, from_tag))
            elif key == "exists":
                assert value in ["yes", "no"], (
                    "exists takes yes/no; use country_exists for a tag"
                )
                answer = self.exists(scope) == (value == "yes")
            elif key == "has_country_flag":
                answer = value in self.countries[scope]["flags"]
            elif key == "has_global_flag":
                answer = value in self.global_flags
            elif key == "has_war":
                answer = any(scope in pair for pair in self.wars) == (value == "yes")
            elif key == "has_war_with":
                answer = (
                    frozenset([scope, self.resolve(value, root, from_tag)]) in self.wars
                )
            elif key == "is_subject":
                answer = bool(self.countries[scope]["subject_of"]) == (value == "yes")
            elif key == "is_subject_of":
                answer = self.countries[scope]["subject_of"] == self.resolve(
                    value, root, from_tag
                )
            elif key == "is_owned_by":
                answer = self.states[scope]["owner"] == self.resolve(
                    value, root, from_tag
                )
            elif key in ["owns_state", "controls_state"]:
                field = "owner" if key == "owns_state" else "controller"
                answer = self.states[int(value)][field] == scope
            elif key == "always":
                answer = value == "yes"
            else:
                raise AssertionError(f"Unmodelled trigger {key}")
            answers.append(answer)
        return any(answers) if any_ else all(answers)

    def exec(self, block, scope, root, from_tag=None):
        for e in block.entries():
            key, value = e.key, e.value
            if key == "if":
                if self.eval(value.block("limit"), scope, root, from_tag):
                    self.exec(
                        Block([x for x in value.entries() if x.key != "limit"]),
                        scope,
                        root,
                        from_tag,
                    )
            elif key in self.effects:
                self.exec(self.effects[key], scope, root, from_tag)
            elif (
                key in ["ROOT", "FROM"]
                or key in self.countries
                or re.fullmatch(r"[A-Z0-9]{3}", key)
                or key.isdigit()
            ):
                target = (
                    int(key) if key.isdigit() else self.resolve(key, root, from_tag)
                )
                self.exec(value, target, root, from_tag)
            elif key == "set_country_flag":
                self.countries[scope]["flags"].add(value)
            elif key == "clr_country_flag":
                self.countries[scope]["flags"].discard(value)
            elif key == "set_global_flag":
                self.global_flags.add(value)
            elif key == "set_politics":
                self.countries[scope]["party"] = value.scalar("ruling_party")
            elif key == "create_country_leader":
                self.countries[scope]["leaders"][value.scalar("ideology")] = (
                    value.scalar("name")
                )
            elif key == "kill_country_leader":
                if self.countries[scope]["party"] == "communism":
                    self.countries[scope]["leaders"].pop("stalinism", None)
            elif key == "set_cosmetic_tag":
                self.countries[scope]["cosmetic"] = value
            elif key == "release":
                for state in self.states.values():
                    if state["owner"] == scope and value in state["cores"]:
                        state["owner"] = state["controller"] = value
            elif key in ["add_core_of", "remove_core_of"]:
                if key == "add_core_of":
                    self.states[scope]["cores"].add(value)
                else:
                    self.states[scope]["cores"].discard(value)
            elif key == "transfer_state":
                self.states[int(value)]["owner"] = self.states[int(value)][
                    "controller"
                ] = scope
            elif key == "puppet":
                self.countries[value]["subject_of"] = scope
            elif key == "oob":
                self.countries[scope]["oob"] = unquote(value)
            elif key == "load_oob":
                self.loaded_armies[scope] += 1
            elif key == "declare_war_on":
                self.wars.add(frozenset([scope, value.scalar("target")]))
            elif key == "white_peace":
                self.wars.discard(frozenset([scope, value]))
            elif key == "annex_country":
                target = self.resolve(value.scalar("target"), root, from_tag)
                for state in self.states.values():
                    if state["owner"] == target:
                        state["owner"] = state["controller"] = scope
                self.countries[target]["subject_of"] = None
            elif key == "country_event":
                event_id = value.scalar("id")
                days = int(value.scalar("days", "0"))
                if days:
                    self.delayed.append(
                        (self.date + timedelta(days=days), event_id, scope, root)
                    )
                else:
                    self.fire(event_id, scope, root)
            else:
                # The model intentionally ignores economic, technology and display effects.
                pass

    def fire(self, event_id, target, from_tag=None, choice=0):
        self.fired[event_id] += 1
        if not self.auto_resolve:
            self.pending.append((event_id, target, from_tag))
            return
        event = self.events[event_id]
        self.exec(event.values("option")[choice], target, target, from_tag)

    def advance(self, until):
        until = self.to_date(until)
        while self.date < until:
            self.date += timedelta(days=1)
            due = [v for v in self.delayed if v[0] <= self.date]
            self.delayed = [v for v in self.delayed if v[0] > self.date]
            for _, event_id, tag, from_tag in due:
                self.fire(event_id, tag, from_tag)
            for tag in ["SER", "MAC", "SRP"]:
                if self.exists(tag):
                    self.exec(
                        self.hooks.block("on_daily_" + tag).block("effect"), tag, tag
                    )

    def union_owners(self):
        states = {
            s
            for tag, c in self.config["countries"].items()
            if tag != "SRP"
            for s in c["states"]
        }
        return {s: self.states[s]["owner"] for s in sorted(states)}
