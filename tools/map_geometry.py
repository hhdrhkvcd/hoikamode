"""Native map-placement schema; raster work is optional and only for import/deep checks.

A spawn point is not a state-history building. The last column of
naval_base_spawn is a SEA province; floating_harbor uses the coastal LAND province.
"""

from __future__ import annotations

import math
from io import BytesIO

SPAWN_TYPES = {
    "naval_base_spawn",
    "nuclear_reactor_spawn",
    "rocket_site_spawn",
    "special_project_facility_spawn",
    "supply_node",
    "floating_harbor",
}
SEA_TARGET_TYPES = {"naval_base_spawn"}


class ProvinceRaster:
    def __init__(self, bitmap, definitions):
        import numpy as np
        from PIL import Image

        self.np = np
        image = Image.open(BytesIO(bitmap)) if isinstance(bitmap, bytes) else bitmap
        self.width, self.height = image.size
        rgb = np.asarray(image.convert("RGB"))
        lookup = np.zeros(1 << 24, dtype=np.uint16)
        for p, row in definitions.items():
            lookup[(int(row[1]) << 16) | (int(row[2]) << 8) | int(row[3])] = p
        colors = (
            (rgb[:, :, 0].astype(np.uint32) << 16)
            | (rgb[:, :, 1].astype(np.uint32) << 8)
            | rgb[:, :, 2].astype(np.uint32)
        )
        self.ids = lookup[colors]
        max_id = max(definitions)
        land = np.zeros(max_id + 1, dtype=bool)
        sea = np.zeros(max_id + 1, dtype=bool)
        for p, row in definitions.items():
            land[p] = bool(p) and row[4] == "land"
            sea[p] = row[4] == "sea"
        ids = self.ids
        self.land_ids = {p for p, flag in enumerate(land) if flag and p}
        self.sea_ids = {p for p, flag in enumerate(sea) if flag}
        self.shore_pairs = set()
        neighbors = [
            (ids[:, :-1], ids[:, 1:]),
            (ids[:, 1:], ids[:, :-1]),
            (ids[:-1, :], ids[1:, :]),
            (ids[1:, :], ids[:-1, :]),
            (ids[:, -1:], ids[:, :1]),
            (ids[:, :1], ids[:, -1:]),
        ]
        for a, b in neighbors:
            mask = land[a] & sea[b]
            pairs = np.unique(np.column_stack((a[mask], b[mask])), axis=0)
            self.shore_pairs.update((int(p), int(w)) for p, w in pairs)
        self.coastal = {p for p, _ in self.shore_pairs}

    def in_bounds(self, x, z):
        return (
            math.isfinite(x)
            and math.isfinite(z)
            and 0 <= x < self.width
            and 0 <= z < self.height
        )

    def province_at(self, x, z):
        if not self.in_bounds(x, z):
            raise ValueError(f"Map position outside bitmap: {x}, {z}")
        return int(self.ids[self.height - 1 - int(z), int(x)])

    def center(self, province):
        ys, xs = self.np.nonzero(self.ids == province)
        if not len(xs):
            raise ValueError(f"No bitmap pixels for province {province}")
        distance = (xs - xs.mean()) ** 2 + (ys - ys.mean()) ** 2
        i = int(distance.argmin())
        return float(xs[i]) + 0.5, self.height - float(ys[i]) - 0.5


def prepare_buildings(text, allowed, raster, province_states, before=None, removed=()):
    lines, ports = [], []
    floating_seen = set()
    repairs = {
        "floating_harbor_state_repairs": 0,
        "removed_inland_floating_harbors": 0,
        "removed_duplicate_floating_harbors": 0,
        "removed_degenerate_province_markers": 0,
        "removed_retired_state_rows": 0,
    }
    valid_states = {int(s) for s in province_states.values()}
    for original in text.splitlines():
        if not original.strip():
            continue
        row = original.strip().split(";")
        if len(row) != 7:
            raise ValueError("Expected seven native building-placement columns")
        if row[1] not in allowed | SPAWN_TYPES:
            continue
        state, kind, x, y, z, rotation, target = row
        if kind != "floating_harbor" and int(state) not in valid_states:
            # Placements belonging to states retired with the map artefacts.
            repairs["removed_retired_state_rows"] += 1
            continue
        if kind == "floating_harbor":
            province = int(target)
            if province not in raster.coastal:
                repairs["removed_inland_floating_harbors"] += 1
                continue
            if province in floating_seen:
                repairs["removed_duplicate_floating_harbors"] += 1
                continue
            floating_seen.add(province)
            owner_state = str(province_states[province])
            if state != owner_state:
                repairs["floating_harbor_state_repairs"] += 1
                row[0] = owner_state
        numbers = tuple(map(float, (x, y, z, rotation)))
        if not all(math.isfinite(v) for v in numbers) or not raster.in_bounds(
            numbers[0], numbers[2]
        ):
            raise ValueError(f"Invalid building placement: {original}")
        if kind in SPAWN_TYPES:
            # Positions are only remapped for provinces that still exist: the
            # pre-merge raster tells a stale marker apart from a real neighbour.
            source_raster = before or raster
            placed = source_raster.province_at(numbers[0], numbers[2])
            if placed in set(removed) or (
                kind in SEA_TARGET_TYPES
                and (placed not in province_states or placed not in raster.land_ids)
            ):
                repairs["removed_degenerate_province_markers"] += 1
                continue
        if kind == "naval_base_spawn":
            p = raster.province_at(numbers[0], numbers[2])
            if (
                province_states.get(p) != int(state)
                or (p, int(target)) not in raster.shore_pairs
            ):
                raise ValueError(f"Port is not on its state's shoreline: {original}")
            ports.append([len(lines) + 1, p])
        lines.append(";".join(row))
    if (
        len({p for _, p in ports}) != len(ports)
        or {p for _, p in ports} != raster.coastal
    ):
        raise ValueError(
            "Native port markers do not cover every coastal province exactly once"
        )
    # The native buildings loader treats an extra EOF row as an invalid record.
    return "\n".join(lines), ports, repairs


