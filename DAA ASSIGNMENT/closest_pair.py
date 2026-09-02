"""
closest_pair.py
================
Closest-Pair-of-Points algorithms for large-scale geospatial facility data.

Implements:
    1. Brute Force              -> O(n^2)
    2. Divide and Conquer       -> O(n log n)
    3. Hybrid (D&C + threshold) -> O(n log n) with reduced constant factor

Author : CSA0615 - Design and Analysis of Algorithms
Dataset: OpenFlights Airports Database (~7,698 records)
         https://github.com/jpatokal/openflights
"""

import math
import time
import random
from dataclasses import dataclass, field


@dataclass
class Metrics:
    """Tracks operation counts for empirical complexity analysis."""
    distance_calls: int = 0
    comparisons: int = 0

    def reset(self):
        self.distance_calls = 0
        self.comparisons = 0


def euclid(p, q, m: Metrics):
    """Euclidean distance between two (x, y) points. Counts the call."""
    m.distance_calls += 1
    return math.sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)


# ---------------------------------------------------------------------------
# 1. BRUTE FORCE  ->  Theta(n^2)
# ---------------------------------------------------------------------------
def brute_force(points, metrics: Metrics = None):
    """
    Evaluate all n(n-1)/2 pairs and return the minimum-distance pair.
    Time  : Theta(n^2)
    Space : O(1) extra
    """
    m = metrics or Metrics()
    n = len(points)
    best = math.inf
    best_pair = None
    for i in range(n):
        for j in range(i + 1, n):
            m.comparisons += 1
            d = euclid(points[i], points[j], m)
            if d < best:
                best = d
                best_pair = (points[i], points[j])
    return best, best_pair, m


# ---------------------------------------------------------------------------
# 2. DIVIDE AND CONQUER  ->  O(n log n)
# ---------------------------------------------------------------------------
def divide_and_conquer(points, metrics: Metrics = None):
    m = metrics or Metrics()
    px = sorted(points, key=lambda p: p[0])
    py = sorted(points, key=lambda p: p[1])
    best, pair = _closest_pair_rec(px, py, m)
    return best, pair, m


def _closest_pair_rec(px, py, m: Metrics, leaf_threshold: int = 3):
    n = len(px)

    # Base case: brute force for tiny sub-problems (n <= 3)
    if n <= leaf_threshold:
        return _brute_on_slice(px, m)

    mid = n // 2
    mid_point = px[mid]

    px_left, px_right = px[:mid], px[mid:]
    mid_x = mid_point[0]

    py_left, py_right = [], []
    left_set = set(id(p) for p in px_left)
    for p in py:
        if id(p) in left_set:
            py_left.append(p)
        else:
            py_right.append(p)

    d_left, pair_left = _closest_pair_rec(px_left, py_left, m, leaf_threshold)
    d_right, pair_right = _closest_pair_rec(px_right, py_right, m, leaf_threshold)

    if d_left <= d_right:
        d, best_pair = d_left, pair_left
    else:
        d, best_pair = d_right, pair_right

    # Points within d of the dividing line (the "strip")
    strip = [p for p in py if abs(p[0] - mid_x) < d]

    # Classic result: each point needs comparison with at most the next
    # 7 points in the strip when sorted by y (constant factor, not n).
    for i in range(len(strip)):
        for j in range(i + 1, min(i + 8, len(strip))):
            m.comparisons += 1
            dist = euclid(strip[i], strip[j], m)
            if dist < d:
                d = dist
                best_pair = (strip[i], strip[j])

    return d, best_pair


def _brute_on_slice(px, m: Metrics):
    n = len(px)
    best = math.inf
    best_pair = None
    for i in range(n):
        for j in range(i + 1, n):
            m.comparisons += 1
            d = euclid(px[i], px[j], m)
            if d < best:
                best, best_pair = d, (px[i], px[j])
    return best, best_pair


# ---------------------------------------------------------------------------
# 3. HYBRID  ->  O(n log n), smaller constant for small n
# ---------------------------------------------------------------------------
def hybrid(points, metrics: Metrics = None, threshold: int = 40):
    """
    Same divide-and-conquer skeleton, but reverts to brute force whenever a
    sub-problem size falls below `threshold`, avoiding recursion / merge
    overhead on small partitions.
    """
    m = metrics or Metrics()
    px = sorted(points, key=lambda p: p[0])
    py = sorted(points, key=lambda p: p[1])
    best, pair = _hybrid_rec(px, py, m, threshold)
    return best, pair, m


def _hybrid_rec(px, py, m: Metrics, threshold):
    n = len(px)
    if n <= threshold:
        return _brute_on_slice(px, m)

    mid = n // 2
    mid_point = px[mid]
    px_left, px_right = px[:mid], px[mid:]
    mid_x = mid_point[0]

    left_set = set(id(p) for p in px_left)
    py_left, py_right = [], []
    for p in py:
        (py_left if id(p) in left_set else py_right).append(p)

    d_left, pair_left = _hybrid_rec(px_left, py_left, m, threshold)
    d_right, pair_right = _hybrid_rec(px_right, py_right, m, threshold)

    if d_left <= d_right:
        d, best_pair = d_left, pair_left
    else:
        d, best_pair = d_right, pair_right

    strip = [p for p in py if abs(p[0] - mid_x) < d]
    for i in range(len(strip)):
        for j in range(i + 1, min(i + 8, len(strip))):
            m.comparisons += 1
            dist = euclid(strip[i], strip[j], m)
            if dist < d:
                d, best_pair = dist, (strip[i], strip[j])

    return d, best_pair


# ---------------------------------------------------------------------------
# Timed wrapper used by the experiment harness
# ---------------------------------------------------------------------------
def run_timed(algo_fn, points, **kwargs):
    m = Metrics()
    t0 = time.perf_counter()
    dist, pair, m = algo_fn(points, metrics=m, **kwargs) if kwargs else algo_fn(points, metrics=m)
    t1 = time.perf_counter()
    return {
        "distance": dist,
        "pair": pair,
        "time_sec": t1 - t0,
        "distance_calls": m.distance_calls,
        "comparisons": m.comparisons,
    }


if __name__ == "__main__":
    random.seed(42)
    pts = [(random.uniform(0, 1000), random.uniform(0, 1000)) for _ in range(2000)]
    r1 = run_timed(brute_force, pts)
    r2 = run_timed(divide_and_conquer, pts)
    r3 = run_timed(hybrid, pts, threshold=40)
    print("Brute force :", r1["distance"], r1["time_sec"], r1["distance_calls"])
    print("D&C         :", r2["distance"], r2["time_sec"], r2["distance_calls"])
    print("Hybrid      :", r3["distance"], r3["time_sec"], r3["distance_calls"])
