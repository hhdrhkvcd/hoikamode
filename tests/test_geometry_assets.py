"""Native geometry/flag regressions from the post-bootstrap startup log.

Synthetic rasters are tiny test fixtures, not new game artwork or geography.
"""

import json
import zipfile

import pytest
from clausewitz import read, unquote, walk
from flag_assets import validate_payload, validate_tga
from map_geometry import ProvinceRaster, prepare_buildings, repair_unitstacks
from PIL import Image
from validate_mod import MOD, ROOT


@pytest.fixture
def tiny_raster():
    image = Image.new("RGB", (6, 3))
    row = [(200, 0, 0), (0, 200, 0), (0, 200, 0), (200, 0, 0), (0, 0, 200), (0, 0, 200)]
    image.putdata(row * 3)
    definitions = {
        1: ["1", "200", "0", "0", "land", "true", "plains", "1"],
        2: ["2", "0", "0", "200", "sea", "false", "ocean", "0"],
        3: ["3", "0", "200", "0", "land", "false", "plains", "1"],
    }
    return ProvinceRaster(image, definitions)


def test_naval_spawn_is_preserved_even_though_it_is_not_a_state_building(tiny_raster):
    source = "1;arms_factory;1.5;10;1.5;0;0\n1;naval_base_spawn;3.5;9.5;1.5;0;2\n"
    text, ports, repairs = prepare_buildings(
        source, {"arms_factory"}, tiny_raster, {1: 1, 3: 1}
    )
    assert ";naval_base_spawn;" in text
    assert ports == [[2, 1]]
    assert text.splitlines()[1].split(";")[-1] == "2"  # SEA id, not the land province.
    assert not text.endswith("\n")
    assert not any(repairs.values())


def test_old_state_building_only_filter_would_be_rejected_for_missing_ports(
    tiny_raster,
):
    with pytest.raises(ValueError, match="every coastal province"):
        prepare_buildings(
            "1;arms_factory;1.5;10;1.5;0;0", {"arms_factory"}, tiny_raster, {1: 1, 3: 1}
        )


def test_port_must_target_an_adjacent_sea_not_a_land_province(tiny_raster):
    with pytest.raises(ValueError, match="shoreline"):
        prepare_buildings(
            "1;naval_base_spawn;3.5;9.5;1.5;0;3", set(), tiny_raster, {1: 1, 3: 1}
        )


def test_floating_harbor_uses_land_target_and_its_current_state(tiny_raster):
    text, ports, repairs = prepare_buildings(
        "1;naval_base_spawn;3.5;9.5;1.5;0;2\n"
        "99;floating_harbor;4.5;9.5;1.5;0;1\n"
        "1;floating_harbor;4.5;9.5;1.5;0;1\n"
        "1;floating_harbor;1.5;9.5;1.5;0;3",
        set(),
        tiny_raster,
        {1: 1, 3: 1},
    )
    assert text.splitlines()[1].startswith("1;floating_harbor;")
    assert len(text.splitlines()) == 2
    assert ports == [[1, 1]]
    assert repairs == {
        "floating_harbor_state_repairs": 1,
        "removed_inland_floating_harbors": 1,
        "removed_duplicate_floating_harbors": 1,
    }


@pytest.mark.parametrize("with_anchor", [False, True])
def test_off_map_victory_point_stack_is_repaired_inside_its_province(
    tiny_raster, with_anchor
):
    source = "3;38;311.06;0;-1000.41;0;1\n"
    if with_anchor:
        source = "3;0;1.5;12.3;1.5;0;1\n" + source
    content, repairs = repair_unitstacks(source, tiny_raster)
    row = content.decode().splitlines()[-1].split(";")
    assert tiny_raster.province_at(float(row[2]), float(row[4])) == 3
    if with_anchor:
        assert float(row[3]) == 12.3
    assert repairs == [[3, 38]]


def test_full_map_has_native_markers_and_no_terminal_empty_record():
    metadata = json.loads((ROOT / "assets/MAP_SOURCE.json").read_text("utf-8"))
    content = (MOD / "map/buildings.txt").read_bytes()
    assert not content.endswith(b"\n")
    kinds = [line.split(";")[1] for line in content.decode().splitlines()]
    assert kinds.count("naval_base_spawn") == 2496
    assert kinds.count("supply_node") == 11724
    assert kinds.count("special_project_facility_spawn") == 11724
    assert kinds.count("nuclear_reactor_spawn") == 1493
    assert kinds.count("rocket_site_spawn") == 1493
    assert len(metadata["geometry"]["repaired_unitstacks"]) == 10
    assert len(metadata["geometry"]["ports"]) == 2496
    state = read(MOD / "history/states/169-BC.txt").block("state")
    assert state.block("history").block("buildings").get("dockyard") is None


def test_compatibility_payload_fixes_missing_flags_and_indexed_csa_overlay():
    manifest = validate_payload()
    assert len(manifest["payload_files"]) == 5328
    with zipfile.ZipFile(ROOT / "assets/compatibility_flags.zip") as archive:
        for name in [
            "gfx/flags/A24.tga",
            "gfx/flags/small/XIN_neutrality.tga",
            "gfx/flags/CSA_neutrality.tga",
        ]:
            content = archive.read(name)
            validate_tga(content, name)
            assert content[16] == 32
    assert not set(manifest["fallback_tags"]) & {
        "SER",
        "CRO",
        "BOS",
        "SRP",
        "SLV",
        "KOS",
        "MAC",
        "MNT",
        "USA",
        "FRA",
        "GER",
    }


@pytest.mark.parametrize("depth", [8, 24])
def test_shipped_flags_cannot_use_indexed_or_legacy_depth(depth):
    content = bytearray((MOD / "gfx/flags/SER.tga").read_bytes())
    content[16] = depth
    with pytest.raises(ValueError, match="32-bpp"):
        validate_tga(bytes(content), "gfx/flags/SER.tga")


def test_base_character_prototypes_remain_but_old_national_ai_does_not():
    descriptor = read(MOD / "descriptor.mod")
    replace_paths = {unquote(p) for p in descriptor.values("replace_path")}
    assert "common/characters" not in replace_paths
    assert {
        "common/ai_strategy",
        "common/ai_strategy_plans",
        "common/decisions/categories",
    } <= replace_paths
    for path in (MOD / "history/countries").glob("*.txt"):
        assert not any(e.key == "recruit_character" for e in walk(read(path)))
