#!/usr/bin/env python3
"""
generate_county_maps.py — Generates county SVG maps and county data from Census TIGER shapefiles.

Usage:
    python3 tools/generate_county_maps.py WA          # generate WA county map + counties.json
    python3 tools/generate_county_maps.py WA --places  # also generate place maps for all WA counties

Downloads (cached in /tmp/):
    Census TIGER county boundaries: cb_2023_us_county_500k
    Census TIGER place boundaries: tl_2023_{statefp}_place

Writes:
    geo/states/{st}-counties.svg         — county map SVG
    geo/states/{st}-{county}-places.svg  — place map SVGs (one per county)
    tools/data/counties.json             — county data keyed by state
    tools/data/places.json               — place data keyed by state > county
"""

import json
import math
import os
import struct
import sys
import urllib.request
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GEO_STATES = REPO_ROOT / "geo" / "states"
DATA_DIR = Path(__file__).resolve().parent / "data"
CACHE_DIR = Path("/tmp/ctm_geo")

STATE_FIPS = {
    "AL": "01", "AK": "02", "AZ": "04", "AR": "05", "CA": "06",
    "CO": "08", "CT": "09", "DE": "10", "FL": "12", "GA": "13",
    "HI": "15", "ID": "16", "IL": "17", "IN": "18", "IA": "19",
    "KS": "20", "KY": "21", "LA": "22", "ME": "23", "MD": "24",
    "MA": "25", "MI": "26", "MN": "27", "MS": "28", "MO": "29",
    "MT": "30", "NE": "31", "NV": "32", "NH": "33", "NJ": "34",
    "NM": "35", "NY": "36", "NC": "37", "ND": "38", "OH": "39",
    "OK": "40", "OR": "41", "PA": "42", "RI": "44", "SC": "45",
    "SD": "46", "TN": "47", "TX": "48", "UT": "49", "VT": "50",
    "VA": "51", "WA": "53", "WV": "54", "WI": "55", "WY": "56",
}


# ---------------------------------------------------------------------------
# Pure-Python shapefile reader (no geopandas / fiona / pyshp dependency)
# ---------------------------------------------------------------------------

def read_dbf(path):
    with open(path, "rb") as f:
        f.read(1)  # version
        f.read(3)  # date
        nrec = struct.unpack("<I", f.read(4))[0]
        hdr_len = struct.unpack("<H", f.read(2))[0]
        rec_len = struct.unpack("<H", f.read(2))[0]
        f.read(20)
        fields = []
        while True:
            fb = f.read(32)
            if fb[0] == 0x0D:
                break
            name = fb[:11].split(b"\x00")[0].decode("ascii")
            flen = fb[16]
            fields.append((name, flen))
        f.seek(hdr_len)
        records = []
        for _ in range(nrec):
            raw = f.read(rec_len)
            if raw[0:1] == b"*":
                continue
            rec = {}
            offset = 1
            for name, flen in fields:
                rec[name] = raw[offset : offset + flen].decode("latin-1").strip()
                offset += flen
            records.append(rec)
    return records


def read_shp_polygons(path):
    with open(path, "rb") as f:
        f.read(4)  # file code
        f.read(20)  # unused
        file_len = struct.unpack(">I", f.read(4))[0] * 2
        f.read(4)  # version
        struct.unpack("<I", f.read(4))[0]  # shape type
        f.read(64)  # bounding box (8 doubles)
        shapes = []
        while f.tell() < file_len:
            buf = f.read(4)
            if len(buf) < 4:
                break
            struct.unpack(">I", buf)  # record number
            content_len = struct.unpack(">I", f.read(4))[0] * 2
            start = f.tell()
            st = struct.unpack("<I", f.read(4))[0]
            if st == 0:
                shapes.append({"parts": [], "bbox": None})
                f.seek(start + content_len)
                continue
            bbox = struct.unpack("<4d", f.read(32))
            num_parts = struct.unpack("<I", f.read(4))[0]
            num_points = struct.unpack("<I", f.read(4))[0]
            parts = list(struct.unpack(f"<{num_parts}I", f.read(4 * num_parts)))
            points = []
            for _ in range(num_points):
                x, y = struct.unpack("<2d", f.read(16))
                points.append((x, y))
            rings = []
            for i, start_idx in enumerate(parts):
                end_idx = parts[i + 1] if i + 1 < len(parts) else num_points
                rings.append(points[start_idx:end_idx])
            shapes.append({"parts": rings, "bbox": bbox})
            f.seek(start + content_len)
    return shapes


