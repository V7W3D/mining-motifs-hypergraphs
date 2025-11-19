# Mining Higher-Order Motifs in Hypergraphs

Compact Python tools to enumerate and count higher-order motifs (k=3,4) in hypergraphs.

This repository contains:
- `src/` — library code: hypergraph model, ESU enumerator, canonicalization, baseline and efficient motif counting algorithms.
- `src/dataloaders.py` — dataset loaders (DBLP CSV and `email-Eu` format).
- `examples/` — small example runner.
- `scripts/` — helpers and benchmark runner (`benchmark_motifs.py`, `run_benchmarks.sh`).

Quick start
-----------
1. Install the project locally (editable mode):

```bash
pip install -e .
pip install -r requirements.txt
```

2. Run the small example:

```bash
python3 src/hypergraph_motifs.py --example
```

Dataset loaders
---------------
- DBLP CSV loader: `src/dataloaders.load_dblp(file_path='data/dblp.csv', max_size=4, Hypergraph=Hypergraph)`
  - expects CSV with header and rows: `paper,author,year` (year optional). Groups authors by paper to form hyperedges.
- email-Eu loader: `src/dataloaders.load_email_eu(dir_path='data/email-Eu', max_size=4, Hypergraph=Hypergraph)`
  - expects two files in the directory: `email-Eu-nverts.txt` (counts per simplex) and `email-Eu-simplices.txt` (flat vertex list). Builds simplices by consuming runs of lengths from the nverts file.

Benchmarking
------------
Use the benchmark script to time the algorithms on a dataset:

```bash
# email-Eu directory
python3 scripts/benchmark_motifs.py --file data/email-Eu --dataset email-eu --max-size 4

# DBLP CSV
python3 scripts/benchmark_motifs.py --file data/dblp.csv --dataset dblp --max-size 4
```

Or run the automated installer + benchmarks (will skip missing datasets):

```bash
chmod +x scripts/run_benchmarks.sh
./scripts/run_benchmarks.sh
```

Algorithms implemented
----------------------
- `baseline_count(H, k)` — Algorithm 1: project hypergraph to 2-section, enumerate connected k-node induced subgraphs via ESU, build induced sub-hypergraphs, canonicalize and count.
- `efficient_count_order3(H)` — Algorithm 2: counts size-3 hyperedges directly, then enumerates remaining connected triples (ESU) while skipping already-counted triples.
- `efficient_count_order4(H)` — Algorithm 3: counts size-4 hyperedges, considers unions of adjacent size-3/other edges to form 4-sets, and finally runs ESU for remaining 4-sets.

Notes
-----
- Canonicalization is brute-force for k<=4 (permutations), suitable for small motifs.
- The code uses a list-of-frozensets for edges; consider switching to a set-of-frozensets if you want automatic deduplication of trimmed edges.
- Benchmarks on large datasets can take significant time and memory; run the scripts on a machine with enough resources and consider limiting `--max-size`.

Contributing
------------
If you'd like me to add tests, CI, or optimize inner loops (canonicalization, ESU), tell me which part to focus on and I will implement it.
