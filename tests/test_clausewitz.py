import pytest
from clausewitz import ParseError, Tagged, dumps, parse


def test_duplicate_keys_comments_quotes_and_comparisons_survive_round_trip():
    text = """# A hash in quotes must not start a comment.
state = { id = 104 name = "Bosnia # 1" history = { add_core_of = BOS add_core_of = SRP } date > 1980.5.3 }
"""
    doc = parse(text)
    s = doc.block("state")
    assert s.block("history").values("add_core_of") == ["BOS", "SRP"]
    assert s.scalar("name") == "Bosnia # 1"
    assert parse(dumps(doc)) == doc


def test_tagged_colour_and_empty_blocks():
    doc = parse("color = rgb { 20 40 60 } empty = { }")
    assert isinstance(doc.get("color"), Tagged)
    assert doc.get("color").block.atoms() == ["20", "40", "60"]
    assert not doc.block("empty").items
    assert parse(dumps(doc)) == doc


@pytest.mark.parametrize(
    "text", ["x = {", "x = }", "}", 'x = "unclosed', "= x", "x = { y = }"]
)
def test_malformed_input_is_rejected(text):
    with pytest.raises(ParseError):
        parse(text)


def test_set_does_not_accumulate_duplicate_assignments():
    doc = parse("x = 1 x = 2")
    doc.set("x", "3")
    assert doc.values("x") == ["3"]