def download_and_extract(url, cache_key):
    cache_path = CACHE_DIR / cache_key
    zip_path = cache_path / (cache_key + ".zip")
    if cache_path.exists() and any(cache_path.glob("*.shp")):
        return cache_path
    cache_path.mkdir(parents=True, exist_ok=True)
    print(f"  downloading {url} ...")
    urllib.request.urlretrieve(url, zip_path)
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(cache_path)
    return cache_path


def get_county_shapefiles():
    url = "https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_us_county_500k.zip"
    cache = CACHE_DIR / "county"
    shp = cache / "cb_2023_us_county_500k.shp"
    if shp.exists():
        return cache
    # Check if already downloaded elsewhere
    alt = Path("/tmp/county/cb_2023_us_county_500k.shp")
    if alt.exists():
        cache.mkdir(parents=True, exist_ok=True)
        for ext in [".shp", ".shx", ".dbf", ".prj", ".cpg"]:
            src = alt.parent / f"cb_2023_us_county_500k{ext}"
            dst = cache / f"cb_2023_us_county_500k{ext}"
            if src.exists() and not dst.exists():
                os.symlink(src, dst)
        return cache
    return download_and_extract(url, "county")


def get_place_shapefiles(statefp):
    url = f"https://www2.census.gov/geo/tiger/TIGER2023/PLACE/tl_2023_{statefp}_place.zip"
    cache = CACHE_DIR / f"place_{statefp}"
    shp = cache / f"tl_2023_{statefp}_place.shp"
    if shp.exists():
        return cache
    alt = Path(f"/tmp/wa_places/tl_2023_{statefp}_place.shp")
    if alt.exists():
        cache.mkdir(parents=True, exist_ok=True)
        for ext in [".shp", ".shx", ".dbf", ".prj", ".cpg"]:
            src = alt.parent / f"tl_2023_{statefp}_place{ext}"
            dst = cache / f"tl_2023_{statefp}_place{ext}"
            if src.exists() and not dst.exists():
                os.symlink(src, dst)
        return cache
    return download_and_extract(url, f"place_{statefp}")


# ---------------------------------------------------------------------------
# Coordinate projection (lon/lat → SVG pixels)
# ---------------------------------------------------------------------------

def project_albers(lon, lat):
    lon0 = -96.0
    lat0 = 37.5
    lat1 = 29.5
    lat2 = 45.5
    to_rad = math.pi / 180
    n = 0.5 * (math.sin(lat1 * to_rad) + math.sin(lat2 * to_rad))
    c = math.cos(lat1 * to_rad) ** 2 + 2 * n * math.sin(lat1 * to_rad)
    rho0 = math.sqrt(c - 2 * n * math.sin(lat0 * to_rad)) / n
    theta = n * (lon - lon0) * to_rad
    rho = math.sqrt(c - 2 * n * math.sin(lat * to_rad)) / n
    x = rho * math.sin(theta)
    y = rho0 - rho * math.cos(theta)
    return x, y


def rings_to_svg_path(rings, transform):
    parts = []
    for ring in rings:
        if not ring:
            continue
        cmds = []
        for i, (lon, lat) in enumerate(ring):
            px, py = transform(lon, lat)
            if i == 0:
                cmds.append(f"M{px:.1f},{py:.1f}")
            else:
                cmds.append(f"L{px:.1f},{py:.1f}")
        cmds.append("Z")
        parts.append("".join(cmds))
    return "".join(parts)


def compute_bbox_svg(shapes, transform):
    min_x = min_y = float("inf")
    max_x = max_y = float("-inf")
    for shape in shapes:
        for ring in shape["parts"]:
            for lon, lat in ring:
                px, py = transform(lon, lat)
                min_x = min(min_x, px)
                min_y = min(min_y, py)
                max_x = max(max_x, px)
                max_y = max(max_y, py)
    return min_x, min_y, max_x, max_y


