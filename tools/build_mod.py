#!/usr/bin/env python3
"""Build the ready-to-install ZIP, expanding the compressed map payload.

No RAR tool, full Millennium Dawn installation or third-party Python packages
are needed to build from this repository. Raw BMPs are not duplicated in Git.
"""

from __future__ import annotations

import argparse
import hashlib
import tempfile
import zipfile
from contextlib import ExitStack
from pathlib import Path

from validate_mod import MOD, ROOT, require, validate_package, validate_source

LAUNCHERS = [
    "START_BALKAN",
    "START_VANILLA",
    "RESTORE_PREVIOUS_MODS",
    "COLLECT_BALKAN_LOGS",
    "CHECK_INSTALL",
]


def build(output: Path):
    output = output.resolve()
    require(output.suffix.lower() == ".zip", "Output must be a .zip file")
    require(
        output
        not in [
            ROOT / "assets/millennium_map.zip",
            ROOT / "assets/compatibility_flags.zip",
            ROOT / "Balkan_Collapse_RECOVERY_V3.zip",
        ],
        "Cannot overwrite a source archive",
    )
    require(not output.is_relative_to(ROOT / ".git"), "Cannot build inside .git")
    require(
        not output.is_relative_to(MOD), "Cannot build the archive inside the mod folder"
    )
    validate_source()
    output.parent.mkdir(parents=True, exist_ok=True)
    entries = {}
    for file in MOD.rglob("*"):
        if file.is_file() and not any(p in ["__pycache__", ".git"] for p in file.parts):
            entries["Balkan_Collapse/" + file.relative_to(MOD).as_posix()] = file
    for launcher in LAUNCHERS:
        for ext in ["bat", "ps1"]:
            file = ROOT / f"{launcher}.{ext}"
            entries[file.name] = file
    for name in ["Balkan_Collapse.mod", "README.md", "NOTICE.md"]:
        entries[name] = ROOT / name
    for folder in ["scripts", "docs"]:
        for file in (ROOT / folder).rglob("*"):
            if file.is_file():
                entries[file.relative_to(ROOT).as_posix()] = file
    for name in ["MAP_SOURCE.json", "ARTWORK_SOURCE.json", "FLAGS_SOURCE.json"]:
        entries["assets/" + name] = ROOT / "assets" / name
    with ExitStack() as stack:
        for payload_name in ["millennium_map.zip", "compatibility_flags.zip"]:
            source = stack.enter_context(
                zipfile.ZipFile(ROOT / "assets" / payload_name)
            )
            for file in source.namelist():
                name = "Balkan_Collapse/" + file
                if name in entries:
                    require(
                        entries[name].read_bytes() == source.read(file),
                        f"Local asset differs from source payload: {file}",
                    )
                entries[name] = (source, file)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(
                prefix=".bc-package-", suffix=".zip", dir=output.parent, delete=False
            ) as stream:
                temporary = Path(stream.name)
            with zipfile.ZipFile(
                temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
            ) as archive:
                for name, file in sorted(entries.items()):
                    content = (
                        file[0].read(file[1])
                        if isinstance(file, tuple)
                        else file.read_bytes()
                    )
                    info = zipfile.ZipInfo(name, date_time=(2026, 10, 28, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    info.external_attr = 0o100644 << 16
                    archive.writestr(
                        info,
                        content,
                        compress_type=zipfile.ZIP_DEFLATED,
                        compresslevel=9,
                    )
            validate_package(temporary)
            temporary.replace(output)
        finally:
            if temporary and temporary.exists():
                temporary.unlink()
    sha = hashlib.sha256(output.read_bytes()).hexdigest()
    print(
        f"Built {output.name}: {len(entries)} files, {output.stat().st_size / 1024**2:.1f} MiB"
    )
    print(f"SHA256 {sha}")
    print(
        "Offline validation passed. Windows/HOI4 launch is NOT tested by this builder."
    )
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, default=ROOT / "Balkan_Collapse_1980.zip"
    )
    build(parser.parse_args().output)
