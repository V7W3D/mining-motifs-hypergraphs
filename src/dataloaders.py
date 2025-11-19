"""Data loader utilities for higher-order hypergraph datasets.

Provides a loader for the DBLP-style CSV where each row associates a paper
with an author (paper,author,year). The loader groups authors by paper and
creates hyperedges from the set of authors per paper.

Functions:
- load_dblp(file_path='data/dblp.csv', max_size=4): returns Hypergraph

If the file is missing, the loader does not raise but returns None.
"""
from typing import Optional
import os


def load_dblp(file_path: str = 'data/dblp.csv', max_size: int = 4, Hypergraph=None):
    """Load DBLP-format CSV and return a Hypergraph instance.

    file format: CSV with header, rows like: paper,author,year

    Parameters:
    - file_path: path to CSV file
    - max_size: maximum hyperedge size to include (keep edges with 2 <= size <= max_size)
    - Hypergraph: the Hypergraph class to instantiate (passed to avoid circular imports)

    Returns: Hypergraph instance or None if file not found.
    """
    if Hypergraph is None:
        raise ValueError("Hypergraph class must be provided")

    if not os.path.exists(file_path):
        return None

    graph = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if i == 0:
            continue
        l = line.strip()
        if not l:
            continue
        parts = l.split(',')
        if len(parts) < 2:
            continue
        # expecting paper,author,year (year optional)
        paper = parts[0].strip()
        author = parts[1].strip()
        if paper in graph:
            graph[paper].append(author)
        else:
            graph[paper] = [author]

    edges = set()
    for p, authors in graph.items():
        tup = tuple(sorted(set(authors)))
        if len(tup) > 1 and len(tup) <= max_size:
            edges.add(tup)

    # build Hypergraph
    H = Hypergraph(list(edges))
    return H


def load_email_eu(dir_path: str = 'data/email-Eu', max_size: int = 4, Hypergraph=None):
    """Load the email-Eu dataset from a directory containing
    'email-Eu-nverts.txt' and 'email-Eu-simplices.txt'.

    The format expected (following the example loader):
    - 'email-Eu-nverts.txt' contains one integer per line giving the
      number of vertices in each hyperedge (simplex) in order.
    - 'email-Eu-simplices.txt' contains a flat list of vertex ids,
      one integer per line; consecutive runs of lengths from the
      nverts file form each simplex.

    Parameters:
    - dir_path: directory containing the dataset files
    - max_size: maximum hyperedge size to include (keep edges with 2 <= size <= max_size)
    - Hypergraph: Hypergraph class to construct; required

    Returns: Hypergraph instance or None if files not found or Hypergraph not provided.
    """
    if Hypergraph is None:
        raise ValueError("Hypergraph class must be provided")

    name = 'email-Eu'
    a_path = os.path.join(dir_path, f'{name}-nverts.txt')
    b_path = os.path.join(dir_path, f'{name}-simplices.txt')
    if not os.path.exists(a_path) or not os.path.exists(b_path):
        return None

    with open(a_path, 'r', encoding='utf-8') as fa:
        v_lines = [line.strip() for line in fa if line.strip()]
    with open(b_path, 'r', encoding='utf-8') as fb:
        s_lines = [line.strip() for line in fb if line.strip()]

    try:
        v = list(map(int, v_lines))
        s = list(map(int, s_lines))
    except ValueError:
        # unexpected format
        return None

    edges = set()
    tot = set()

    idx = 0
    for count in v:
        # take next `count` integers from s
        if count <= 0:
            e = ()
        else:
            block = s[idx: idx + count]
            idx += count
            e = tuple(sorted(block))
        tot.add(e)
        if len(e) > 1 and len(e) <= max_size:
            edges.add(e)

    H = Hypergraph(list(edges))
    return H