def compute_bbox_from_transform(shapes, transform_fn):
    min_x = min_y = float("inf")
    max_x = max_y = float("-inf")
    for shape in shapes:
        for ring in shape["parts"]:
            for lon, lat in ring:
                px, py = transform_fn(lon, lat)
                min_x = min(min_x, px)
                min_y = min(min_y, py)
                max_x = max(max_x, px)
                max_y = max(max_y, py)
    return min_x, min_y, max_x, max_y


def make_transform(shapes, width=800, height=600, padding=20):
    min_x, min_y, max_x, max_y = compute_bbox_svg(shapes, project_albers)
    data_w = max_x - min_x
    data_h = max_y - min_y
    scale = min((width - 2 * padding) / data_w, (height - 2 * padding) / data_h)
    off_x = padding - min_x * scale + (width - 2 * padding - data_w * scale) / 2
    off_y = padding + max_y * scale + (height - 2 * padding - data_h * scale) / 2

    def transform(lon, lat):
        px, py = project_albers(lon, lat)
        return px * scale + off_x, -py * scale + off_y

    return transform


def simplify_ring(ring, tolerance=0.0001):
    if len(ring) <= 4:
        return ring
    result = [ring[0]]
    for i in range(1, len(ring) - 1):
        dx = ring[i][0] - result[-1][0]
        dy = ring[i][1] - result[-1][1]
        if math.sqrt(dx * dx + dy * dy) > tolerance:
            result.append(ring[i])
    result.append(ring[-1])
    return result


# ---------------------------------------------------------------------------
# County SVG generation
# ---------------------------------------------------------------------------

def slugify(name):
    return name.lower().replace(" ", "-").replace("'", "").replace(".", "")


def generate_county_svg(state_abbr, records, shapes):
    statefp = STATE_FIPS[state_abbr]
    indices = [i for i, r in enumerate(records) if r["STATEFP"] == statefp]
    state_shapes = [(records[i], shapes[i]) for i in indices]

    simplified = []
    for rec, shape in state_shapes:
        new_parts = [simplify_ring(ring, 0.002) for ring in shape["parts"]]
        simplified.append({"parts": new_parts, "bbox": shape["bbox"]})

    transform = make_transform(simplified)

    paths = []
    for (rec, _), simp in zip(state_shapes, simplified):
        name = rec["NAME"]
        fips = rec["COUNTYFP"]
        slug = slugify(name)
        path_d = rings_to_svg_path(simp["parts"], transform)
        paths.append(
            f'    <path class="county" id="{state_abbr}-{fips}" '
            f'data-county="{fips}" data-name="{name} County" '
            f'data-slug="{slug}" data-fips="{fips}">'
            f"<title>{name} County</title></path>"
            if not path_d
            else f'    <path class="county" id="{state_abbr}-{fips}" '
            f'data-county="{fips}" data-name="{name} County" '
            f'data-slug="{slug}" data-fips="{fips}" '
            f'd="{path_d}">'
            f"<title>{name} County</title></path>"
        )

    min_x, min_y, max_x, max_y = compute_bbox_svg(simplified, transform)
    vb_x = min_x - 5
    vb_y = min_y - 5
    vb_w = (max_x - min_x) + 10
    vb_h = (max_y - min_y) + 10

    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="{vb_x:.1f} {vb_y:.1f} {vb_w:.1f} {vb_h:.1f}"
     aria-label="{state_abbr} County Map"
     role="img">
  <g id="counties">
{chr(10).join(paths)}
  </g>
