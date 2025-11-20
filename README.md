# Project layout

src/
	hypergraph_motifs.py
	dataloaders.py

examples/

scripts/
	benchmark_motifs.py

run_benchmarks.sh

docs/

Make the runner executable:

```
chmod +x run_benchmarks.sh
```

Make `run_benchmarks.sh` executable so you can run it directly from the shell.

Run the benchmark runner:

```
./run_benchmarks.sh [--dataset email-eu|dblp|all] [--file PATH]
```

Run the benchmark harness; use `--dataset` to choose `email-eu`, `dblp`, or `all`, or pass a dataset file with `--file PATH`.
