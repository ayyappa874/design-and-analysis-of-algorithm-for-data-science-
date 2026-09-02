# Closest-Pair-of-Points — DAA Assignment (CSA0615)

Brute Force, Divide-and-Conquer, and Hybrid algorithms for the Closest-Pair-of-Points
problem, benchmarked on the real-world OpenFlights airports dataset (7,698 records).

## Files
- `closest_pair.py` — the three algorithm implementations + shared Metrics counter
- `experiment.py` — loads the dataset, projects coordinates, runs the benchmark
- `threshold_sweep.py` — justifies the hybrid algorithm's brute-force switch-over threshold
- `make_charts.py` — generates all report figures from the results
- `results.json` / `results.csv` — benchmark output
- `threshold_sweep.json` — threshold sweep output

## Run it
```bash
pip install matplotlib
python3 experiment.py
python3 threshold_sweep.py
python3 make_charts.py
```

Dataset: [OpenFlights Airports Database](https://github.com/jpatokal/openflights)
(download `data/airports.dat` into a local `data/` folder before running, or point
`DATA_PATH` in `experiment.py` at your own copy).

## Results summary (n = 7,698)
| Algorithm | Time | Distance calls |
|---|---|---|
| Brute Force | ~7.5s (extrapolated) | ~29.6M |
| Divide & Conquer | 58 ms | 79,328 |
| Hybrid (threshold=20) | 40 ms | 70,823 |