</svg>"""
    return svg, state_shapes


# ---------------------------------------------------------------------------
# Place SVG generation (places within a single county)
# ---------------------------------------------------------------------------

def point_in_polygon(px, py, polygon):
    inside = False
    n = len(polygon)
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def centroid_of_shape(shape):
    all_x = []
    all_y = []
    for ring in shape["parts"]:
        for x, y in ring:
            all_x.append(x)
            all_y.append(y)
    if not all_x:
        return 0, 0
    return sum(all_x) / len(all_x), sum(all_y) / len(all_y)


def assign_places_to_counties(place_records, place_shapes, county_records, county_shapes, statefp):
    county_indices = [i for i, r in enumerate(county_records) if r["STATEFP"] == statefp]
    county_polygons = []
    for i in county_indices:
        rec = county_records[i]
        shape = county_shapes[i]
        largest_ring = max(shape["parts"], key=len) if shape["parts"] else []
        county_polygons.append((rec["COUNTYFP"], rec["NAME"], largest_ring))

    assignments = {}
    for i, (prec, pshape) in enumerate(zip(place_records, place_shapes)):
        cx, cy = centroid_of_shape(pshape)
        assigned_fips = None
        for cfips, cname, ring in county_polygons:
            if ring and point_in_polygon(cx, cy, ring):
                assigned_fips = cfips
                break
        if assigned_fips:
            assignments.setdefault(assigned_fips, []).append(i)
    return assignments


def generate_place_svg(state_abbr, county_fips, county_name,
                       county_shape, place_records, place_shapes, place_indices):
    all_shapes_for_bbox = [county_shape]
    place_data = []
    for idx in place_indices:
        simp_parts = [simplify_ring(ring, 0.001) for ring in place_shapes[idx]["parts"]]
        simp_shape = {"parts": simp_parts, "bbox": place_shapes[idx]["bbox"]}
        all_shapes_for_bbox.append(simp_shape)
        place_data.append((place_records[idx], simp_shape))

    transform = make_transform(all_shapes_for_bbox)

    county_simp_parts = [simplify_ring(ring, 0.001) for ring in county_shape["parts"]]
    county_path_d = rings_to_svg_path(county_simp_parts, transform)
    boundary_el = (
        f'    <path class="county-boundary" d="{county_path_d}" />'
    )

    paths = []
    for prec, pshape in place_data:
        name = prec["NAME"]
        slug = slugify(name)
        lsad = prec.get("LSAD", "")
        classfp = prec.get("CLASSFP", "")
        if classfp in ("C1", "C5"):
            ptype = "city"
        elif classfp == "C2":
            ptype = "town"
        elif classfp in ("U1", "U2"):
            ptype = "cdp"
        else:
            ptype = "place"
        path_d = rings_to_svg_path(pshape["parts"], transform)
        paths.append(
            f'    <path class="place" id="{state_abbr}-{county_fips}-{slug}" '
            f'data-name="{name}" data-slug="{slug}" data-type="{ptype}" '
            f'd="{path_d}">'
            f"<title>{name}</title></path>"
        )

    min_x, min_y, max_x, max_y = compute_bbox_svg(all_shapes_for_bbox, transform)
    vb_x = min_x - 5
    vb_y = min_y - 5
    vb_w = (max_x - min_x) + 10
    vb_h = (max_y - min_y) + 10

    county_slug = slugify(county_name)
    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="{vb_x:.1f} {vb_y:.1f} {vb_w:.1f} {vb_h:.1f}"
     aria-label="{county_name} County Places Map"
     role="img">
{boundary_el}
  <g id="places">
{chr(10).join(paths)}
  </g>
</svg>"""
    return svg, place_data


# ---------------------------------------------------------------------------
# Data file generation
# ---------------------------------------------------------------------------

