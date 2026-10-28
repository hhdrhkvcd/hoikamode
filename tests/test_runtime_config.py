"""Regression checks from the uploaded 1.19.4 startup errors.

The Lua bootstrap below is synthetic test data, NOT the game's defines or an
HOI4 emulator. It checks ordering and preservation of an existing Lua table.
No original crash logs, personal paths or hardware details are stored here.
"""

import json

import pytest
from clausewitz import parse
from lupa.lua51 import LuaError, LuaRuntime
from scenario_model import Model
from validate_mod import MOD, ROOT, ValidationError, validate_country_existence_triggers

BASE_DEFINES = """
NDefines = {
    NGame = {
        START_DATE = "1936.1.1.12", END_DATE = "1949.1.1.1",
        OIL_RESOURCE = "oil", FUEL_RESOURCE = "fuel", ENERGY_RESOURCE = "coal"
    },
    NDiplomacy = { TENSION_TIME_SCALE_START_DATE = "1936.1.1.12", BASE_SENTINEL = 41 },
    NProject = { SPEEDS = { 0, 0.1, 0.2 }, THRESHOLDS = { 10, 20 } }
}
original_defines = NDefines
original_game = NDefines.NGame
"""
BASE_GRAPHICS = """
NDefines.NGraphics = { BORDER_COLOR_CUSTOM_HIGHLIGHTS = { 1, 0.5, 0.2, 1 } }
"""


def load_lua_in_filename_order(override_name):
    lua = LuaRuntime(register_eval=False, register_builtins=False)
    scripts = {
        "00_defines.lua": BASE_DEFINES,
        "00_graphics.lua": BASE_GRAPHICS,
        override_name: (MOD / "common/defines/zz_balkan_collapse.lua").read_text(
            "utf-8"
        ),
    }
    for _, script in sorted(scripts.items()):
        lua.execute(script)
    return lua


def test_early_filename_reproduces_the_uploaded_ndefines_nil_error():
    with pytest.raises(LuaError, match="NDefines"):
        load_lua_in_filename_order("00_balkan_collapse.lua")


def test_late_filename_keeps_base_defines_and_overrides_only_scenario_dates():
    lua = load_lua_in_filename_order("zz_balkan_collapse.lua")
    data = json.loads((ROOT / "data/balkans.json").read_text("utf-8"))
    assert lua.eval("rawequal(NDefines, original_defines)")
    assert lua.eval("rawequal(NDefines.NGame, original_game)")
    assert lua.eval("NDefines.NGame.START_DATE") == data["start_date"]
    assert lua.eval("NDefines.NGame.END_DATE") == data["end_date"]
    assert (
        lua.eval("NDefines.NDiplomacy.TENSION_TIME_SCALE_START_DATE")
        == data["start_date"]
    )
    assert lua.eval("NDefines.NGame.OIL_RESOURCE") == "oil"
    assert lua.eval("NDefines.NGame.FUEL_RESOURCE") == "fuel"
    assert lua.eval("NDefines.NGame.ENERGY_RESOURCE") == "coal"
    assert lua.eval("NDefines.NDiplomacy.BASE_SENTINEL") == 41
    assert lua.eval("#NDefines.NGraphics.BORDER_COLOR_CUSTOM_HIGHLIGHTS") == 4
    assert lua.eval("#NDefines.NProject.SPEEDS == #NDefines.NProject.THRESHOLDS + 1")


def test_source_contains_no_obsolete_early_lua_override():
    assert sorted(p.name for p in (MOD / "common/defines").glob("*.lua")) == [
        "zz_balkan_collapse.lua"
    ]


@pytest.mark.parametrize("target", ["CRO", "BOS", "FROM"])
def test_exists_cannot_take_a_country_tag_or_scope_reference(target):
    with pytest.raises(ValidationError, match="exists expects yes/no"):
        validate_country_existence_triggers(
            parse(f"exists = {target}"), {"SER", "CRO", "BOS"}
        )


def test_country_exists_and_scoped_boolean_exists_have_distinct_valid_syntax():
    validate_country_existence_triggers(
        parse(
            "country_exists = CRO CRO = { exists = yes } NOT = { country_exists = FROM }"
        ),
        {"SER", "CRO"},
    )
    with pytest.raises(ValidationError, match="unknown country_exists target"):
        validate_country_existence_triggers(
            parse("country_exists = ZZY"), {"SER", "CRO"}
        )


def test_timeline_model_no_longer_silently_accepts_the_rejected_exists_syntax():
    game = Model()
    assert game.eval(parse("country_exists = SER exists = yes"), "SER", "SER")
    assert not game.eval(parse("country_exists = CRO"), "SER", "SER")
    with pytest.raises(AssertionError, match="use country_exists"):
        game.eval(parse("exists = CRO"), "SER", "SER")
