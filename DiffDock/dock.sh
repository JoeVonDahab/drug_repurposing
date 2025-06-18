#!/usr/bin/env bash
set -euo pipefail

echo "--- Step 1 of 4: Preparing Docking Jobs ---"
python create_ligand_csv.py

if [[ ! -s all_ligands.csv ]]; then
  echo "❌ FATAL ERROR: all_ligands.csv was not created or is empty." >&2
  exit 1
fi
echo "✅ Master list 'all_ligands.csv' created."

echo "--- Step 2 of 4: Splitting Jobs for GPUs ---"
header=$(head -n 1 all_ligands.csv)
body_file=$(mktemp)
tail -n +2 all_ligands.csv > "$body_file"
total_ligands=$(wc -l < "$body_file")
half_ligands=$(((total_ligands + 1) / 2))

echo "Total ligands to dock: $total_ligands"
echo "Allocating $half_ligands ligands to GPU0, and $((total_ligands - half_ligands)) to GPU1."

echo "$header" > ligands_gpu0.csv
head -n "$half_ligands" "$body_file" >> ligands_gpu0.csv
echo "$header" > ligands_gpu1.csv
tail -n +"$((half_ligands + 1))" "$body_file" >> ligands_gpu1.csv
rm "$body_file"
echo "✅ Job lists successfully created."

echo "--- Step 3 of 4: Preparing Output Directories ---"
rm -rf results_gpu0 results_gpu1
mkdir -p results_gpu0 results_gpu1
echo "✅ Output directories are ready."

echo "--- Step 4 of 4: LAUNCHING DOCKING ---"
# Launch processes and redirect output to log files for easy debugging
CUDA_VISIBLE_DEVICES=0 python -m inference --protein_ligand_csv ligands_gpu0.csv --out_dir results_gpu0 > gpu0.log 2>&1 &
pid0=$!
CUDA_VISIBLE_DEVICES=1 python -m inference --protein_ligand_csv ligands_gpu1.csv --out_dir results_gpu1 > gpu1.log 2>&1 &
pid1=$!

echo "✅ Docking is running in the background."
echo "   - GPU 0 PID: $pid0. Log: gpu0.log"
echo "   - GPU 1 PID: $pid1. Log: gpu1.log"

wait "$pid0"
status0=$?
wait "$pid1"
status1=$?

if [[ $status0 -ne 0 || $status1 -ne 0 ]]; then
  echo -e "\n🔥🔥🔥 ERROR: Docking job(s) failed! 🔥🔥🔥" >&2
  echo "Exit code GPU0: $status0 | Exit code GPU1: $status1" >&2
  echo "Please check gpu0.log and gpu1.log for specific errors." >&2
  exit 1
fi

echo -e "\n🎉🎉🎉 Docking Pipeline Has Finished Successfully! 🎉🎉🎉"