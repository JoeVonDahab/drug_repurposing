#!/bin/bash

# === Configuration ===
# 1. How many GPUs do you have available?
NUM_GPUS=2

# 2. How many concurrent gnina processes to run on EACH GPU?
JOBS_PER_GPU=50

# 3. Directory containing all your ligand .sdf files
LIGAND_DIR="all_sdf"

# 4. Name of your prepared receptor file
RECEPTOR_FILE="receptor_ready_5tbm.pdb"

# 5. Directory where scored output files will be saved
OUTPUT_DIR="scored"
# === End of Configuration ===


# --- Sanity Checks & Preparation ---
if ! command -v parallel &> /dev/null; then
    echo "ERROR: GNU Parallel is not installed. Please install it first."
    exit 1
fi

ACTUAL_GPUS=$(nvidia-smi -L | wc -l)
if [ "$NUM_GPUS" -gt "$ACTUAL_GPUS" ]; then
    echo "ERROR: Your configuration requests NUM_GPUS=$NUM_GPUS, but only $ACTUAL_GPUS GPUs were found."
    echo "Please set NUM_GPUS to $ACTUAL_GPUS or lower in the script."
    exit 1
fi

if [ ! -d "$LIGAND_DIR" ]; then
    echo "ERROR: Ligand directory not found: $LIGAND_DIR"
    exit 1
fi

if [ ! -f "$RECEPTOR_FILE" ]; then
    echo "ERROR: Receptor file not found: $RECEPTOR_FILE"
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

# --- Create Master Ligand List ---
MASTER_LIST_FILE="all_ligands_to_process.txt"
find "$LIGAND_DIR" -name "*.sdf" > "$MASTER_LIST_FILE"

TOTAL_LIGANDS=$(wc -l < "$MASTER_LIST_FILE")
if [ "$TOTAL_LIGANDS" -eq 0 ]; then
    echo "ERROR: No .sdf files found in '$LIGAND_DIR'."
    rm "$MASTER_LIST_FILE"
    exit 1
fi

# --- Export variables so they are available to the subshells created by parallel ---
export RECEPTOR_FILE
export OUTPUT_DIR
export NUM_GPUS

TOTAL_JOBS=$((NUM_GPUS * JOBS_PER_GPU))

echo "Receptor:      $RECEPTOR_FILE"
echo "Total Ligands: $TOTAL_LIGANDS"
echo "GPUs to use:   $NUM_GPUS"
echo "Jobs per GPU:  $JOBS_PER_GPU"
echo "Total concurrent Docker containers: $TOTAL_JOBS"
echo "----------------------------------------------------"
echo "Starting parallel processing... Progress will be shown below."

# --- Run everything using GNU Parallel ---
cat "$MASTER_LIST_FILE" | parallel \
  -j "$TOTAL_JOBS" \
  --eta \
  --joblog gnina_parallel.log \
  '
    # FINAL FIX: Added parentheses to ensure correct order of operations
    GPU_ID=$((({%} - 1) % NUM_GPUS))

    # Get just the filename for the output file
    base=$(basename "{}" .sdf)

    echo "Starting ligand $base on GPU $GPU_ID"

    docker run --rm --ipc=host --gpus "device=$GPU_ID" \
      -v "$(pwd)":/work \
      -w /work \
      gnina/gnina:latest \
      gnina --score_only --cnn_scoring all \
            -r "$RECEPTOR_FILE" \
            -l "{}" \
            --autobox_ligand "{}" \
            -o "$OUTPUT_DIR/${base}_scored.sdf"
'

# --- Cleanup ---
rm "$MASTER_LIST_FILE"

echo "----------------------------------------------------"
echo "All jobs completed. Check '$OUTPUT_DIR' for results and 'gnina_parallel.log' for a detailed log."