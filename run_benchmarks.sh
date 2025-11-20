#!/usr/bin/env bash
set -euo pipefail

# Automated setup + benchmark runner for both datasets (relocated to project root)
# Usage: ./run_benchmarks.sh

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="./logs"
mkdir -p "$LOG_DIR"

DATASET="all"
FILEPATH=""

usage(){
  cat <<EOF
Usage: $0 [--dataset email-eu|dblp|all] [--file PATH] [--help]

Options:
  --dataset   which dataset to run: 'email-eu', 'dblp', or 'all' (default: all)
  --file      path to dataset (overrides default path for the chosen dataset)
  --help,-h   show this help
EOF
}

# parse args
while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --dataset)
      DATASET="$2"; shift 2;;
    --file)
      FILEPATH="$2"; shift 2;;
    -h|--help)
      usage; exit 0;;
    *)
      echo "Unknown arg: $1"; usage; exit 1;;
  esac
done

echo "[benchmarks] ROOT_DIR=$ROOT_DIR"

echo "[benchmarks] Upgrading pip and installing package in editable mode..."
python3 -m pip install --upgrade pip setuptools wheel
python3 -m pip install -e .

if [ "$DATASET" = "all" ]; then
  if [ -n "$FILEPATH" ]; then
    echo "[benchmarks] Warning: --file given but --dataset=all; ignoring --file" >&2
  fi

  echo "[benchmarks] Running benchmark on email-Eu dataset (if present)"
  EMAIL_DIR="./data/email-Eu"
  if [ -d "$EMAIL_DIR" ]; then
    OUT="$LOG_DIR/email_eu_benchmark.txt"
    echo "[benchmarks] Running: python3 scripts/benchmark_motifs.py --file $EMAIL_DIR --dataset email-eu --max-size 4" | tee "$OUT"
    python3 "scripts/benchmark_motifs.py" --file "$EMAIL_DIR" --dataset email-eu --max-size 4 2>&1 | tee -a "$OUT"
    echo "[benchmarks] email-eu benchmark finished; log: $OUT"
  else
    echo "[benchmarks] email-Eu dataset directory not found at $EMAIL_DIR — skipping" | tee "$LOG_DIR/email_eu_benchmark.txt"
  fi

  echo "[benchmarks] Running benchmark on dblp CSV dataset (if present)"
  DBLP_FILE="./data/dblp.csv"
  if [ -f "$DBLP_FILE" ]; then
    OUT="$LOG_DIR/dblp_benchmark.txt"
    echo "[benchmarks] Running: python3 scripts/benchmark_motifs.py --file $DBLP_FILE --dataset dblp --max-size 4" | tee "$OUT"
    python3 "scripts/benchmark_motifs.py" --file "$DBLP_FILE" --dataset dblp --max-size 4 2>&1 | tee -a "$OUT"
    echo "[benchmarks] dblp benchmark finished; log: $OUT"
  else
    echo "[benchmarks] dblp CSV not found at $DBLP_FILE — skipping" | tee "$LOG_DIR/dblp_benchmark.txt"
  fi

else
  if [ "$DATASET" = "email-eu" ]; then
    EMAIL_DIR="$FILEPATH"
    if [ -z "$EMAIL_DIR" ]; then
      EMAIL_DIR="./data/email-Eu"
    fi
    echo "[benchmarks] Running: python3 scripts/benchmark_motifs.py --file $EMAIL_DIR --dataset email-eu --max-size 4"
    OUT="$LOG_DIR/email_eu_benchmark.txt"
    if [ -d "$EMAIL_DIR" ]; then
      python3 "scripts/benchmark_motifs.py" --file "$EMAIL_DIR" --dataset email-eu --max-size 4 2>&1 | tee "$OUT"
      echo "[benchmarks] email-eu benchmark finished; log: $OUT"
    else
      echo "[benchmarks] Provided email-eu path not found: $EMAIL_DIR"; exit 1
    fi

  elif [ "$DATASET" = "dblp" ]; then
    DBLP_FILE="$FILEPATH"
    if [ -z "$DBLP_FILE" ]; then
      DBLP_FILE="./data/dblp.csv"
    fi
    echo "[benchmarks] Running: python3 scripts/benchmark_motifs.py --file $DBLP_FILE --dataset dblp --max-size 4"
    OUT="$LOG_DIR/dblp_benchmark.txt"
    if [ -f "$DBLP_FILE" ]; then
      python3 "scripts/benchmark_motifs.py" --file "$DBLP_FILE" --dataset dblp --max-size 4 2>&1 | tee "$OUT"
      echo "[benchmarks] dblp benchmark finished; log: $OUT"
    else
      echo "[benchmarks] Provided dblp file not found: $DBLP_FILE"; exit 1
    fi

  else
    echo "Unknown dataset: $DATASET"; usage; exit 1
  fi
fi

echo "[benchmarks] All done. Logs are in $LOG_DIR"
