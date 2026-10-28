import pytest
from clausewitz import read
from scenario_model import Model
from validate_mod import MOD


def test_1980_is_one_federation_with_tito():
    game = Model()
    assert set(game.union_owners().values()) == {"SER"}
    assert game.countries["SER"]["leaders"]["stalinism"] == "Josip Broz Tito"
    assert game.countries["SER"]["party"] == "communism"
    assert game.countries["SER"]["cosmetic"] == "BC_YUGOSLAVIA"
    assert not any(
        game.exists(t) for t in ["CRO", "SLV", "BOS", "MNT", "KOS", "MAC", "SRP"]
    )


def test_tito_dies_on_4_may_and_vucic_succeeds_him():
    game = Model()
    game.advance("1980.5.3")
    assert "SER_tito_dead" not in game.countries["SER"]["flags"]
    game.advance("1980.5.4")
    assert game.fired["serbia_collapse.1"] == 1
    assert game.countries["SER"]["leaders"]["conservatism"] == "Aleksandar Vučić"
    assert "stalinism" not in game.countries["SER"]["leaders"]
    assert game.countries["SER"]["party"] == "democratic"
    assert set(game.union_owners().values()) == {"SER"}


def test_unanswered_popup_is_not_queued_every_day():
    game = Model(auto_resolve=False)
    game.advance("1980.6.1")
    assert game.fired["serbia_collapse.1"] == 1
    assert len(game.pending) == 1


@pytest.fixture(scope="module")
def complete_timeline():
    game = Model()
    milestones = {}
    for when in [
        "1991.6.25",
        "1991.9.25",
        "1992.1.9",
        "1992.3.3",
        "1992.4.27",
        "1995.12.14",
        "2006.6.3",
        "2008.2.17",
    ]:
        game.advance(when)
        milestones[when] = dict(game.union_owners())
    return game, milestones


@pytest.mark.parametrize(
    "tag,when",
    [
        ("CRO", "1991.6.25"),
        ("SLV", "1991.6.25"),
        ("MAC", "1991.9.25"),
        ("SRP", "1992.1.9"),
        ("BOS", "1992.3.3"),
        ("MNT", "2006.6.3"),
        ("KOS", "2008.2.17"),
    ],
)
def test_republics_receive_the_new_map_states(complete_timeline, tag, when):
    game, snapshots = complete_timeline
    ids = game.config["countries"][tag].get(
        "release_states", game.config["countries"][tag]["states"]
    )
    if tag == "BOS":
        ids = [104, 851]
    assert all(snapshots[when][i] == tag for i in ids)
    assert game.loaded_armies[tag] == 1


def test_1992_transition_does_not_replace_vucic(complete_timeline):
    game, _ = complete_timeline
    assert game.countries["SER"]["leaders"]["conservatism"] == "Aleksandar Vučić"
    assert "Ana Brnabić" not in game.countries["SER"]["leaders"].values()
    assert all(n == 1 for n in game.fired.values())
    assert len(game.fired) == 21


def test_dayton_restores_peace_and_entity_relationship(complete_timeline):
    game, snapshots = complete_timeline
    assert game.countries["SRP"]["subject_of"] == "BOS"
    assert snapshots["1995.12.14"][850] == "BOS"
    assert frozenset(["SRP", "BOS"]) not in game.wars
    assert frozenset(["SER", "CRO"]) not in game.wars
    assert frozenset(["SER", "SLV"]) not in game.wars


def test_2008_history_matches_a_played_through_collapse(complete_timeline):
    game, _ = complete_timeline
    quick = Model("2008.2.18")
    assert quick.union_owners() == game.union_owners()
    assert quick.countries["SER"]["leaders"]["conservatism"] == "Aleksandar Vučić"
    assert quick.countries["SRP"]["subject_of"] == "BOS"
    assert all(quick.exists(t) for t in quick.config["countries"])
    quick.advance("2008.3.18")
    assert not quick.fired  # Old milestones must not replay on a late start.


def test_rejection_preserves_sovereignty():
    game = Model("2008.2.18")
    old = game.union_owners()
    game.fire("bc_federation.1", "CRO", "SER", choice=1)
    assert game.union_owners() == old
    assert game.exists("CRO")


def test_acceptance_annexes_only_the_consenting_country():
    game = Model("2008.2.18")
    old_bosnia = game.states[104]["owner"]
    game.fire("bc_federation.1", "CRO", "SER", choice=0)
    assert not game.exists("CRO")
    assert game.states[104]["owner"] == old_bosnia
    assert all(
        game.states[i]["owner"] == "SER"
        for i in game.config["countries"]["CRO"]["states"]
    )


def test_war_prevents_a_pending_peaceful_annexation():
    game = Model("2008.2.18")
    game.wars.add(frozenset(["CRO", "SER"]))
    game.fire("bc_federation.1", "CRO", "SER", choice=0)
    assert game.exists("CRO")


def test_bosnian_entity_follows_consenting_parent():
    game = Model("2008.2.18")
    game.fire("bc_federation.1", "BOS", "SER", choice=0)
    assert not game.exists("BOS") and not game.exists("SRP")
    assert game.states[848]["owner"] == "SER"


def test_restoration_stops_future_forced_secessions():
    game = Model()
    game.advance("1995.12.15")
    for i in game.union_owners():
        game.states[i]["owner"] = game.states[i]["controller"] = "SER"
    game.exec(game.effects["BC_restore_federation"], "SER", "SER")
    game.advance("2008.3.1")
    assert not game.exists("MNT") and not game.exists("KOS")
    assert all("SER" in game.states[i]["cores"] for i in game.union_owners())
    assert game.countries["SER"]["cosmetic"] == "BC_RESTORED_YUGOSLAVIA"


def test_restoration_requires_ownership_and_control_of_every_state():
    game = Model("2008.2.18")
    for i in game.union_owners():
        game.states[i]["owner"] = game.states[i]["controller"] = "SER"
    trigger = game.triggers["BC_owns_all_yugoslavia"]
    assert game.eval(trigger, "SER", "SER")
    game.states[1305]["controller"] = "KOS"
    assert not game.eval(trigger, "SER", "SER")


def test_military_focus_does_not_automatically_start_seven_wars():
    tree = read(MOD / "common/national_focus/serbia_focus_1980.txt").block("focus_tree")
    campaign = next(
        f for f in tree.values("focus") if f.scalar("id") == "SER_balkan_campaign"
    )
    assert "declare_war_on" not in str(campaign.block("completion_reward"))
    assert "create_wargoal" in str(campaign.block("completion_reward"))
