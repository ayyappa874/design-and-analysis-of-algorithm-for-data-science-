"""
experiment.py
=============
Loads the OpenFlights airports dataset, projects lat/long to a local
equirectangular (x, y) plane in kilometres, and benchmarks:
    - Brute Force
    - Divide and Conquer
    - Hybrid (threshold = 40)
across increasing input sizes n = 10^3 ... full dataset (~7.6 x 10^3).

Brute force is capped beyond n where its O(n^2) cost becomes impractical
for repeated experimentation (documented as an assumption in the report).
"""

import csv
import json
import math
import random
import sys

sys.path.insert(0, "/home/claude/project/code")
from closest_pair import brute_force, divide_and_conquer, hybrid, run_timed

random.seed(7)

DATA_PATH = "/home/claude/project/data/airports.dat"
OUT_JSON = "/home/claude/project/data/results.json"
OUT_CSV = "/home/claude/project/data/results.csv"

# ---------------------------------------------------------------------------
# 1. Load and project the dataset
# ---------------------------------------------------------------------------
def load_airports(path):
    pts = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            try:
                lat = float(row[6])
                lon = float(row[7])
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    pts.append((lat, lon))
            except (ValueError, IndexError):
                continue
    return pts


def project_equirectangular(latlon_points):
    """
    Convert (lat, lon) in degrees to local planar (x, y) in kilometres using
    an equirectangular projection centred on the mean latitude. Adequate for
    nearest-neighbour distance ranking over a bounded region; documented as
    an assumption/limitation in the report (great-circle distance would be
    exact but is unnecessary for relative closest-pair ranking here).
    """
    R = 6371.0  # mean Earth radius, km
    mean_lat = sum(p[0] for p in latlon_points) / len(latlon_points)
    mean_lat_rad = math.radians(mean_lat)
    out = []
    for lat, lon in latlon_points:
        x = math.radians(lon) * R * math.cos(mean_lat_rad)
        y = math.radians(lat) * R
        out.append((x, y))
    return out


# ---------------------------------------------------------------------------
# 2. Benchmark loop
# ---------------------------------------------------------------------------
def main():
    raw = load_airports(DATA_PATH)
    all_points = project_equirectangular(raw)
    random.shuffle(all_points)
    N_FULL = len(all_points)
    print(f"Loaded {N_FULL} valid airport coordinate records.")

    # Sizes: 10^3 up to the full dataset size (~7.6k), plus a couple of
    # midpoints, as required by the brief (10^3 - 10^4 range).
    sizes = [1000, 2000, 3000, 4000, 5000, 6000, N_FULL]
    sizes = sorted(set(s for s in sizes if s <= N_FULL))

    BRUTE_FORCE_CUTOFF = 6000  # beyond this, brute force is skipped (too slow to repeat)

    results = []
    for n in sizes:
        subset = all_points[:n]
        row = {"n": n}

        # --- Divide and Conquer ---
        r = run_timed(divide_and_conquer, subset)
        row["dc_time"] = r["time_sec"]
        row["dc_dist_calls"] = r["distance_calls"]
        row["dc_comparisons"] = r["comparisons"]
        row["dc_result"] = r["distance"]

        # --- Hybrid --- (threshold=20 chosen via empirical sweep, see threshold_sweep.py)
        r = run_timed(hybrid, subset, threshold=20)
        row["hy_time"] = r["time_sec"]
        row["hy_dist_calls"] = r["distance_calls"]
        row["hy_comparisons"] = r["comparisons"]
        row["hy_result"] = r["distance"]

        # --- Brute Force (only up to cutoff) ---
        if n <= BRUTE_FORCE_CUTOFF:
            r = run_timed(brute_force, subset)
            row["bf_time"] = r["time_sec"]
            row["bf_dist_calls"] = r["distance_calls"]
            row["bf_comparisons"] = r["comparisons"]
            row["bf_result"] = r["distance"]
        else:
            row["bf_time"] = None
            row["bf_dist_calls"] = None
            row["bf_comparisons"] = None
            row["bf_result"] = None

        results.append(row)
        print(f"n={n:6d}  DC={row['dc_time']*1000:8.2f}ms  "
              f"Hybrid={row['hy_time']*1000:8.2f}ms  "
              f"BF={'%.2fms' % (row['bf_time']*1000) if row['bf_time'] else 'skipped':>10s}")

    with open(OUT_JSON, "w") as f:
        json.dump(results, f, indent=2)

    with open(OUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)

    print(f"\nSaved results to {OUT_JSON} and {OUT_CSV}")


if __name__ == "__main__":
    main()
