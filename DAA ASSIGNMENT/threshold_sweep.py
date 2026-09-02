"""
threshold_sweep.py
===================
Sweeps the hybrid algorithm's brute-force switchover threshold on a fixed
n=7698 dataset to empirically justify the chosen threshold value.
"""
import json
import sys
sys.path.insert(0, "/home/claude/project/code")
from experiment import load_airports, project_equirectangular
from closest_pair import hybrid, run_timed
import random

random.seed(7)
raw = load_airports("/home/claude/project/data/airports.dat")
pts = project_equirectangular(raw)
random.shuffle(pts)

thresholds = [2, 5, 10, 20, 40, 80, 160, 320, 640]
rows = []
for t in thresholds:
    r = run_timed(hybrid, pts, threshold=t)
    rows.append({"threshold": t, "time_sec": r["time_sec"],
                 "distance_calls": r["distance_calls"],
                 "comparisons": r["comparisons"]})
    print(f"threshold={t:4d}  time={r['time_sec']*1000:8.3f} ms  "
          f"distance_calls={r['distance_calls']:8d}")

with open("/home/claude/project/data/threshold_sweep.json", "w") as f:
    json.dump(rows, f, indent=2)
