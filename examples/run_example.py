"""Example runner for hypergraph motif counting."""
from src.hypergraph_motifs import _example_hypergraph, baseline_count


def run():
    H = _example_hypergraph()
    print("Vertices:", sorted(H.vertices))
    print("Edges:", [sorted(e) for e in H.edges])
    for k in (3, 4):
        counts = baseline_count(H, k=k)
        print(f"\nMotif counts for k={k}:")
        for rep, c in counts.items():
            print(rep, "->", c)


if __name__ == '__main__':
    run()
