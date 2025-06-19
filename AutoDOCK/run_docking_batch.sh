#!/bin/bash

# === Configuration ===
# 1. FULL PATH to your compiled AutoDock-GPU executable
AUTODOCK_GPU_EXEC="/home/joe/projects/AutoDOCK/AutoDock-GPU/bin/autodock_gpu_128wi"

# 2. Name of your PRE-CALCULATED receptor grid map file (.maps.fld)
MAP_FILE_FLD_FILENAME="myreceptor_targeted.maps.fld"

# 3. Name of the directory containing your ligand PDBQT files
LIGAND_DIR="ligands_pdbqt"

# 4. Name of the directory where docking results (DLG files) will be saved
OUTPUT_DIR="docking_results_compiled"

# 5. Docking run parameters
NUM_RUNS="10"        # Number of docking runs per ligand
#GPU_ID="0"         # Uncomment if you need to target a specific GPU

# === End of Configuration ===

CURRENT_WORK_DIR=$(pwd)   # script must be run from the folder containing the .maps.fld

# Create output directory if it doesn't exist
if [ ! -d "$OUTPUT_DIR" ]; then
    mkdir -p "$OUTPUT_DIR"
    echo "Created output directory: $OUTPUT_DIR"
fi

# Sanity checks
if [ ! -x "$AUTODOCK_GPU_EXEC" ]; then
    echo "ERROR: AutoDock-GPU binary not found or not executable at: $AUTODOCK_GPU_EXEC"
    exit 1
fi

if [ ! -f "$MAP_FILE_FLD_FILENAME" ]; then
    echo "ERROR: Receptor map file not found: $MAP_FILE_FLD_FILENAME"
    echo "       Make sure you ran generate_grid_maps.sh successfully."
    exit 1
fi

if [ ! -d "$LIGAND_DIR" ]; then
    echo "ERROR: Ligand directory not found: $LIGAND_DIR"
    exit 1
fi

echo "Batch docking starting..."
echo "  GPU binary:    $AUTODOCK_GPU_EXEC"
echo "  Grid map file: $MAP_FILE_FLD_FILENAME"
echo "  Ligands from:  $LIGAND_DIR"
echo "  Results to:    $OUTPUT_DIR"
echo "-------------------------------------------"

for ligand_path in "$LIGAND_DIR"/*.pdbqt; do
    [ -f "$ligand_path" ] || continue
    ligand_file=$(basename "$ligand_path")
    ligand_name="${ligand_file%.pdbqt}"

    echo "Processing ligand: $ligand_file"

    map_file_abs="$CURRENT_WORK_DIR/$MAP_FILE_FLD_FILENAME"
    ligand_abs="$CURRENT_WORK_DIR/$LIGAND_DIR/$ligand_file"
    output_base="$CURRENT_WORK_DIR/$OUTPUT_DIR/${ligand_name}_docked"

    # Run AutoDock-GPU with proper -resnam quoting
    "$AUTODOCK_GPU_EXEC" \
      --ffile "$map_file_abs" \
      --lfile "$ligand_abs" \
      --nrun "$NUM_RUNS" \
      -resnam "$output_base"

    exit_code=$?
    dlg_file="${output_base}.dlg"

    if [ $exit_code -eq 0 ] && [ -f "$dlg_file" ]; then
        echo "  ✓ Docking succeeded: $dlg_file"
    elif [ $exit_code -eq 0 ]; then
        echo "  ! Warning: exit 0 but no DLG created at: $dlg_file"
    else
        echo "  ✗ Error: docking failed (exit code $exit_code) for $ligand_file"
    fi

    echo "-------------------------------------------"
done

echo "Batch docking complete. Check '$OUTPUT_DIR' for .dlg files."
