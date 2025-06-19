import subprocess
from pathlib import Path

# === CONFIGURATION ===
INPUT_SDF_DIR = Path("in_pocket_sdfs")  # Folder containing in-pocket SDFs
OUTPUT_PDBQT_DIR = Path("ligands_pdbqt_diffdock")  # Destination for converted PDBQT files
OBABEL_EXEC = "obabel"  # Assumes Open Babel is installed and in PATH

# Create output folder
OUTPUT_PDBQT_DIR.mkdir(exist_ok=True)

# Find all SDF files
sdf_files = list(INPUT_SDF_DIR.glob("*.sdf"))

print(f"Found {len(sdf_files)} SDF files to convert.")

# Convert each SDF to PDBQT
for sdf_file in sdf_files:
    base_name_with_rank = sdf_file.stem  # e.g., "001_DrugX"

    # --- ADDED THIS LOGIC TO SPLIT THE NAME ---
    # Split on the first underscore '_' and take the second part (the original name)
    name_parts = base_name_with_rank.split('_', 1)
    base_name = name_parts[1] if len(name_parts) > 1 else base_name_with_rank
    
    pdbqt_file = OUTPUT_PDBQT_DIR / f"{base_name}.pdbqt"
    
    cmd = [
        OBABEL_EXEC,
        str(sdf_file),
        "-O", str(pdbqt_file),
        # You can add other obabel flags here if needed, e.g., to add hydrogens:
        # "-h", 
        "--partialcharge", "gasteiger"
    ]
    print(f"Converting {sdf_file.name} -> {pdbqt_file.name}")
    subprocess.run(cmd, check=True)

print(f"✅ All SDFs converted. PDBQT files saved in: {OUTPUT_PDBQT_DIR}")