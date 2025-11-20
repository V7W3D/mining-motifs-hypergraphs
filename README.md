# Mining motifs in hypergraphs

Minimal research codebase for counting small higher-order motifs in hypergraphs.

## Project layout

A conventional layout showing top-level files and important folders:

```
.
├── src/                   # Library source code
│   ├── hypergraph_motifs.py
│   └── dataloaders.py
├── examples/              # Example runners and small inputs
├── scripts/               # Utility scripts
│   └── benchmark_motifs.py
├── run_benchmarks.sh      # Top-level benchmark runner (bash)
├── docs/                  # Reports and documentation
│   └── report_fr.md
├── requirements.txt       # Python dependencies
├── pyproject.toml         # Packaging / project metadata
└── README.md              # This file
```

## Quick start

Make the runner executable so it can be launched directly from the shell:

```
chmod +x run_benchmarks.sh
```

Run the benchmark runner; choose a dataset or provide a path to a dataset file:

```
./run_benchmarks.sh [--dataset email-eu|dblp|all] [--file PATH]
```

- `chmod +x run_benchmarks.sh`: makes the benchmark script executable.
- `./run_benchmarks.sh ...`: launches the benchmarking harness; use `--dataset` to pick a bundled dataset or `--file` to point to a custom file.

For more details on available options, open `scripts/benchmark_motifs.py` or run the script with `--help`.

