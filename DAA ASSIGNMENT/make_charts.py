import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

with open("/home/claude/project/data/results.json") as f:
    R = json.load(f)
with open("/home/claude/project/data/threshold_sweep.json") as f:
    T = json.load(f)

FIG = "/home/claude/project/figures"
plt.rcParams.update({"font.size": 11, "figure.dpi": 150})

ns = [r["n"] for r in R]
dc_t = [r["dc_time"] * 1000 for r in R]
hy_t = [r["hy_time"] * 1000 for r in R]
bf_n = [r["n"] for r in R if r["bf_time"] is not None]
bf_t = [r["bf_time"] * 1000 for r in R if r["bf_time"] is not None]

# 1. Execution time comparison (linear)
plt.figure(figsize=(7, 4.5))
plt.plot(bf_n, bf_t, "o-", color="#d62728", label="Brute Force  O(n²)")
plt.plot(ns, dc_t, "s-", color="#1f77b4", label="Divide & Conquer  O(n log n)")
plt.plot(ns, hy_t, "^-", color="#2ca02c", label="Hybrid  O(n log n)")
plt.xlabel("Input size (n)")
plt.ylabel("Execution time (ms)")
plt.title("Execution Time vs Input Size")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(f"{FIG}/time_comparison_linear.png")
plt.close()

# 2. Log-scale time comparison
plt.figure(figsize=(7, 4.5))
plt.plot(bf_n, bf_t, "o-", color="#d62728", label="Brute Force")
plt.plot(ns, dc_t, "s-", color="#1f77b4", label="Divide & Conquer")
plt.plot(ns, hy_t, "^-", color="#2ca02c", label="Hybrid")
plt.yscale("log")
plt.xlabel("Input size (n)")
plt.ylabel("Execution time (ms, log scale)")
plt.title("Execution Time vs Input Size (log scale)")
plt.legend()
plt.grid(alpha=0.3, which="both")
plt.tight_layout()
plt.savefig(f"{FIG}/time_comparison_log.png")
plt.close()

# 3. Distance computations (operation counts)
dc_calls = [r["dc_dist_calls"] for r in R]
hy_calls = [r["hy_dist_calls"] for r in R]
bf_calls = [r["bf_dist_calls"] for r in R if r["bf_dist_calls"] is not None]

plt.figure(figsize=(7, 4.5))
plt.plot(bf_n, bf_calls, "o-", color="#d62728", label="Brute Force")
plt.plot(ns, dc_calls, "s-", color="#1f77b4", label="Divide & Conquer")
plt.plot(ns, hy_calls, "^-", color="#2ca02c", label="Hybrid")
plt.yscale("log")
plt.xlabel("Input size (n)")
plt.ylabel("Distance computations (log scale)")
plt.title("Distance-Computation Count vs Input Size")
plt.legend()
plt.grid(alpha=0.3, which="both")
plt.tight_layout()
plt.savefig(f"{FIG}/distance_calls.png")
plt.close()

# 4. Threshold sweep
th = [r["threshold"] for r in T]
th_t = [r["time_sec"] * 1000 for r in T]
plt.figure(figsize=(7, 4.5))
plt.plot(th, th_t, "d-", color="#9467bd")
plt.axvline(20, color="gray", linestyle="--", label="Chosen threshold = 20")
plt.xscale("log")
plt.xlabel("Brute-force switchover threshold (log scale)")
plt.ylabel("Execution time (ms)")
plt.title("Hybrid Algorithm: Threshold Sensitivity (n = 7,698)")
plt.legend()
plt.grid(alpha=0.3, which="both")
plt.tight_layout()
plt.savefig(f"{FIG}/threshold_sweep.png")
plt.close()

# 5. Speedup bar chart at full dataset size
last = R[-1]
labels = ["Divide & Conquer", "Hybrid"]
speedup_vs_bf_5000 = None
r5000 = next(r for r in R if r["n"] == 5000)
speedups = [r5000["bf_time"] / r5000["dc_time"], r5000["bf_time"] / r5000["hy_time"]]
plt.figure(figsize=(5.5, 4.5))
bars = plt.bar(labels, speedups, color=["#1f77b4", "#2ca02c"])
plt.ylabel("Speedup factor vs Brute Force (n = 5,000)")
plt.title("Speedup Over Brute Force at n = 5,000")
for b, s in zip(bars, speedups):
    plt.text(b.get_x() + b.get_width()/2, s + 1, f"{s:.0f}x", ha="center", fontweight="bold")
plt.grid(alpha=0.3, axis="y")
plt.tight_layout()
plt.savefig(f"{FIG}/speedup_bar.png")
plt.close()

print("Charts saved to", FIG)