def repair_unitstacks(text, raster, drop=()):
    drop = set(drop)
    rows = [
        row
        for row in (line.split(";") for line in text.splitlines() if line.strip())
        if int(row[0]) not in drop
    ]
    anchors = {}
    for row in rows:
        if len(row) != 7:
            raise ValueError("Expected seven unit-stack columns")
        p, slot = int(row[0]), int(row[1])
        x, y, z, angle, scale = map(float, row[2:])
        if slot == 0 and raster.in_bounds(x, z) and raster.province_at(x, z) == p:
            anchors[p] = (x, y, z)
    repaired = []
    for row in rows:
        p, slot = int(row[0]), int(row[1])
        x, y, z, angle, scale = map(float, row[2:])
        if not all(
            math.isfinite(v) for v in (x, y, z, angle, scale)
        ) or not raster.in_bounds(x, z):
            if p in anchors:
                x, y, z = anchors[p]
            else:
                x, z = raster.center(p)
                y = 9.5
            row[2:5] = [f"{v:.2f}" for v in (x, y, z)]
            repaired.append([p, slot])
    return ("\n".join(";".join(row) for row in rows) + "\n").encode("utf-8"), repaired


# The engine derives province centres, label anchors and building meshes from
# the raster. A province drawn with a handful of pixels collapses to zero
# extent in the downsampled masks it uses at menu/country-select zoom and the
# game then divides by that zero area -- crash C0000094 (INT_DIVIDE_BY_ZERO)
# in the province-graphics chain, seconds after "Startup time".
MIN_PROVINCE_PIXELS = 8


def province_areas(raster):
    """Pixel count per province id in the supplied provinces bitmap."""
    np = raster.np
    values, counts = np.unique(raster.ids, return_counts=True)
    return {int(v): int(c) for v, c in zip(values, counts)}


def degenerate_provinces(raster, limit=MIN_PROVINCE_PIXELS):
    """Map artefacts smaller than `limit` pixels, in stable id order."""
    return sorted(
        p for p, area in province_areas(raster).items() if 0 < area < limit
    )


def merge_targets(raster, provinces):
    """Merge every degenerate province into its most common 4-neighbour.

    Untouched pixels keep their exact colour, so the rest of the map stays
    byte-identical; only the artefact itself is repainted.
    """
    np = raster.np
    ids = raster.ids
    height, width = ids.shape
    targets = sorted(set(provinces))
    tally = {p: {} for p in targets}
    for province in targets:
        ys, xs = np.nonzero(ids == province)
        for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            ny, nx = ys + dy, xs + dx
            keep = (ny >= 0) & (ny < height) & (nx >= 0) & (nx < width)
            for value in ids[ny[keep], nx[keep]].tolist():
                if value != province:
                    tally[province][value] = tally[province].get(value, 0) + 1
    merged = {}
    for province, counts in tally.items():
        if not counts:
            raise ValueError(f"Province {province} touches no other province")
        merged[province] = min(counts, key=lambda p: (-counts[p], p))
    return merged


def paint_provinces(bitmap, replacements, definitions):
    """Rewrite the merge pixels in place inside the original BMP bytes."""
    if not replacements:
        return bitmap
    np = import_numpy()
    bytearray_buffer = bytearray(bitmap)
    if bytearray_buffer[:2] != b"BM":
        raise ValueError("Provinces image must be a BMP file")
    offset = int.from_bytes(bytearray_buffer[10:14], "little")
    header_size = int.from_bytes(bytearray_buffer[14:18], "little")
    width = int.from_bytes(bytearray_buffer[18:22], "little", signed=True)
    height = int.from_bytes(bytearray_buffer[22:26], "little", signed=True)
    bits = int.from_bytes(bytearray_buffer[28:30], "little")
    compression = int.from_bytes(bytearray_buffer[30:34], "little")
    if header_size < 40 or bits != 24 or compression != 0 or width <= 0 or not height:
        raise ValueError("Provinces image must be an uncompressed 24-bpp BMP")
    rows = abs(height)
    stride = (width * 3 + 3) & ~3
    pixels = np.frombuffer(bytearray_buffer, dtype=np.uint8,
                           count=stride * rows, offset=offset)
    colours = {}
    for province, target in replacements.items():
        row = definitions[target]
        colours[province] = np.array(
            [int(row[3]), int(row[2]), int(row[1])], dtype=np.uint8
        )
    image = raster_colours(bitmap)
    pixel_offsets = np.arange(3)
    for province, colour in colours.items():
        source = definitions[province]
        mask = (
            (image[:, :, 0] == int(source[1]))
            & (image[:, :, 1] == int(source[2]))
            & (image[:, :, 2] == int(source[3]))
        )
        ys, xs = np.nonzero(mask)
        if not len(xs):
            raise ValueError(f"No pixels found for province {province}")
        row_index = (rows - 1 - ys) if height > 0 else ys
        target_offsets = row_index * stride + xs * 3
        pixels[target_offsets[:, None] + pixel_offsets[None, :]] = colour[None, :]
    return bytes(bytearray_buffer)


def raster_colours(bitmap):
    """RGB array of a provinces bitmap, top-down like the game's rows."""
    np = import_numpy()
    from PIL import Image

    return np.asarray(Image.open(BytesIO(bitmap)).convert("RGB"))


def import_numpy():
    import numpy

    return numpy
