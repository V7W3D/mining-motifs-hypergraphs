"""Benchmark the implemented motif mining algorithms.

Loads a hypergraph (DBLP CSV by default) and times:
- baseline_count(k=3)
- efficient_count_order3
- baseline_count(k=4)
- efficient_count_order4

If `data/dblp.csv` is not present the script falls back to the built-in example hypergraph.
"""
import sys
import os
import time
import argparse

# make repo root importable
sys.path.insert(0, os.path.abspath('.'))

from src.hypergraph_motifs import (
    baseline_count,
    efficient_count_order3,
    efficient_count_order4,
    _example_hypergraph,
)
from src.dataloaders import load_dblp, load_email_eu


def time_fn(fn, *args, repeat=1):
    start = time.perf_counter()
    res = None
    for _ in range(repeat):
        res = fn(*args)
    end = time.perf_counter()
    return res, (end - start) / repeat


def main():
    parser = argparse.ArgumentParser(description='Benchmark motif counting methods')
    parser.add_argument('--file', default='data/dblp.csv', help='path to dblp csv or directory for email-Eu')
    parser.add_argument('--dataset', choices=['auto', 'email-eu', 'dblp'], default='auto',
                        help='dataset type; when set to email-eu, --file is treated as a directory')
    parser.add_argument('--max-size', type=int, default=4, help='max hyperedge size to load')
    parser.add_argument('--repeat', type=int, default=1, help='number of repeats for timing')
    args = parser.parse_args()

    # attempt to load DBLP
    try:
        from src.hypergraph_motifs import Hypergraph
    except Exception:
        Hypergraph = None

    H = None
    if Hypergraph is not None:
        if args.dataset == 'email-eu':
            H = load_email_eu(dir_path=args.file, max_size=args.max_size, Hypergraph=Hypergraph)
        elif args.dataset == 'dblp':
            H = load_dblp(args.file, max_size=args.max_size, Hypergraph=Hypergraph)
        else:  # auto
            if os.path.isdir(args.file):
                # try email-Eu style loader
                H = load_email_eu(dir_path=args.file, max_size=args.max_size, Hypergraph=Hypergraph)
            else:
                # try CSV-style DBLP loader
                H = load_dblp(args.file, max_size=args.max_size, Hypergraph=Hypergraph)

    if H is None:
        print('data file not found or failed to load — using example hypergraph')
        H = _example_hypergraph()

    print('Vertices:', len(H.vertices))
    print('Hyperedges:', len(H.edges))

    # baseline k=3
    counts3_base, t3_base = time_fn(baseline_count, H, 3, repeat=args.repeat)
    print(f'Baseline k=3: {sum(counts3_base.values())} motifs, time={t3_base:.6f}s')

    # efficient order-3
    counts3_eff, t3_eff = time_fn(efficient_count_order3, H, repeat=args.repeat)
    print(f'Efficient order-3: {sum(counts3_eff.values())} motifs, time={t3_eff:.6f}s')

    #baseline k=4
    counts4_base, t4_base = time_fn(baseline_count, H, 4, repeat=args.repeat)
    print(f'Baseline k=4: {sum(counts4_base.values())} motifs, time={t4_base:.6f}s')

    # efficient order-4
    counts4_eff, t4_eff = time_fn(efficient_count_order4, H, repeat=args.repeat)
    print(f'Efficient order-4: {sum(counts4_eff.values())} motifs, time={t4_eff:.6f}s')
    
    # print brief summary table
    print('\nSummary (motifs,count,time[s]):')
    print('k=3 baseline:', len(counts3_base), sum(counts3_base.values()), t3_base)
    print('k=3 efficient:', len(counts3_eff), sum(counts3_eff.values()), t3_eff)
    print('k=4 baseline:', len(counts4_base), sum(counts4_base.values()), t4_base)
    print('k=4 efficient:', len(counts4_eff), sum(counts4_eff.values()), t4_eff)


if __name__ == '__main__':
    main()
