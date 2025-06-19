#!/usr/bin/env bash
# This script scores a batch of PDBQT files using the --xraylfile method
# to get the energy of a fixed pose without moving it.

# Exit immediately if a command fails or a variable is unset.
set -euo pipefail

# === Configuration ===
AUTODOCK_GPU_EXEC="/home/joe/projects/AutoDOCK/AutoDock-GPU/bin/autodock_gpu_128wi"
MAP_FILE="myreceptor_targeted.maps.fld"
LIGAND_DIR="ligands_pdbqt_diffdock"
FINAL_OUTPUT_DIR="final_scores"
# === End of Configuration ===


# --- 1. Preparation ---
echo "--- Preparing ligand lists for 2 GPUs ---"
mkdir -p "$FINAL_OUTPUT_DIR"

# Create a master list of all PDBQT files to be processed
find "$LIGAND_DIR" -name '*.pdbqt' | sort > all_ligands.lst

if [[ ! -s all_ligands.lst ]]; then
    echo "❌ ERROR: No PDBQT files found in the '$LIGAND_DIR' directory." >&2
    exit 1
fi

# Split the master list into two temporary files for each GPU
split -n l/2 -d -a 1 all_ligands.lst lig_batch_
GPU1_LIST=lig_batch_0
GPU2_LIST=lig_batch_1


# --- 2. Scoring Function Definition ---
# This function processes a list of ligands for one GPU
score_batch () {
    local ligand_list_file=$1
    local gpu_device_num=$2
    local output_csv="${FINAL_OUTPUT_DIR}/scores_gpu${gpu_device_num}.csv"

    # Create the header for the output CSV file
    echo "ligand_name,binding_energy_kcal_mol" > "$output_csv"

    # Loop through each ligand in the list
    while read -r ligand_path; do
        # This command block runs AD-GPU on a single ligand
        # and extracts just the binding energy (delta G).
        delta_g=$("$AUTODOCK_GPU_EXEC" \
                    --lfile "$ligand_path" \
                    --xraylfile "$ligand_path" \
                    --ffile "$MAP_FILE" \
                    --rlige 1 \
                    --nrun 1 --nev 0 --heuristics 0 --autostop 0 \
                    --dlgoutput 0 --xmloutput 0 \
                    --devnum "$gpu_device_num" \
                    | awk '/RefLig/{getline; print $2}') # This extracts the score

        # Write the ligand name and its score to the CSV
        echo "$(basename "$ligand_path" .pdbqt),$delta_g" >> "$output_csv"
    done < "$ligand_list_file"
}


# --- 3. Execution ---
echo "--- Launching parallel scoring on 2 GPUs ---"

# Launch the scoring function for each GPU in the background
score_batch "$GPU1_LIST" 1 &
PID1=$!
score_batch "$GPU2_LIST" 2 &
PID2=$!

echo "Scoring jobs running in background (PIDs $PID1, $PID2)."
echo "Waiting for completion..."

# Wait for both background jobs to finish and check their status
wait $PID1
wait $PID2

# --- 4. Cleanup ---
rm lig_batch_0 lig_batch_1 all_ligands.lst
echo "✅  Finished. Check for results in the '${FINAL_OUTPUT_DIR}' directory."