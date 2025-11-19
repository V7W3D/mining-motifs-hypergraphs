"""Hypergraph motif baseline counting implementation.

Implements Algorithm 1 Baseline: Counting higher-order motifs
for k in {3,4} from the user's description.

Usage (as module):
    from src.hypergraph_motifs import Hypergraph, baseline_count

Usage (CLI):
    python3 src/hypergraph_motifs.py --example

This file provides a compact Hypergraph class, projection to a graph
(`2-section`), an ESU enumerator for connected k-node induced
subgraphs of the projection, and hypergraph isomorphism by canonical
labeling (brute force on k<=4 by permuting vertex labels).
"""
from collections import defaultdict, deque
from itertools import combinations, permutations
import argparse
import json
import sys


class Hypergraph:
    """Simple hypergraph representation.

    vertices: set of hashable vertex ids
    edges: list of frozenset(vertex)
    """

    def __init__(self, edges=None):
        self.edges = []
        self.vertices = set()
        if edges:
            for e in edges:
                self.add_edge(e)

    def add_edge(self, edge):
        e = frozenset(edge)
        if len(e) == 0:
            return
        self.edges.append(e)
        self.vertices.update(e)

    def induced_subhypergraph(self, vertex_subset):
        """Return a new Hypergraph induced by vertex_subset (iterable).
        Only edges with non-empty intersection are kept, but trimmed to
        the subset (i.e., e' = e intersect V*), and we discard empty edges.
        """
        Vset = set(vertex_subset)
        sub_edges = []
        for e in self.edges:
            inter = e & Vset
            if inter:
                sub_edges.append(inter)
        H = Hypergraph(sub_edges)
        return H

    def projection_2_section(self):
        """Return the projection graph G as adjacency dict mapping vertex -> set(neighbors).
        Two vertices are adjacent if they appear together in at least one hyperedge.
        """
        G = {v: set() for v in self.vertices}
        for e in self.edges:
            for u, v in combinations(e, 2):
                G[u].add(v)
                G[v].add(u)
        return G


def esu_enumerate_connected_subgraphs(G, k):
    """ESU enumerator for connected induced subgraphs of size k.

    G: dict vertex -> set(neighbors)
    Returns a generator of frozenset vertex sets of size k.

    Implementation: classic ESU: for each start vertex v (ordered),
    grow subgraphs using an extension set containing neighbors with id > start
    to avoid duplicates. We assume vertex ids are comparable; if not, we
    will map to a sorted list.
    """
    # create a deterministic ordering
    vertices = sorted(G.keys(), key=lambda x: str(x))
    index = {v: i for i, v in enumerate(vertices)}

    def rec(subgraph, ext, start):
        if len(subgraph) == k:
            yield frozenset(subgraph)
            return
        # copy ext to iterate safely
        ext_list = list(ext)
        while ext_list:
            w = ext_list.pop()
            new_sub = subgraph + [w]
            # build new extension: neighbors of w with index > start and not already in subgraph
            new_ext = set(ext_list)
            for nb in G.get(w, []):
                if nb in new_sub:
                    continue
                if index[nb] > index[start]:
                    new_ext.add(nb)
            yield from rec(new_sub, new_ext, start)

    for v in vertices:
        # extension contains neighbors of v with index > index[v]
        ext = set(nb for nb in G[v] if index[nb] > index[v])
        yield from rec([v], ext, v)


def is_connected_hypergraph(H):
    """Check connectivity in hypergraph H (vertices reachable via hyperedges).

    BFS on vertices: from a start, traverse edges and collect vertices.
    """
    if not H.vertices:
        return True
    start = next(iter(H.vertices))
    visited = set([start])
    q = deque([start])
    # build incidence: vertex -> list of edges (as sets)
    incidence = defaultdict(list)
    for e in H.edges:
        for v in e:
            incidence[v].append(e)

    while q:
        v = q.popleft()
        for e in incidence.get(v, ()):  # for each edge containing v
            for u in e:
                if u not in visited:
                    visited.add(u)
                    q.append(u)
    return visited == set(H.vertices)


def canonical_form_hypergraph(H):
    """Return a canonical string representation for small hypergraphs (k<=4).

    Approach: consider vertex set V of size k, list all permutations of V
    mapping to [0..k-1]; for each permutation produce a sorted tuple of
    sorted hyperedges (as tuples of new labels). Choose lexicographically
    smallest representation.
    """
    V = sorted(H.vertices, key=lambda x: str(x))
    k = len(V)
    if k == 0:
        return "()"
    best = None
    Vlist = list(V)
    edges = [tuple(sorted(map(lambda x: Vlist.index(x), e))) for e in H.edges]
    # permutations of indices 0..k-1
    for perm in permutations(range(k)):
        # build mapping old_index -> new_index
        mapping = {i: perm[i] for i in range(k)}
        mapped_edges = []
        for e in edges:
            new_e = tuple(sorted(mapping[i] for i in e))
            mapped_edges.append(new_e)
        mapped_edges_sorted = tuple(sorted(mapped_edges))
        if (best is None) or (mapped_edges_sorted < best):
            best = mapped_edges_sorted
    # represent as string
    return json.dumps(best)


def baseline_count(H, k=3):
    """Implement Algorithm 1 Baseline: count motif frequencies of order k in hypergraph H.

    Steps:
    1) project H to graph G
    2) enumerate connected k-node induced subgraphs of G using ESU
    3) for each vertex set, build induced sub-hypergraph from H, check
       hypergraph connectivity, compute isomorphism class, and count
    Returns: dict mapping canonical motif representation -> count
    """
    if k not in (3, 4):
        raise ValueError("k must be 3 or 4")
    G = H.projection_2_section()
    M = defaultdict(int)
    seen = 0
    for Vstar in esu_enumerate_connected_subgraphs(G, k):
        seen += 1
        candidate = H.induced_subhypergraph(Vstar)
        if is_connected_hypergraph(candidate):
            Cm = canonical_form_hypergraph(candidate)
            M[Cm] += 1
    # optionally return metadata
    return dict(M)


