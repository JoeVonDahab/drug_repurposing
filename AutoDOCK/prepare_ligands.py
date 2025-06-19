# This script converts SMILES strings from an input file into individual PDBQT files.

import os
import subprocess
from rdkit import Chem
from rdkit.Chem import AllChem

def prepare_ligands_from_smiles(smiles_file_path, output_pdbqt_dir):
    """
    Converts SMILES from an input file to individual PDBQT files.

    Args:
        smiles_file_path (str): Path to the input SMILES file.
                                
        output_pdbqt_dir (str): Path to the directory where PDBQT files will be saved.
    """
    if not os.path.exists(output_pdbqt_dir):
        os.makedirs(output_pdbqt_dir)
        print(f"Created output directory: {output_pdbqt_dir}")

    # Read SMILES file
    try:
        with open(smiles_file_path, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"ERROR: Input SMILES file not found: {smiles_file_path}")
        return

    print(f"Processing {len(lines)} potential molecules from {smiles_file_path}...")

    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        parts = line.split()
        smiles = parts[0]
        if len(parts) > 1:
            name_suggestion = parts[1]
        else:
            name_suggestion = f"ligand_{i+1}"

        # Sanitize name to be a valid filename
        safe_name = "".join(c if c.isalnum() else "_" for c in name_suggestion)
        if not safe_name: # Handle cases where name becomes empty or only underscores
            safe_name = f"ligand_{i+1}"

        print(f"\nProcessing molecule {i+1}: ID '{safe_name}' (SMILES: {smiles})")

        # Create RDKit molecule object
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            print(f"  ERROR: Could not parse SMILES: {smiles}. Skipping.")
            continue

        # Add hydrogens
        mol_h = Chem.AddHs(mol)

        # Embed 3D coordinates
        # Using ETKDGv3 for better conformer generation
        params = AllChem.ETKDGv3()
        params.randomSeed = 0xf00d # for reproducibility if needed
        embed_status = AllChem.EmbedMolecule(mol_h, params)

        if embed_status == -1: 
            continue
            print(f"  WARNING: Initial 3D embedding failed for {safe_name}. Trying with random coordinates.")
            params_random = AllChem.EmbedParameters()
            params_random.useRandomCoords = True
            embed_status = AllChem.EmbedMolecule(mol_h, params_random)
            if embed_status == -1:
                print(f"  ERROR: Could not generate 3D coordinates for {safe_name} even with random coords. Skipping.")
                continue

        # Optimize geometry (optional, but recommended)
        try:
            AllChem.UFFOptimizeMolecule(mol_h)
            print("  3D coordinates generated and optimized.")
        except Exception as e:
            # Sometimes optimization can fail for very strained molecules from random coords
            print(f"  WARNING: Geometry optimization failed for {safe_name}: {e}. Using unoptimized conformer.")

        # --- Convert to PDBQT using Open Babel ---
        temp_sdf_path = os.path.join(output_pdbqt_dir, f"{safe_name}_temp.sdf")
        output_pdbqt_path = os.path.join(output_pdbqt_dir, f"{safe_name}.pdbqt")

        try:
            # Write RDKit molecule to an SDF file
            writer = Chem.SDWriter(temp_sdf_path)
            writer.write(mol_h)
            writer.close()
            # print(f"  Temporary SDF file created: {temp_sdf_path}") # Optional: for debugging

            # Construct Open Babel command
            obabel_cmd = [
                'obabel', temp_sdf_path,
                '-opdbqt',
                '-O', output_pdbqt_path,
                '-h',  # Add hydrogens (Open Babel's perception)
                '--partialcharge', 'gasteiger' # Assign Gasteiger partial charges
            ]

            # print(f"  Running Open Babel: {' '.join(obabel_cmd)}") # Optional: for debugging
            result = subprocess.run(obabel_cmd, check=True, capture_output=True, text=True)
            if os.path.exists(output_pdbqt_path):
                 print(f"  Successfully created PDBQT: {output_pdbqt_path}")
            else:
                print(f"  ERROR: Open Babel command ran, but PDBQT file not found: {output_pdbqt_path}")
                print(f"  Open Babel stdout: {result.stdout}")
                print(f"  Open Babel stderr: {result.stderr}")


        except subprocess.CalledProcessError as e:
            print(f"  ERROR: Open Babel conversion failed for {safe_name}.")
            print(f"  Command: {' '.join(e.cmd)}")
            print(f"  Stderr: {e.stderr}")
            print(f"  Stdout: {e.stdout}")
        except Exception as e:
            print(f"  ERROR: An unexpected error occurred during PDBQT conversion for {safe_name}: {e}")
        finally:
            # Clean up temporary SDF file
            if os.path.exists(temp_sdf_path):
                os.remove(temp_sdf_path)

    print(f"\nLigand preparation finished. PDBQT files are in {output_pdbqt_dir}")

# --- How to use the function ---
if __name__ == "__main__":
    # ======================================================================
    # IMPORTANT: Customize these paths before running!
    # ======================================================================

    # 1. Set the path to YOUR input SMILES file
    #    Examples: "actives.smi"
    input_smiles_file = "undocked_smiles.smi"  # <--- CHANGE THIS to process a different SMILES file

    # 2. Set the name for the directory where PDBQT files will be saved
    #    This directory will be created if it doesn't exist.
    pdbqt_output_directory = "ligands_pdbqt_part1" # <--- you can change this to any directory name you prefer, but its better to keep it as it is 
    # ======================================================================

    print(f"Starting ligand preparation...")
    print(f"Input SMILES file: {os.path.abspath(input_smiles_file)}")
    print(f"Output PDBQT directory: {os.path.abspath(pdbqt_output_directory)}")

    if not os.path.exists(input_smiles_file):
        print(f"\nError: Input SMILES file not found at '{os.path.abspath(input_smiles_file)}'")
        print("Please make sure the file exists in your current directory or provide the full path.")
    else:
        prepare_ligands_from_smiles(input_smiles_file, pdbqt_output_directory)