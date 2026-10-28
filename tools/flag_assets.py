"""Small source payload for flags absent from the supplied map/vanilla 1.19.4.

Missing-country flags are explicitly neutral technical placeholders sampled from
an existing supplied image. They are NOT new national artwork or real flags.
"""

from __future__ import annotations

import hashlib
import json
import re
import struct
import zipfile
from io import BytesIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SIZES = {"": (82, 52), "medium": (41, 26), "small": (10, 7)}
SUFFIXES = ["", "_democratic", "_neutrality", "_communism", "_fascism"]
PAYLOAD = ROOT / "assets/compatibility_flags.zip"
MANIFEST = ROOT / "assets/FLAGS_SOURCE.json"


def expected_members(config):
    names = set()
    for tag in config["fallback_tags"]:
        if not re.fullmatch(r"[A-Z0-9]{3}", tag):
            raise ValueError("Invalid compatibility flag tag")
        for suffix in SUFFIXES:
            for folder in SIZES:
                names.add(
                    "/".join(
                        p for p in ["gfx/flags", folder, tag + suffix + ".tga"] if p
                    )
                )
    for tag, ideologies in config["overlay_patches"].items():
        if not re.fullmatch(r"[A-Z0-9]{3}", tag) or not set(ideologies) <= {
            "democratic",
            "neutrality",
            "communism",
            "fascism",
        }:
            raise ValueError("Invalid flag overlay specification")
        for ideology in ideologies:
            for folder in SIZES:
                names.add(
                    "/".join(
                        p for p in ["gfx/flags", folder, f"{tag}_{ideology}.tga"] if p
                    )
                )
    return names


def prepare():
    from PIL import Image

    config = json.loads((ROOT / "data/flag_compatibility.json").read_text("utf-8"))
    source = (
        ROOT / "Balkan_Collapse/gfx/interface/illustrations/bc_main_menu_background.dds"
    )
    pixel = (
        Image.open(source)
        .crop(tuple(config["source_crop"]))
        .convert("RGB")
        .convert("RGBA")
    )
    templates = {}
    for folder, size in SIZES.items():
        out = BytesIO()
        pixel.resize(size).save(out, format="TGA", compression=None)
        templates[folder] = out.getvalue()
    files = {}
    PAYLOAD.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(
        PAYLOAD, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as archive:
        for name in sorted(expected_members(config)):
            if (ROOT / "Balkan_Collapse" / name).exists():
                raise ValueError(f"Do not overwrite supplied local flags: {name}")
            folder = Path(name).parent.name
            folder = folder if folder in ["small", "medium"] else ""
            content = templates[folder]
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 28, 0, 0, 0))
            info.external_attr = 0o100644 << 16
            archive.writestr(
                info, content, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9
            )
            files[name] = hashlib.sha256(content).hexdigest()
    manifest = {
        "payload": PAYLOAD.relative_to(ROOT).as_posix(),
        "payload_sha256": hashlib.sha256(PAYLOAD.read_bytes()).hexdigest(),
        "source": source.relative_to(ROOT).as_posix(),
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "crop": config["source_crop"],
        "note": "Neutral technical placeholders only, sampled from supplied artwork. Not authentic national flags. Existing Balkan and native flags are retained.",
        "observed_engine": config["observed_engine"],
        "fallback_tags": config["fallback_tags"],
        "overlay_patches": config["overlay_patches"],
        "payload_files": files,
    }
    MANIFEST.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"Prepared {len(files)} 32-bpp compatibility flag files in compressed source payload."
    )


def validate_tga(content, name):
    if len(content) < 18 or content[2] != 2 or content[16] != 32:
        raise ValueError(f"{name}: expected uncompressed 32-bpp true-color TGA")
    folder = Path(name).parent.name
    size = SIZES.get(folder, SIZES[""])
    if struct.unpack_from("<HH", content, 12) != size:
        raise ValueError(f"{name}: unexpected flag dimensions")
    if len(content) < 18 + content[0] + size[0] * size[1] * 4:
        raise ValueError(f"{name}: truncated flag pixels")


def validate_payload():
    manifest = json.loads(MANIFEST.read_text("utf-8"))
    config = json.loads((ROOT / "data/flag_compatibility.json").read_text("utf-8"))
    if hashlib.sha256(PAYLOAD.read_bytes()).hexdigest() != manifest["payload_sha256"]:
        raise ValueError("Compatibility flag payload checksum mismatch")
    if (
        hashlib.sha256((ROOT / manifest["source"]).read_bytes()).hexdigest()
        != manifest["source_sha256"]
    ):
        raise ValueError("Compatibility flag source image changed")
    expected = expected_members(config)
    with zipfile.ZipFile(PAYLOAD) as archive:
        if (
            len(archive.namelist()) != len(expected)
            or set(archive.namelist()) != expected
            or set(manifest["payload_files"]) != expected
        ):
            raise ValueError("Compatibility flag inventory mismatch")
        for name in sorted(expected):
            content = archive.read(name)
            validate_tga(content, name)
            if hashlib.sha256(content).hexdigest() != manifest["payload_files"][name]:
                raise ValueError(f"Compatibility flag hash mismatch: {name}")
    return manifest


if __name__ == "__main__":
    prepare()