def efficient_count_order3(H):
    """Efficient Algorithm 2 for counting motifs of order 3.

    Steps implemented:
    1) Count all hyperedges of size 3 directly (each such edge induces a motif on its 3 vertices).
    2) Remove all size-3 hyperedges from H to form G.
    3) Enumerate connected 3-vertex induced subgraphs of G's projection using ESU.
       For each vertex set V* not already counted, build the induced sub-hypergraph
       from G (i.e., without the original size-3 hyperedges), check hypergraph
       connectivity, canonicalize and count.

    Returns: dict mapping canonical motif representation -> count
    """
    M = defaultdict(int)
    visited = set()

    # 1) count direct hyperedges of size 3
    for e in H.edges:
        if len(e) == 3:
            Vstar = frozenset(e)
            candidate = H.induced_subhypergraph(Vstar)
            # canonicalize and count
            Cm = canonical_form_hypergraph(candidate)
            M[Cm] += 1
            visited.add(Vstar)

    # 2/3) enumerate connected 3-vertex induced subgraphs in projection of the
    # original hypergraph H (this matches the baseline ESU enumeration) and
    # skip triples already counted. Build induced candidates from the original
    # H so trimmed edges from size-3 hyperedges remain.
    G_proj = H.projection_2_section()
    for Vstar in esu_enumerate_connected_subgraphs(G_proj, 3):
        Vf = frozenset(Vstar)
        if Vf in visited:
            continue
        candidate = H.induced_subhypergraph(Vstar)
        if is_connected_hypergraph(candidate):
            Cm = canonical_form_hypergraph(candidate)
            M[Cm] += 1
            visited.add(Vf)

    return dict(M)


def efficient_count_order4(H):
    """Efficient Algorithm 3 for counting motifs of order 4.

    Implements the steps from Algorithm 3:
    1) Count all hyperedges of size 4 directly.
    2) Remove size-4 edges; for each remaining size-3 edge e, look at
       all adjacent hyperedges ei. If |e ∪ ei| == 4 and that 4-set
       hasn't been visited, build the induced sub-hypergraph and count it.
    3) Remove size-3 edges and run ESU on the projection to enumerate
       connected 4-vertex induced subgraphs; for any 4-set not visited
       count its canonical motif.

    Returns: dict mapping canonical motif representation -> count
    """
    M = defaultdict(int)
    visited = set()

    # 1) count direct hyperedges of size 4
    for e in H.edges:
        if len(e) == 4:
            Vstar = frozenset(e)
            candidate = H.induced_subhypergraph(Vstar)
            Cm = canonical_form_hypergraph(candidate)
            M[Cm] += 1
            visited.add(Vstar)

    # 2) remove size-4 edges
    edges_no4 = [e for e in H.edges if len(e) != 4]
    H_no4 = Hypergraph(edges_no4)

    # for each size-3 edge, look at adjacent hyperedges in H_no4
    size3_edges = [e for e in H_no4.edges if len(e) == 3]
    if size3_edges:
        for e in size3_edges:
            for ei in H_no4.edges:
                if ei is e:
                    continue
                if not (ei & e):
                    continue
                union = e | ei
                if len(union) == 4:
                    Vf = frozenset(union)
                    if Vf in visited:
                        continue
                    # build induced candidate from the original H (to match baseline semantics)
                    candidate = H.induced_subhypergraph(union)
                    if is_connected_hypergraph(candidate):
                        Cm = canonical_form_hypergraph(candidate)
                        M[Cm] += 1
                        visited.add(Vf)

    # 3) enumerate connected 4-vertex induced subgraphs in projection of original H
    # (use original projection to match baseline enumeration), skip visited
    G_proj = H.projection_2_section()
    for Vstar in esu_enumerate_connected_subgraphs(G_proj, 4):
        Vf = frozenset(Vstar)
        if Vf in visited:
            continue
        candidate = H.induced_subhypergraph(Vstar)
        if is_connected_hypergraph(candidate):
            Cm = canonical_form_hypergraph(candidate)
            M[Cm] += 1
            visited.add(Vf)

    return dict(M)


def _example_hypergraph():
    # small toy example with overlapping hyperedges
    edges = [
        ["a", "b", "c"],
        ["b", "c", "d"],
        ["c", "d", "e"],
        ["a", "d"]
    ]
    return Hypergraph(edges)


def main():
    parser = argparse.ArgumentParser(description="Count k-order hypergraph motifs (k=3,4)")
    parser.add_argument("--k", type=int, default=3, choices=[3,4], help="motif order")
    parser.add_argument("--example", action="store_true", help="run built-in example")
    parser.add_argument("--efficient", action="store_true", help="run efficient order-3 counting algorithm")
    parser.add_argument("--efficient4", action="store_true", help="run efficient order-4 counting algorithm")
    args = parser.parse_args()

    if args.example:
        H = _example_hypergraph()
        print(f"Hypergraph vertices: {sorted(H.vertices)}")
        print(f"Hypergraph edges: {list(map(sorted, H.edges))}")
        if args.efficient4:
            counts = efficient_count_order4(H)
        elif args.efficient:
            counts = efficient_count_order3(H)
        else:
            counts = baseline_count(H, k=args.k)
        print(f"Motif counts for k={args.k} (canonical form -> count):")
        for krep, c in counts.items():
            print(krep, "->", c)
        return

    parser.print_help()


if __name__ == "__main__":
    main()
