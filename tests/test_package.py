import pytest
from build_mod import build
from validate_mod import MOD, ROOT, ValidationError, validate_package


def test_release_archive_matches_sources_and_expands_the_map():
    report = validate_package(ROOT / "Balkan_Collapse_1980.zip")
    assert report["files"] > 2400
    assert report["bytes"] < 100 * 1024 * 1024


@pytest.mark.parametrize(
    "output",
    [
        ROOT / "assets/millennium_map.zip",
        ROOT / "assets/compatibility_flags.zip",
        ROOT / "Balkan_Collapse_RECOVERY_V3.zip",
        MOD / "nested.zip",
        ROOT / ".git/bad.zip",
    ],
)
def test_builder_cannot_overwrite_source_assets_or_build_into_protected_folders(output):
    with pytest.raises(ValidationError):
        build(output)
