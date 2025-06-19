#!/bin/bash

# === Configuration ===
# 1. Path to the python interpreter in your 'autodock' conda environment
PYTHON_EXEC="/home/joe/miniconda3/envs/autodock/bin/python"

# 2. Path to your MGLTools installation directory
MGLTOOLS_ROOT="/home/joe/miniconda3/envs/autodock/MGLToolsPckgs"

# 3. Full path to the MGLTools script for extracting the lowest energy ligand
CONVERT_SCRIPT="${MGLTOOLS_ROOT}/AutoDockTools/Utilities24/write_lowest_energy_ligand.py"

# 4. Source directory containing your .dlg files
SOURCE_DIR="docking_results_compiled"

# 5. Destination directory for the converted .pdbqt files
DEST_DIR="docked_converted"
# === End of Configuration ===

echo "Starting DLG to PDBQT conversion..."
echo "Source DLG directory: $SOURCE_DIR"
echo "Destination PDBQT directory: $DEST_DIR"
echo "Using MGLTools script: $CONVERT_SCRIPT"
echo "-------------------------------------------"

export MGLTOOLS="$MGLTOOLS_ROOT"
export PYTHONPATH="${MGLTOOLS}:${PYTHONPATH}"

if [ ! -x "$PYTHON_EXEC" ]; then
    echo "ERROR: Python interpreter not found or not executable at '$PYTHON_EXEC'"
    exit 1
fi

if [ ! -f "$CONVERT_SCRIPT" ]; then
    echo "ERROR: MGLTools script not found at '$CONVERT_SCRIPT'"
    exit 1
fi

if [ ! -d "$SOURCE_DIR" ]; then
    echo "ERROR: Source directory '$SOURCE_DIR' not found."
    exit 1
fi

mkdir -p "$DEST_DIR"
if [ ! -d "$DEST_DIR" ]; then
    echo "ERROR: Could not create destination directory '$DEST_DIR'."
    exit 1
fi

# Use find to safely iterate over .dlg files, especially if there are many
# -maxdepth 1 ensures it only looks in the immediate SOURCE_DIR, not subdirectories
# -print0 and read -d $'\0' handle filenames with spaces or special characters safely

echo "Looking for .dlg files in '$SOURCE_DIR'..."
file_count=$(find "$SOURCE_DIR" -maxdepth 1 -name "*.dlg" -type f | wc -l)

if [ "$file_count" -eq 0 ]; then
    echo "No .dlg files found in '$SOURCE_DIR'. Exiting."
    exit 0
fi
echo "Found $file_count .dlg files to process."


find "$SOURCE_DIR" -maxdepth 1 -name "*.dlg" -type f -print0 | while IFS= read -r -d $'\0' dlg_file_path; do
    dlg_filename=$(basename "$dlg_file_path")
    base_name="${dlg_filename%.dlg}"
    output_pdbqt_path="$DEST_DIR/${base_name}_best_pose.pdbqt"

    echo "Processing: $dlg_filename"

    "$PYTHON_EXEC" "$CONVERT_SCRIPT" -f "$dlg_file_path" -o "$output_pdbqt_path"

    if [ $? -eq 0 ] && [ -f "$output_pdbqt_path" ]; then
        echo "  Successfully converted to: $output_pdbqt_path"
    else
        echo "  ERROR: Conversion failed for '$dlg_filename'. Check for errors above or if output file was created."
    fi
    echo "---"
done

echo "-------------------------------------------"
echo "Batch DLG to PDBQT conversion finished."
echo "Converted files are in: $DEST_DIR"