def build_counties_json(state_abbr, records, shapes):
    statefp = STATE_FIPS[state_abbr]
    counties_path = DATA_DIR / "counties.json"
    if counties_path.exists():
        with open(counties_path) as f:
            data = json.load(f)
    else:
        data = {}

    counties = []
    for rec in records:
        if rec["STATEFP"] != statefp:
            continue
        counties.append({
            "name": rec["NAME"],
            "fips": rec["COUNTYFP"],
            "slug": slugify(rec["NAME"]),
            "full_name": rec.get("NAMELSAD", f"{rec['NAME']} County"),
        })
    counties.sort(key=lambda c: c["fips"])
    data[state_abbr] = counties

    with open(counties_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  wrote {counties_path} ({len(counties)} {state_abbr} counties)")
    return counties


def build_places_json(state_abbr, place_records, place_shapes,
                      county_records, county_shapes, assignments):
    statefp = STATE_FIPS[state_abbr]
    places_path = DATA_DIR / "places.json"
    if places_path.exists():
        with open(places_path) as f:
            data = json.load(f)
    else:
        data = {}

    state_data = {}
    county_lookup = {}
    for rec in county_records:
        if rec["STATEFP"] == statefp:
            county_lookup[rec["COUNTYFP"]] = rec["NAME"]

    for county_fips, indices in sorted(assignments.items()):
        county_name = county_lookup.get(county_fips, county_fips)
        county_slug = slugify(county_name)
        places = []
        for idx in indices:
            prec = place_records[idx]
            classfp = prec.get("CLASSFP", "")
            if classfp in ("C1", "C5"):
                ptype = "city"
            elif classfp == "C2":
                ptype = "town"
            elif classfp in ("U1", "U2"):
                ptype = "cdp"
            else:
                ptype = "place"
            places.append({
                "name": prec["NAME"],
                "slug": slugify(prec["NAME"]),
                "type": ptype,
                "placefp": prec.get("PLACEFP", ""),
            })
        places.sort(key=lambda p: p["name"])
        state_data[county_slug] = places

    data[state_abbr] = state_data
    with open(places_path, "w") as f:
        json.dump(data, f, indent=2)
    total = sum(len(v) for v in state_data.values())
    print(f"  wrote {places_path} ({total} {state_abbr} places across {len(state_data)} counties)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 tools/generate_county_maps.py STATE_ABBR [--places]")
        print("Example: python3 tools/generate_county_maps.py WA --places")
        sys.exit(1)

    state_abbr = sys.argv[1].upper()
    do_places = "--places" in sys.argv

    if state_abbr not in STATE_FIPS:
        print(f"Unknown state: {state_abbr}")
        sys.exit(1)

    statefp = STATE_FIPS[state_abbr]
    st_lower = state_abbr.lower()

    GEO_STATES.mkdir(parents=True, exist_ok=True)

    print(f"Generating county map for {state_abbr} (FIPS {statefp})...")

    # Load county data
    county_dir = get_county_shapefiles()
    county_dbf = county_dir / "cb_2023_us_county_500k.dbf"
    county_shp = county_dir / "cb_2023_us_county_500k.shp"
    county_records = read_dbf(county_dbf)
    county_shapes = read_shp_polygons(county_shp)
    print(f"  loaded {len(county_records)} county records")

    # Generate county SVG
    svg_content, state_counties = generate_county_svg(state_abbr, county_records, county_shapes)
    svg_path = GEO_STATES / f"{st_lower}-counties.svg"
    svg_path.write_text(svg_content)
    print(f"  wrote {svg_path} ({len(state_counties)} counties)")

    # Build counties.json
    counties = build_counties_json(state_abbr, county_records, county_shapes)

    if do_places:
        print(f"\nGenerating place maps for {state_abbr}...")
        place_dir = get_place_shapefiles(statefp)
        place_dbf = place_dir / f"tl_2023_{statefp}_place.dbf"
        place_shp = place_dir / f"tl_2023_{statefp}_place.shp"
        place_records = read_dbf(place_dbf)
        place_shapes = read_shp_polygons(place_shp)
        print(f"  loaded {len(place_records)} place records")

        # Assign places to counties via centroid containment
        assignments = assign_places_to_counties(
            place_records, place_shapes, county_records, county_shapes, statefp
        )
        print(f"  assigned {sum(len(v) for v in assignments.values())} places to {len(assignments)} counties")

        # Build places.json
        build_places_json(state_abbr, place_records, place_shapes,
                         county_records, county_shapes, assignments)

        # Generate place SVGs for each county
        county_index = {i: (county_records[i], county_shapes[i])
                       for i in range(len(county_records))
                       if county_records[i]["STATEFP"] == statefp}
        fips_to_idx = {county_records[i]["COUNTYFP"]: i for i in county_index}

        for county_fips, place_indices in sorted(assignments.items()):
            ci = fips_to_idx.get(county_fips)
            if ci is None:
                continue
            crec = county_records[ci]
            cshape = county_shapes[ci]
            county_slug = slugify(crec["NAME"])

            place_svg, _ = generate_place_svg(
                state_abbr, county_fips, crec["NAME"],
                cshape, place_records, place_shapes, place_indices
            )
            place_svg_path = GEO_STATES / f"{st_lower}-{county_slug}-places.svg"
            place_svg_path.write_text(place_svg)
            print(f"  wrote {place_svg_path} ({len(place_indices)} places)")

    print(f"\nDone: {state_abbr} county maps generated")


if __name__ == "__main__":
    main()
