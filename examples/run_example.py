"""Example runner for hypergraph motif counting."""
import sys
import os
# allow running examples from repo root where `src` may not be on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.hypergraph_motifs import _example_hypergraph, baseline_count, efficient_count_order3


def run():
    H = _example_hypergraph()
    print("Vertices:", sorted(H.vertices))
    print("Edges:", [sorted(e) for e in H.edges])
    for k in (3, 4):
        counts = baseline_count(H, k=k)
        print(f"\nMotif counts for k={k}:")
        for rep, c in counts.items():
            print(rep, "->", c)
    print("\nEfficient order-3 counting (Algorithm 2):")
    counts_e = efficient_count_order3(H)
    for rep, c in counts_e.items():
        print(rep, "->", c)
    print("\nEfficient order-4 counting (Algorithm 3):")
    from src.hypergraph_motifs import efficient_count_order4
    counts_e4 = efficient_count_order4(H)
    for rep, c in counts_e4.items():
        print(rep, "->", c)


if __name__ == '__main__':
    run()
