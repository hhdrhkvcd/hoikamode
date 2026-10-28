import hashlib
import json

import pytest
from clausewitz import Block, parse, read, walk
from validate_mod import (
    MOD,
    ROOT,
    ValidationError,
    validate_source,
    validate_sprite_namespace,
)


def test_entire_mod_and_map_payload():
    report = validate_source(deep_images=True)
    assert report["states"] == 1483
    assert report["national_focuses"] == 400
    assert report["engine_launch_tested"] is False


@pytest.mark.parametrize("kind", ["spriteType", "corneredTileSpriteType"])
def test_vanilla_frontend_sprite_overrides_are_rejected(kind):
    # Cover both the original cornered-tile override and its 2.0.0 spriteType regression.
    doc = parse(
        f'spriteTypes = {{ {kind} = {{ name = "GFX_frontend_bg" '
        'texturefile = "gfx/interface/illustrations/bc_main_menu_background.dds" } }'
    )
    with pytest.raises(ValidationError, match="never replace vanilla UI sprites"):
        validate_sprite_namespace(doc, "unsafe_frontend.gfx")


def test_no_unconditional_mass_annexation_in_focus_rewards():
    for file in (MOD / "common/national_focus").glob("*.txt"):
        for e in walk(read(file)):
            assert e.key != "annex_country", file


def test_old_wrong_state_ids_not_used_for_balkan_claims():
    tree = read(MOD / "common/national_focus/serbia_focus_1980.txt").block("focus_tree")
    claims = {int(e.value) for e in walk(tree) if e.key == "add_state_claim"}
    assert claims == {
        102,
        103,
        104,
        105,
        109,
        163,
        736,
        785,
        848,
        849,
        850,
        851,
        900,
        1305,
        1306,
    }
    assert not claims.intersection({764, 802, 803, 804, 852, 853, 970})


def test_portraits_are_local_files_not_unresolved_generic_sprite_names():
    for file in (MOD / "history/countries").glob("*.txt"):
        for e in walk(read(file)):
            if e.key == "picture":
                assert "GFX_portrait_generic" not in e.value
                assert (MOD / e.value.strip('"')).is_file()


def test_windows_scripts_keep_utf8_bom_and_do_not_delete_game_or_settings():
    for file in list(ROOT.glob("*.ps1")) + list((ROOT / "scripts").glob("*.psm1")):
        raw = file.read_bytes()
        assert raw.startswith(b"\xef\xbb\xbf"), file
        text = raw.decode("utf-8-sig")
        assert "Remove-Item -LiteralPath $hoiData" not in text
        assert "Remove-Item -LiteralPath $paths.Data" not in text
        assert "Remove-Item -LiteralPath $documents" not in text
    installer = (ROOT / "START_BALKAN.ps1").read_text("utf-8-sig")
    assert installer.index("Read-BalkanSettings $paths.LoadFile") < installer.index(
        "$transactionStarted = $true"
    )
    assert installer.index("Expand-Archive") < installer.index(
        "$transactionStarted = $true"
    )
    assert "if ($oldModMoved)" in installer
    assert (
        "$obsoleteDefine = Join-Path $stagedMod 'common\\defines\\00_balkan_collapse.lua'"
        in installer
    )
    assert installer.index(
        "Remove-Item -LiteralPath $obsoleteDefine"
    ) < installer.index("$transactionStarted = $true")
    assert "'common\\defines\\zz_balkan_collapse.lua'" in installer
    assert "$settings.enabled_mods = @('mod/Balkan_Collapse.mod')" in installer
    assert (
        "steam://rungameid" not in installer
    )  # Do not silently reset the playset through Launcher.


def test_supplied_photograph_provenance_is_explicit():
    data = json.loads((ROOT / "assets/ARTWORK_SOURCE.json").read_text("utf-8"))
    assert "No generated or downloaded photographs" in data["method"]
    for name, sha in data["sources"].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == sha


def test_non_block_aligned_goal_and_portrait_dds_use_uncompressed_rgba():
    for folder in [MOD / "gfx/interface/goals", MOD / "gfx/leaders/BC"]:
        for file in folder.glob("*.dds"):
            assert file.read_bytes()[84:88] == b"\x00\x00\x00\x00", file


def test_only_expected_bookmarks_are_selectable():
    bookmarks = (
        read(MOD / "common/bookmarks/balkan_collapse_1980.txt")
        .block("bookmarks")
        .values("bookmark")
    )
    assert len(bookmarks) == 2
    late = bookmarks[1]
    for tag in ["SER", "CRO", "SLV", "BOS", "SRP", "MNT", "MAC", "KOS"]:
        assert isinstance(late.get(tag), Block)


def test_army_modernisation_does_not_require_already_winning_reunification():
    tree = read(MOD / "common/national_focus/serbia_focus_1980.txt").block("focus_tree")
    focus = next(
        f for f in tree.values("focus") if f.scalar("id") == "SER_army_expansion_01"
    )
    assert focus.block("prerequisite").scalar("focus") == "SER_modern_army"
