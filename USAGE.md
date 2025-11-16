Hypergraph motifs baseline counting

This repository provides a small Python implementation of the "Algorithm 1 Baseline: Counting higher-order motifs" for hypergraphs (k in {3,4}).

Files added:
- `src/hypergraph_motifs.py`: implementation of Hypergraph, projection, ESU enumeration, connectivity check, canonical isomorphism for small motifs, and `baseline_count`.
- `examples/run_example.py`: small example runner.

Quick start:

1) Run the built-in example:

```bash
python3 src/hypergraph_motifs.py --example
```

2) Or run the example script:

```bash
python3 examples/run_example.py
```

Usage as a library:

```python
from src.hypergraph_motifs import Hypergraph, baseline_count
H = Hypergraph(["a","b","c"],["b","c","d"])
counts = baseline_count(H, k=3)
print(counts)
```

Notes:
- For k <= 4 the isomorphism test uses brute-force permutations (k! permutations), which is fine for small k but not suitable for larger motifs.
- The ESU enumerator yields connected induced subgraphs in the graph projection of the hypergraph; for each such vertex set we build the induced hypergraph and check hypergraph connectivity before counting.
