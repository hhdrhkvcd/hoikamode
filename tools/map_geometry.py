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


def prepare_buildings(text, allowed, raster, province_states):
    lines, ports = [], []
    floating_seen = set()
    repairs = {
        "floating_harbor_state_repairs": 0,
        "removed_inland_floating_harbors": 0,
        "removed_duplicate_floating_harbors": 0,
    }
    for original in text.splitlines():
        if not original.strip():
            continue
        row = original.strip().split(";")
        if len(row) != 7:
            raise ValueError("Expected seven native building-placement columns")
        if row[1] not in allowed | SPAWN_TYPES:
            continue
        state, kind, x, y, z, rotation, target = row
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


def repair_unitstacks(text, raster):
    rows = [line.split(";") for line in text.splitlines() if line.strip()]
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
