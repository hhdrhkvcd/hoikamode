#!/usr/bin/env python3
"""Crop/re-encode supplied artwork only. No image model or downloaded photographs.

Requires Pillow. Source DDS files already shipped in Balkan_Collapse are retained.
Leader photo placeholders show a flag, NOT a fabricated photograph of a politician.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageOps

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / "Balkan_Collapse"
COUNTRIES = json.loads((ROOT / "data/balkans.json").read_text("utf-8"))["countries"]


def save_dds(image, relative):
    p = MOD / relative
    p.parent.mkdir(parents=True, exist_ok=True)
    # Legacy DirectX paths are stricter about BC-compressed dimensions.
    # Keep 95x95 goals and 156x210 portraits as ordinary RGBA DDS.
    options = (
        {"pixel_format": "DXT5"} if image.width % 4 == image.height % 4 == 0 else {}
    )
    image.convert("RGBA").save(p, **options)


def fit(image, box, size):
    return ImageOps.fit(
        image.crop(box).convert("RGB"), size, method=Image.Resampling.LANCZOS
    )


def prepare():
    tito_src = MOD / "gfx/loadingscreens/load_1.dds"
    city_src = MOD / "gfx/interface/illustrations/bc_main_menu_background.dds"
    serbia_src = MOD / "gfx/interface/illustrations/bc_serbia_background.dds"
    tito = Image.open(tito_src).convert("RGB")
    city = Image.open(city_src).convert("RGB")
    serbia = Image.open(serbia_src).convert("RGB")
    # Retain the supplied tank illustration, not a deleted legacy installation archive.
    crisis_src = ROOT / "assets/source/bc_supplied_crisis.png"
    crisis = Image.open(crisis_src).convert("RGB")
    crops = {
        "tito": (tito, (270, 15, 900, 845)),
        "government": (tito, (1050, 100, 1750, 570)),
        "economy": (city, (30, 150, 900, 700)),
        "transport": (city, (400, 260, 1420, 690)),
        "diplomacy": (serbia, (650, 30, 1450, 720)),
        "research": (city, (650, 320, 1350, 980)),
        "reconstruction": (tito, (1550, 620, 1920, 900)),
        "army": (crisis, (115, 278, 455, 444)),
    }
    tiles = {}
    for name, (source, box) in crops.items():
        tile = fit(source, box, (95, 95)).convert("RGBA")
        tile = ImageEnhance.Contrast(tile).enhance(1.08)
        mask = Image.new("L", (95, 95))
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle((2, 2, 92, 92), radius=14, fill=255)
        tile.putalpha(mask)
        ImageDraw.Draw(tile).rounded_rectangle(
            (2, 2, 92, 92), radius=14, outline=(199, 167, 104, 255), width=3
        )
        tiles[name] = tile
    for tag in COUNTRIES:
        flag = Image.open(MOD / f"gfx/flags/{tag}.tga").convert("RGBA")
        tile = Image.new("RGBA", (95, 95), (23, 29, 38, 0))
        ImageDraw.Draw(tile).rounded_rectangle(
            (2, 2, 92, 92),
            radius=14,
            fill=(23, 29, 38, 255),
            outline=(199, 167, 104, 255),
            width=3,
        )
        flag = ImageOps.contain(flag, (81, 65), method=Image.Resampling.LANCZOS)
        tile.alpha_composite(flag, ((95 - flag.width) // 2, (95 - flag.height) // 2))
        tiles[tag.lower()] = tile
    for name, tile in tiles.items():
        save_dds(tile, f"gfx/interface/goals/bc_{name}.dds")

    # One supplied Tito illustration. Other portraits are explicitly symbolic placeholders.
    save_dds(fit(tito, (260, 12, 900, 875), (156, 210)), "gfx/leaders/BC/BC_Tito.dds")
    government = fit(tito, (1050, 100, 1760, 650), (156, 210)).convert("RGBA")
    government = ImageEnhance.Brightness(government).enhance(0.65)
    save_dds(government, "gfx/leaders/BC/BC_government.dds")
    for tag in COUNTRIES:
        portrait = government.copy()
        flag = (
            Image.open(MOD / f"gfx/flags/{tag}.tga")
            .convert("RGBA")
            .resize((138, 88), Image.Resampling.LANCZOS)
        )
        portrait.alpha_composite(flag, (9, 88))
        ImageDraw.Draw(portrait).rectangle(
            (8, 87, 147, 177), outline=(199, 167, 104), width=2
        )
        save_dds(portrait, f"gfx/leaders/BC/BC_{tag}_government.dds")

    # Actual bookmark thumbnails, not a screenshot of a fake in-game menu.
    save_dds(
        fit(tito, (60, 0, 1810, 880), (512, 256)), "gfx/interface/bookmarks/bc_1980.dds"
    )
    save_dds(
        ImageOps.fit(serbia, (512, 256), method=Image.Resampling.LANCZOS),
        "gfx/interface/bookmarks/bc_serbia.dds",
    )
    save_dds(
        fit(tito, (80, 5, 1770, 870), (512, 320)), "gfx/event_pictures/bc_tito.dds"
    )
    save_dds(
        fit(tito, (1030, 70, 1910, 900), (512, 320)), "gfx/event_pictures/bc_crisis.dds"
    )
    save_dds(
        ImageOps.fit(serbia, (512, 320), method=Image.Resampling.LANCZOS),
        "gfx/event_pictures/bc_serbia.dds",
    )

    sprites = ["spriteTypes = {"]

    def sprite(name, texture):
        sprites.extend(
            [
                "    spriteType = {",
                f'        name = "{name}"',
                f'        texturefile = "{texture}"',
                "    }",
            ]
        )

    for name in tiles:
        for prefix in ["GFX_BC_goal_", "GFX_decision_BC_"]:
            sprite(prefix + name, f"gfx/interface/goals/bc_{name}.dds")
        sprite(f"GFX_BC_goal_{name}_shine", f"gfx/interface/goals/bc_{name}.dds")
    for key, tile in [
        ("BC_debt_crisis", "reconstruction"),
        ("BC_fragmented_command", "army"),
        ("BC_reconstruction_program", "economy"),
    ]:
        sprite("GFX_idea_" + key, f"gfx/interface/goals/bc_{tile}.dds")
    for name, file in [
        # Keep the source panorama available without replacing a native UI sprite.
        (
            "GFX_BC_MAIN_MENU_PANORAMA",
            "gfx/interface/illustrations/bc_main_menu_background.dds",
        ),
        (
            "GFX_BC_SERBIA_BACKGROUND",
            "gfx/interface/illustrations/bc_serbia_background.dds",
        ),
        ("GFX_BC_BOOKMARK_1980", "gfx/interface/bookmarks/bc_1980.dds"),
        ("GFX_BC_BOOKMARK_SERBIA", "gfx/interface/bookmarks/bc_serbia.dds"),
        ("GFX_BC_event_tito", "gfx/event_pictures/bc_tito.dds"),
        ("GFX_BC_event_crisis", "gfx/event_pictures/bc_crisis.dds"),
        ("GFX_BC_event_serbia", "gfx/event_pictures/bc_serbia.dds"),
    ]:
        sprite(name, file)
    sprites.append("}")
    old = MOD / "interface/balkan_collapse.gfx"
    if old.exists():
        old.unlink()
    (MOD / "interface/zz_balkan_collapse.gfx").write_text(
        "\n".join(sprites) + "\n", encoding="utf-8"
    )

    # Accurate geometric state flags, not invented photographs. These cosmetic tags
    # use the existing Serbian flag or the historical Yugoslav tricolour.
    blue, white, red = (0, 56, 147), (255, 255, 255), (222, 0, 0)
    yug = Image.new("RGB", (820, 520), white)
    d = ImageDraw.Draw(yug)
    d.rectangle((0, 0, 819, 172), fill=blue)
    d.rectangle((0, 347, 819, 519), fill=red)
    fry = yug.copy()
    center, radius = (410, 260), 168
    points = []
    for n in range(10):
        a = -math.pi / 2 + math.pi * n / 5
        r = radius if n % 2 == 0 else radius * 0.382
        points.append((center[0] + math.cos(a) * r, center[1] + math.sin(a) * r))
    d.polygon(points, fill=red, outline=(255, 209, 0), width=10)
    modern = Image.open(MOD / "gfx/flags/SER.tga").convert("RGB")
    for cosmetic, flag in [
        ("BC_YUGOSLAVIA", yug),
        ("BC_RESTORED_YUGOSLAVIA", yug),
        ("BC_FRY", fry),
        ("BC_SERBIA", modern),
    ]:
        for folder, size in [("", (82, 52)), ("medium", (41, 26)), ("small", (10, 7))]:
            directory = MOD / "gfx/flags" / folder
            directory.mkdir(parents=True, exist_ok=True)
            for suffix in ["", "_communism", "_democratic", "_neutrality", "_fascism"]:
                flag.resize(size, Image.Resampling.LANCZOS).save(
                    directory / f"{cosmetic}{suffix}.tga", compression=None
                )
    # Preserve the supplied loading screens and panorama asset. Leave native menu UI alone.
    # load_1 = Tito / Serbia 1980; load_2 = Serbia; the game chooses loading images randomly.
    manifest = {
        "method": "Crops, resizing, DDS encoding and flag geometry only. No generated or downloaded photographs.",
        "sources": {
            p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in [tito_src, city_src, serbia_src, crisis_src]
        },
        "photo_focuses": {name: list(box) for name, (_, box) in crops.items()},
        "leader_portraits": "Tito is cropped from the supplied image. All other leaders use symbolic flag/building placeholders; these are not their photographs.",
    }
    (ROOT / "assets/ARTWORK_SOURCE.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"Prepared {len(tiles)} reused photograph/flag focus icons, bookmark art and symbolic leader portraits."
    )


if __name__ == "__main__":
    prepare()
