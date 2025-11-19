#!/usr/bin/env bash
set -euo pipefail

# Automated setup + benchmark runner for both datasets
# Usage: ./scripts/run_benchmarks.sh

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$ROOT_DIR/logs"
mkdir -p "$LOG_DIR"

echo "[benchmarks] ROOT_DIR=$ROOT_DIR"

echo "[benchmarks] Upgrading pip and installing package in editable mode..."
python3 -m pip install --upgrade pip setuptools wheel
python3 -m pip install -e "$ROOT_DIR"

if [ -f "$ROOT_DIR/requirements.txt" ]; then
  echo "[benchmarks] Installing requirements.txt (if any)"
  python3 -m pip install -r "$ROOT_DIR/requirements.txt" || true
fi

echo "[benchmarks] Running benchmark on email-Eu dataset (if present)"
EMAIL_DIR="$ROOT_DIR/data/email-Eu"
if [ -d "$EMAIL_DIR" ]; then
  OUT="$LOG_DIR/email_eu_benchmark.txt"
  echo "[benchmarks] Running: python3 scripts/benchmark_motifs.py --file $EMAIL_DIR --dataset email-eu --max-size 4" | tee "$OUT"
  python3 "$ROOT_DIR/scripts/benchmark_motifs.py" --file "$EMAIL_DIR" --dataset email-eu --max-size 4 2>&1 | tee -a "$OUT"
  echo "[benchmarks] email-eu benchmark finished; log: $OUT"
else
  echo "[benchmarks] email-Eu dataset directory not found at $EMAIL_DIR — skipping" | tee "$LOG_DIR/email_eu_benchmark.txt"
fi

echo "[benchmarks] Running benchmark on dblp CSV dataset (if present)"
DBLP_FILE="$ROOT_DIR/data/dblp.csv"
if [ -f "$DBLP_FILE" ]; then
  OUT="$LOG_DIR/dblp_benchmark.txt"
  echo "[benchmarks] Running: python3 scripts/benchmark_motifs.py --file $DBLP_FILE --dataset dblp --max-size 4" | tee "$OUT"
  python3 "$ROOT_DIR/scripts/benchmark_motifs.py" --file "$DBLP_FILE" --dataset dblp --max-size 4 2>&1 | tee -a "$OUT"
  echo "[benchmarks] dblp benchmark finished; log: $OUT"
else
  echo "[benchmarks] dblp CSV not found at $DBLP_FILE — skipping" | tee "$LOG_DIR/dblp_benchmark.txt"
fi

echo "[benchmarks] All done. Logs are in $LOG_DIR"
